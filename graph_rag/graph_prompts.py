FINAL_PROMPT = """Objective:
Reply to a question in order to generate a perfect Cypher query to retrieve dish information from a graph database representing an alien galaxy’s restaurant network. The question will be in italian language.

Context:
- The database models an alien galaxy.
- Restaurants are situated on planets, and each planet’s interplanetary distance (in light years) is recorded as the "distanza" property on the "HA_DISTANZA" relationship.
- Each restaurant offers various dishes.
- Each dish may include multiple ingredients and can be cooked using many techniques
- Each technique requires specific licenses (RICHIEDE_LICENZA relationship).
- Each restaurant has a Chef that may hold one or more licenses. The license’s grade (score) is stored as the property "grado" on the "HA_LICENZA" relationship between Chef and Licenza.
- Note: Sirius Cosmo is mentioned solely as the rule-set creator and is not involved as a chef.

Key Relationships:
- **HA_DISTANZA**: stores the "distanza" (distance in light years between planets).
- **HA_LICENZA**: contains the license grade ("grado"), and involves the nodes Chef and Licenza.
- **RICHIEDE_LICENZA**: also holds a "grado" property, but involves the nodes Ristorante and Licenza

Rules:
- Use only existing relationship and properties.
- Do not introduce any additional relationships or attributes.
- Your query should always aim to return one or more dishes (Piatto) based on the given filters.
- The final output must be the Cypher query only.

The Database Schema is the following and you must use these relations and properties:
{schema}

Example:
Trova i piatti che :
- hanno almeno 2 ingredienti tra 'RAVIOLI AL VAPOREON', 'SPAGHI DEL SOLE' e 'NETTARE DI SIRENA'
- non contengono 'PANE DI LUCE'
- considera che sinonimi di SPAGHI DE SOLE sono SPAGHI SOLEGGIATI

A valid query would be:
```cypher
MATCH (p:Piatto)-[:CONTIENE]->(i:Ingrediente)
WHERE i.nome IN ['RAVIOLI AL VAPOREON', 'SPAGHI DEL SOLE', 'SPAGHI SOLEGGIATI', 'NETTARE DI SIRENA']
WITH p, COLLECT(i) AS ingredienti
WHERE SIZE(ingredienti) >= 2
AND NOT EXISTS {{
  MATCH (p)-[:CONTIENE]->(i2:Ingrediente)
  WHERE i2.nome = 'PANE DI LUCE'
}}
RETURN DISTINCT p.nome AS piatto

Now reply to this question, but please pay attention to the syntax of the generated cypher query.
{question}
"""

SIMPLE_PROMPT = """
Objective:
Generate a Cypher query to retrieve dish information from a graph database representing a network of restaurants in an alien galaxy. The question will be in Italian.

Context:
Restaurants (Ristorante) are located on planets (Pianeta).
The distance between planets is measured in light years and is stored as the "distanza" property in the HA_DISTANZA relationship.
Each restaurant offers various dishes (Piatto).
Dishes can contain multiple ingredients (Ingrediente).
Dishes can be cooked using different techniques (Tecnica).
Techniques may require specific licenses (RICHIEDE_LICENZA relationship).
Each restaurant has a Chef, who can hold one or more licenses (Licenza) with a grade (stored as the "grado" property in the HA_LICENZA relationship).
Sirius Cosmo is only the creator of the rules and is not a chef.

General Rules:
Use only the provided nodes, relationship types and properties from the schema.
The query must always return one or more dishes (Piatto) based on the given filters.
The output must be only the Cypher query, with no additional explanations.

Cypher Rules:
- Always use single curly braces to enclose subqueries (do not use '{{' or '}}').
- When using subqueries (e.g. in an EXISTS clause), variables declared inside the subquery are local and must not be referenced outside of it. Always use distinct variable names for each subquery, and perform any aggregations (e.g., COUNT) in a separate MATCH after the subqueries.


Database Schema:
{schema}

Example:
Question:
Trova i piatti che:  
- Hanno almeno 2 ingredienti tra 'FARINA DI NETTUNO', 'FRUTTI DEL DIAVOLO' e 'CIOCCORANE'.  

**Output:**  
```cypher
MATCH (p:Piatto)-[:CONTIENE]->(i:Ingrediente)
WHERE i.nome IN ['FARINA DI NETTUNO', 'FRUTTI DEL DIAVOLO', 'CIOCCORANE']
WITH p, COLLECT(i) AS ingredienti
WHERE SIZE(ingredienti) >= 2
RETURN DISTINCT p.nome AS piatto

Now reply to this question, but please pay attention to the syntax of the generated cypher query.
After generating the cypher query, check that the query respects the Cypher Rules I provided. If it doesn't meet them, modify the query appropriately
{question}
"""

