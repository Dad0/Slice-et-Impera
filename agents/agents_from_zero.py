"""
Questo script contiene il sistema di agenti utilizzato per la challenge
"""
import time
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing import Dict, List, Any, Annotated
import operator
import json
from graph_rag import graph_retrivial as gr
from neo4j import GraphDatabase
from graph_rag import cypher_correction as cc
from agents import agents_functions as af
from agents import agents_prompt as ap
from dotenv import load_dotenv
import os

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
    """
    Rappresenta lo stato di un agente con le informazioni necessarie per elaborare una domanda e generare risposte.

    Attributi:
        messages (list[BaseMessage]): Lista di messaggi scambiati con l'utente.
        cleaned_question (str): La domanda dell'utente ripulita e riformulata.
        dishes_dict (Dict[str, list]): Dizionario dei piatti disponibili.
        entity_dict (Dict[str, Dict[str, Any]]): Dizionario delle entità con i relativi dettagli.
        entity (Annotated[str, operator.add]): Nome dell'entità attualmente in elaborazione.
        dishes (Annotated[List[List[str]], af.merge_list_of_lists]): Lista di liste di piatti associati alle entità.
        query (Annotated[List[List[str]], af.merge_list_of_lists]): Lista di liste di query generate per le entità.
        all_queries (List[List[str]]): Lista di tutte le query generate.
        all_entities (List[List[str]]): Lista di tutte le entità identificate.
    """

    messages: list[BaseMessage]
    cleaned_question: str

    dishes_dict: Dict[str, list]
    entity_dict: Dict[str, Dict[str, Any]]
    entity: Annotated[str, operator.add]

    dishes: Annotated[List[List[str]], af.merge_list_of_lists]
    query: Annotated[List[List[str]], af.merge_list_of_lists]

    all_queries: List[List[str]]
    all_entities: List[List[str]]

class QuestionRewriter(BaseModel):

    reply: str = Field(
        description="Rispondi creando l'output in base alla domanda dell'utente"
    )

def rewrites_questions(state: AgentState):
    """
    Riscrive la domanda dell'utente per renderla più chiara e strutturata.

    Args:
        state (AgentState): Lo stato attuale dell'agente contenente i messaggi e altre informazioni.

    Returns:
        AgentState: Lo stato aggiornato dell'agente con la domanda ripulita.
    """
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
    """
    Classifica le entità presenti nella domanda dell'utente e crea un JSON con le entità identificate.

    Args:
        state (AgentState): Lo stato attuale dell'agente contenente i messaggi e altre informazioni.

    Returns:
        dict: Un dizionario contenente i nomi delle entità e il dizionario delle entità.
    """

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

    return {"entity_names": result_dict.keys(), "entity_dict":result_dict}

def generate_agents(state: AgentState):
    """
    Genera gli agenti basati sulle entità classificate nello stato dell'agente.
    Nel particolare, Sends permette di inviare dinamicamente stati differenti a nodi specifici,
    abilitando l'esecuzione parallela di task (fase map) secondo il flusso definito nel grafo.
    Utilizzando conditional edges, Send distribuisce elementi a istanze multiple di un nodo,
    garantendo che ogni ramo riceva uno stato unico da elaborare.
    In sostanza, è presente una sorta di meccanismo di mapReduce:
    Durante la fase di map, il lavoro viene suddiviso e distribuito tra vari agenti.
    Nella fase di reduce, i risultati parziali vengono aggregati per produrre il risultato finale.
    Per la fase di reduce, viene usata l'Annotated List per combinare i risultati provenienti
    da più nodi paralleli

    Args:
        state (AgentState): Lo stato attuale dell'agente contenente i nomi delle entità e il dizionario delle entità.

    Returns:
        list: Una lista di agenti creati per le entità classificate.
    """

    entity = state["entity_names"]
    dicts = state["entity_dict"]

    dicts = list(dicts.values())

    sends = af.create_sends(entity, dicts)

    return sends

def EntityAgent(state: AgentState) -> Any:
    """
    Gestisce un singolo agente per un'entità specifica, eseguendo query e processando i risultati.

    Args:
        state (AgentState): Lo stato attuale dell'agente contenente i dettagli dell'entità.

    Returns:
        dict: Un dizionario contenente il nome dell'entità, i piatti trovati e le query generate.
    """

    single_entity_name = state["single_entity_name"]

    print(f"\nQuesto è l'agente '{single_entity_name}'")

    single_entity_dict = af.get_single_entity_dict(state)
    single_entity_name = state.get("single_entity_name")

    print(f"I valori sono i seguenti: {single_entity_dict}")

    nomi = single_entity_dict["nomi"]

    # Utile per mettersi al riparo da eventuali (rari) casi in cui il campo nome non è stato popolato
    if nomi == "":
        return {"entity": "fake_entity" + "|", "dishes": [], "query": []}

    single_entity_dict["descrizione"] = af.replace_with_upper_case_insensitive(single_entity_dict["descrizione"], nomi)

    nomi_upper = [x.upper() for x in nomi]
    max_length = max(len(s) for s in nomi_upper)

    single_entity_dict, risultati = af.process_entity(single_entity_name, single_entity_dict, db_driver, nomi_upper, max_length)

    query_for_entity = af.build_query_for_entity(single_entity_name, single_entity_dict, risultati, max_length, get_validate_cypher)

    print(f"\n{query_for_entity}")

    # Log setup
    logger, logger_error = af.setup_logging_for_entity(single_entity_name)

    # Esecuzione delle query
    generated_cypher, dishes = af.process_query(single_entity_name, query_for_entity, db_driver, validate_cypher, gr, cc, logger_error)

    # Log dei piatti trovati
    logger.info(f"\n{i}\n{dishes}\n")

    return {"entity": single_entity_name + "|", "dishes": [dishes], "query": [[generated_cypher]]}

def Combiner(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combina i risultati parziali degli agenti, rimuovendo eventuali entità fittizie e aggiornando lo stato.

    Args:
        state (Dict[str, Any]): Lo stato attuale contenente i piatti trovati, le entità e le query.

    Returns:
        Dict[str, Any]: Lo stato aggiornato con le entità e i piatti validi.
    """

    print(f"\nTotale piatti trovati:{state['dishes']}")

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
    """
    Valuta i risultati delle query eseguite dagli agenti e registra i risultati.

    Args:
        state (AgentState): Lo stato attuale dell'agente contenente le entità, le query e altre informazioni.

    Returns:
        any: I risultati valutati delle query eseguite.
    """

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

def get_validate_cypher():
    return validate_cypher

righe = af.leggi_csv(DOMANDE_PATH, 100)

read_from_file = False

if read_from_file:
    for i, query in enumerate(righe):
        i+=1
        def get_index():
            return i
        print(i)
        print(query)

        validate_cypher = True

        if i < 0:
            continue

        graph.invoke(
            input={
                "messages": [HumanMessage(content=query)]
            }
        )

        # Se va troppo fast Openai mi da errore perchè uso troppi token in troppo poco tempo :/
        time.sleep(5)

else:

    n = 54
    validate_cypher = True

    for i, query in enumerate(righe):
        i += 1
        def get_index():
            return i

        if i == n:
            print(i)
            print(query)
            query = "Che piatti posso mangiare che siano preparati che siano prodotti con sferificazione o fermentazione e che contengano baccacedro??"
            graph.invoke(
                input={
                    "messages": [HumanMessage(content=query)]
                }
            )
        else:
            pass



