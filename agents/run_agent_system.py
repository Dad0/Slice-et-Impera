def find_dishes(query):
    import time
    from pydantic import BaseModel, Field
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from typing import TypedDict
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from langgraph.graph import END, StateGraph, START
    from typing import Dict, List, Any, Annotated
    import operator
    import json
    from graph_rag import graph_retrivial as gr
    from neo4j import GraphDatabase
    import logging
    from graph_rag import cypher_correction as cc
    from agents import agents_functions as af
    from agents import agents_prompt as ap
    from dotenv import load_dotenv
    import os
    import re

    load_dotenv()

    URI = os.getenv("URI")
    USERNAME = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Esempio di utilizzo
    DISH_DICT_PATH = os.getenv("DISH_DICT")
    dish_dict = af.load_dish_dict(DISH_DICT_PATH)

    DOMANDE_PATH = os.getenv("DOMANDE_PATH")

    db_driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD), database="pizzadb")


    class AgentState(TypedDict):
        messages: list[BaseMessage]
        cleaned_question: str

        dishes_dict: Dict[str, list]
        entity_dict: Dict[str, Dict[str, Any]]
        string_value: Annotated[str, operator.add]
        entity: Annotated[str, operator.add]

        dishes: Annotated[List[List[str]], af.merge_list_of_lists]
        query: Annotated[List[List[str]], af.merge_list_of_lists]

        all_queries: List[List[str]]
        all_entities: List[List[str]]
        # Aggiunte...
        # cleaned_question: Annotated[str, operator.add]


    class QuestionRewriter(BaseModel):
        reply: str = Field(
            description="Rispondi creando l'output in base alla domanda dell'utente"
        )


    def rewrites_questions(state: AgentState):
        QUESTION_REWRITER_PROMPT = ap.get_question_rewriter_prompt()

        question = state["messages"][-1].content

        query_cleaner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QUESTION_REWRITER_PROMPT),
                ("human", "User question: {question}"),
            ]
        )

        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(QuestionRewriter)
        question_rewriter_pipeline = query_cleaner_prompt | structured_llm
        result = question_rewriter_pipeline.invoke({"question": question})

        print(result.reply)

        state["cleaned_question"] = result.reply

        return state


    class EntityClassifier(BaseModel):
        reply: str = Field(
            description="Rispondi creando il json in base alla domanda dell'utente. Non rispondere mai in maniera diversa da quel json."
        )


    def classifies_entities(state: AgentState):
        # Prompt per classificare entità e creare il json
        ENTITY_CLASSIFIER_PROMPT = ap.get_entity_classifier_prompt()

        question = state["cleaned_question"]

        entity_classifier_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ENTITY_CLASSIFIER_PROMPT),
                ("human", "User question: {question}"),
            ]
        )

        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(EntityClassifier)
        entity_classifier_pipeline = entity_classifier_prompt | structured_llm
        result = entity_classifier_pipeline.invoke({"question": question})

        # Salva solo le entità utili, e crea gli agenti solo per quelle entità
        result_dict = af.extract_entities(json.loads(result.reply))

        print(result_dict)

        return {"entity_names": result_dict.keys(), "entity_dict": result_dict}


    def generate_agents(state: AgentState):
        entity = state["entity_names"]
        dicts = state["entity_dict"]

        dicts = list(dicts.values())

        sends = af.create_sends(entity, dicts)

        return sends


    def EntityAgent(state: AgentState) -> Any:
        import re
        single_entity_name = state["single_entity_name"]

        print(f"\nQuesto è l'agente '{single_entity_name}'")

        single_entity_dict = af.get_single_entity_dict(state)
        single_entity_name = state.get("single_entity_name")

        print(f"I valori sono i seguenti: {single_entity_dict}")

        nomi = single_entity_dict["nomi"]

        # DA VERIFICARE
        if nomi == "":
            return {"entity": "fake_entity" + "|", "dishes": [], "query": []}

        # print(f"Vecchia descrizione = {single_entity_dict['descrizione']}")
        single_entity_dict["descrizione"] = af.replace_with_upper_case_insensitive(single_entity_dict["descrizione"], nomi)
        # print(f"Nuova descrizione = {single_entity_dict['descrizione']}")

        nomi_upper = [x.upper() for x in nomi]
        max_length = max(len(s) for s in nomi_upper)

        single_entity_dict, risultati = af.process_entity(single_entity_name, single_entity_dict, db_driver, nomi_upper,
                                                          max_length)

        query_for_entity = af.build_query_for_entity(single_entity_name, single_entity_dict, risultati, max_length,
                                                     get_validate_cypher)

        print(f"\n{query_for_entity}")

        # Log setup
        logger, logger_error = af.setup_logging_for_entity(single_entity_name)

        # Esecuzione delle query
        # generated_cypher, dishes = af.process_query(single_entity_name, query_for_entity, validate_cypher, gr, cc, logger_error)
        generated_cypher, dishes = af.process_query(single_entity_name, query_for_entity, db_driver, validate_cypher, gr,
                                                    cc, logger_error)

        # Log dei piatti trovati
        logger.info(f"\nCiao! Questo è l'agente '{single_entity_name}'\n. Ho trovato i seguenti piatti che corrispondono alla tua richiesta :) \n")

        logger.info(f"\n{i}\n{dishes}\n")

        # print(f"Cypher che sto passando a Combiner: {generated_cypher}")

        return {"entity": single_entity_name + "|", "dishes": [dishes], "query": [[generated_cypher]]}


    def Combiner(state: Dict[str, Any]) -> Dict[str, Any]:
        # print(state["entity"])
        print(f"\nTotale piatti trovati:{state['dishes']}")
        # print(f"ECCO TUTTE LE CYPHER RICEVUTE {state['query']}")
        all_entities = (state["entity"].split("|"))[:-1]
        state["all_queries"] = state['query']

        def remove_list_by_index(lst_of_lists, index):
            if 0 <= index < len(lst_of_lists):
                del lst_of_lists[index]
            return lst_of_lists

        cont = -1
        flag = False
        for z, ent in enumerate(all_entities):
            if ent == "fake_entity":
                flag = True
                cont = z

        if flag:
            all_entities = [s for s in all_entities if s != "fake_entity"]
            state["dishes"] = remove_list_by_index(state["dishes"], cont)

        state["all_entities"] = all_entities
        return state


    def evaluates_results(state: AgentState) -> any:
        print("\nQuesto è l'agente SetEvaluator")

        all_entities = state["all_entities"]
        result = af.evaluate_entities_query(get_index(), state, all_entities, ap, QuestionRewriter)

        logger = af.setup_logger("Results")

        i = get_index()
        if len(result) == 0:
            logger.info(f"\n{i}\n" + "Problema con un'entità\n")
            logger.info(f"\n{i}\n" + "NON HO SAPUTO RISPONDERE, RISPONDO 23 SPERANDO CHE MI PORTI FORTUNA\n")
            # raise ValueError("Questo è un errore intenzionale")
            af.append_dish_indices(i, result, dish_dict, "risultati.csv", 1)

        else:
            logger.info(f"\n{i}\n" + str(result) + "\n")
            af.append_dish_indices(i, result, dish_dict, "risultati.csv")

        logger = af.setup_logger("Query")

        all_queries = state["all_queries"]
        cleaned_question = state["cleaned_question"]

        print(all_queries)
        log_message = "\n" + str(i) + " " + cleaned_question + ")\n\n"
        for z, cypher_query in enumerate(all_queries):
            log_message += "\n" + "[" + all_entities[z] + "]" + "\n\n" + cypher_query[0] + "\n\n"

        logger.info(log_message)


    workflow = StateGraph(AgentState)
    workflow.set_entry_point("Question_Rewriter")
    workflow.add_node("Question_Rewriter", rewrites_questions)
    workflow.add_node("Entity_Classifier", classifies_entities)
    workflow.add_node("EntityAgent", EntityAgent)
    workflow.add_node("Combiner", Combiner)
    workflow.add_node("SetEvaluatorAgent", evaluates_results)

    workflow.add_edge("Question_Rewriter", "Entity_Classifier")

    workflow.add_conditional_edges(
        "Entity_Classifier", generate_agents, ["EntityAgent"]
    )

    workflow.add_edge("EntityAgent", "Combiner")
    workflow.add_edge("Combiner", "SetEvaluatorAgent")
    workflow.add_edge("SetEvaluatorAgent", END)

    graph = workflow.compile()

    validate_cypher = True
    i = 0

    def get_validate_cypher():
        return True

    def get_index():
        return i

    graph.invoke(
        input={
            "messages": [HumanMessage(content=query)]
        }
    )