COMPLEX_PROMPT = """
Objective:
Generate a Cypher query to retrieve dish information from a graph database representing a network of restaurants in an alien galaxy. The question will be in Italian.

Context:
Restaurants (Ristorante) are located on planets (Pianeta).
The distance between planets is measured in light years and is stored as the "distanza" property in the HA_DISTANZA relationship.
Each restaurant offers various dishes (Piatto).
Dishes can contain multiple ingredients (Ingrediente).
Dishes can be cooked using different techniques (Tecnica).
Techniques may require specific licenses (RICHIEDE_LICENZA relationship).
Each restaurant has a Chef, who can hold one or more licenses (Licenza) with a grade (stored as the "grado" property in the HA_LICENZA relationship).
Sirius Cosmo is only the creator of the rules and is not a chef.

General Rules:
Use only the provided nodes, relationship types and properties from the schema.
The query must always return one or more dishes (Piatto) based on the given filters.
The output must be only the Cypher query, with no additional explanations.

Cypher Rules:
- Always use single curly braces to enclose subqueries (do not use '{{' or '}}').
- When using subqueries (e.g. in an EXISTS clause), variables declared inside the subquery are local and must not be referenced outside of it. Always use distinct variable names for each subquery, and perform any aggregations (e.g., COUNT) in a separate MATCH after the subqueries.


Database Schema:
{schema}

Example:
Question:
Trova i piatti che:  
- Hanno almeno 2 ingredienti tra brodo di pollo e cioccomostri.  
- Considera che sinonimi di 'BRODO DI POLLO' sono 'POLLI IN BRODO'
- Considera che sinonimi di 'CIOCCOMOSTRI' sono 'CIOCCOMOSTRI'
- Usa la proprietà 'nome' del nodo Ingrediente nella query
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- Ogni volta che confronti stringhe nelle query, usa sempre toUpper() per i valori confrontati. Ad esempio: WHERE z.nome = toUpper('TEST'). Non usare toUpper() se stai confrontando numeri.
- REGOLA IMPORTANTE: ogni query deve dare come output sempre e solo i nomi dei piatti.
- REGOLA IMPORTANTE2: cerca sempre di capire se un'entità dev'essere presente insieme ad altre entità in contemporanea oppure no.

**Output:**  
```cypher
MATCH (p:Piatto)-[:CONTIENE]->(i:Ingrediente)
WHERE i.nome IN [toUpper('BRODO DI POLLO'), toUpper('POLLI IN BRODO')]
WITH p, COUNT(i) AS count_ing
WHERE count_ing >= 1
MATCH (p)-[:CONTIENE]->(i2:Ingrediente)
WHERE i2.nome IN [toUpper('CIOCCOMOSTRI')]
RETURN DISTINCT p.nome AS piatto

Now reply to this question, but please pay attention to the syntax of the generated cypher query.
After generating the cypher query, check that the query respects the Cypher Rules I provided. If it doesn't meet them, modify the query appropriately
{question}
"""

generated_query  = """
Objective:
Correct a Cypher query to retrieve dish information from a graph database representing a network of restaurants in an alien galaxy.

Context:
Restaurants (Ristorante) are located on planets (Pianeta).
The distance between planets is measured in light years and is stored as the "distanza" property in the HA_DISTANZA relationship.
Each restaurant offers various dishes (Piatto).
Dishes can contain multiple ingredients (Ingrediente).
Dishes can be cooked using different techniques (Tecnica).
Techniques may require specific licenses (RICHIEDE_LICENZA relationship).
Each restaurant has a Chef, who can hold one or more licenses (Licenza) with a grade (stored as the "grado" property in the HA_LICENZA relationship).
Sirius Cosmo is only the creator of the rules and is not a chef.

General Rules:
Use only the provided nodes, relationship types and properties from the schema.
The query must always return one or more dishes (Piatto) based on the given filters.
The output must be only the Cypher query, with no additional explanations.

Cypher Rules:
- Always use single curly braces to enclose subqueries (do not use '{{' or '}}').
- When using subqueries (e.g. in an EXISTS clause), variables declared inside the subquery are local and must not be referenced outside of it. Always use distinct variable names for each subquery, and perform any aggregations (e.g., COUNT) in a separate MATCH after the subqueries.

Database Schema:
{schema}

This is the cypher query you need to fix, as there appears to be a syntax error. Try to understand the objective of this query, and then produce a correct one, respecting the scheme I have provided.
{query}
"""

