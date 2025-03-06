from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts.prompt import PromptTemplate
from graph_rag import graph_prompts
import os

URI = os.getenv("URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

graph = Neo4jGraph(url=URI, username=USERNAME, password=PASSWORD, enhanced_schema=True, database="pizzadb")


def get_graph_schema(driver):
    with driver.session() as session:
        result = session.run("""USE pizzadb CALL db.schema.visualization()
            """)
        return result.single()

chatty = ChatOpenAI(
        model="gpt-4o",
        # model = "gpt-4o-mini-2024-07-18",
        temperature=0,
        max_tokens=None,
    )

# Prova a far riscrivere la mail a Chatty
def askChatty_for_cypher(query, validate_cypher=True):

    db_driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    schema = get_graph_schema(db_driver)

    chain = GraphCypherQAChain.from_llm(
        llm = chatty,
        graph = graph,
        verbose = True,
        allow_dangerous_requests = True,
        cypher_prompt = PromptTemplate(input_variables=[schema, query], template=graph_prompts.get_cypher_prompt()),
        return_direct = True,
        return_intermediate_steps = True,
        top_k = 300,
        validate_cypher = validate_cypher
    )

    answer = chain.invoke({
        'schema': schema,
        'query': query
    })

    return answer["result"], answer["intermediate_steps"]

# Fai interrogare il db a Chatty e dagli un esempio -> TO DO
def askChatty_for_cypher_with_example(original_question, query, validate_cypher=True):

    def get_graph_schema(driver):
        with driver.session() as session:
            result = session.run("""USE pizzadb CALL db.schema.visualization()
                """)
            return result.single()

    db_driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    schema = get_graph_schema(db_driver)

    chain = GraphCypherQAChain.from_llm(
        llm=chatty,
        graph=graph,
        verbose=True,
        allow_dangerous_requests=True,
        cypher_prompt=PromptTemplate(input_variables=[schema, original_question, query], template=graph_prompts.get_cypher_prompt_with_example()),
        return_direct=True,
        return_intermediate_steps=True,
        top_k=300,
        validate_cypher=validate_cypher
    )

    answer = chain.invoke({
        'schema': schema,
        'original_question': original_question,
        'query': query
    })

    return answer["result"], answer["intermediate_steps"]