generated_query_with_example  = """
Objective:
Correct a Cypher query to retrieve dish information from a graph database representing a network of restaurants in an alien galaxy.

This is the database Schema:
{schema}

General Rules:
Use only the provided nodes, relationship types and properties from the schema.
The query must always return one or more dishes (Piatto) based on the given filters.
The output must be only the Cypher query, with no additional explanations.

Cypher Rules:
- Always use single curly braces to enclose subqueries (do not use '{{' or '}}').
- When using subqueries (e.g. in an EXISTS clause), variables declared inside the subquery are local and must not be referenced outside of it. Always use distinct variable names for each subquery, and perform any aggregations (e.g., COUNT) in a separate MATCH after the subqueries.

This is the question for which an incorrect cypher query was produced:
{original_question}

This is the cypher query you need to fix, as there appears to be a syntax error. Try to understand the objective of this query, and then produce a correct one, respecting the scheme I have provided.
{query}
"""

VERY_SIMPLE_PROMPT = """
Objective:
Your objective is generate a Cypher query to a graph RAG, in order to retrieve dish names.

Context:
The graph rag models an invented alien galaxy with some entities.
The schema is star-shaped, with the 'Piatto' entity in the center
Restaurants are located on planets.
The distance between planets is measured in light years and is stored as the "distanza" property.
Each dish is offered by a restaurant.
Dishes can contain multiple ingredients.
Dishes can be cooked using different techniques.
Techniques may require specific licenses (RICHIEDE_LICENZA relationship).
Each restaurant has a Chef, who can hold one or more licenses (Licenza) with a grade, stored as the "grado" property.
Sirius Cosmo is only the creator of the alien galaxy and is not a chef.

Cypher generation rules:
Use only the provided nodes, relationship types and properties from the schema.
The query must always return one or more name dishes based on the given filters.
The output must be only the Cypher query, with no additional explanations.

Schema of the graph rag you need to use:
{schema}

Example
Trova i piatti che:
- hanno almeno 2 ingredienti tra 'POLVERE DI CROCONITE', 'SPAGHI DEL SOLE' e 'CARNE DI MUCCA'
- non contengono 'PANE DI LUCE'
- Usa la proprietà 'nome' del nodo Ingrediente nella query
- REGOLA IMPORTANTE: ogni query deve dare come output sempre e solo i nomi dei piatti.
- REGOLA IMPORTANTE2: cerca sempre di capire se un'entità dev'essere presente insieme ad altre entità in contemporanea oppure no.

Possible output:
MATCH (p:Piatto)-[:CONTIENE]->(i:Ingrediente)
WHERE i.nome IN ['POLVERE DI CROCONITE', 'SPAGHI DEL SOLE', 'CARNE DI MUCCA']
WITH p, COLLECT(i) AS ingredienti_filtrati
WHERE SIZE(ingredienti_filtrati) >= 2
AND NOT EXISTS {{
  MATCH (p)-[:CONTIENE]->(i2:Ingrediente)
  WHERE i2.nome = 'PANE DI LUCE'
}}
RETURN DISTINCT p.nome AS piatto

Now reply to this question, but please pay attention to the syntax of the generated cypher query.
The future of this alien galaxy depends on how correct your answers are.
{question}
"""

# Esempio pianeta
"""
Quali sono i piatti che hanno una distanza da MOS IESLEY <= 30?

Answer:
MATCH (p:Piatto)-[:OFFERTO_DA]->(r:Ristorante)
MATCH (r)-[:SITUATO_SU]->(pl:Pianeta)
MATCH (pl)-[d:HA_DISTANZA]->(pl2:Pianeta)
WHERE pl2.nome IN ['MOS EISLEY', 'MOS EISLEYY'] AND d.distanza <= 30
RETURN DISTINCT p.nome AS piatto
"""

# Suggerimenti per cypher corretta
"""
- IMPORTANT: Always use single curly braces to enclose subqueries (do not use '{{' or '}}').
- IMPORTANT: When using subqueries (e.g. in an EXISTS clause), variables declared inside the subquery are local and must not be referenced outside of it. Always use distinct variable names for each subquery, and perform any aggregations (e.g., COUNT) in a separate MATCH after the subqueries.
"""

def get_retrivial_prompt():
    PROMPT = VERY_SIMPLE_PROMPT
    return PROMPT

def get_cypher_prompt():
    PROMPT = generated_query
    return PROMPT

def get_cypher_prompt_with_example():
    PROMPT = generated_query_with_example
    return PROMPT

def clean_cypher_query(query: str) -> str:
    return query.lstrip("cypher\n").strip()