REMOVE_ALL =\
"""
USE pizzadb
MATCH (n)  
DETACH DELETE n
"""

READ_ALL_INGREDIENTS =\
"""
USE pizzadb
MATCH (i:Ingrediente)
RETURN i
"""

CREATE_RISTORANTE_QUERY =\
"""
USE pizzadb
CREATE (r:Ristorante {nome: $nome})
RETURN r
"""

CREATE_PIATTO_QUERY = \
"""
USE pizzadb
MERGE (p:Piatto {nome: $nome_piatto})
WITH p
MATCH (r:Ristorante {nome: $nome_ristorante})
MERGE (p)-[:OFFERTO_DA]->(r)
RETURN p
"""

CREATE_INGREDIENTE_QUERY = \
"""
USE pizzadb
MERGE (i:Ingrediente {nome: $nome_ingrediente})
WITH i
MATCH (p:Piatto {nome: $nome_piatto})
MERGE (p)-[:CONTIENE]->(i)
RETURN i
"""

CREATE_CHEF_QUERY = """
USE pizzadb
MERGE (c:Chef {nome: $nome_chef})
WITH c
MATCH (r:Ristorante {nome: $nome_ristorante})
MERGE (r)-[:HA_CHEF]->(c)
RETURN c
"""

CREATE_PLANET_QUERY =\
"""
USE pizzadb
MERGE (p:Pianeta {nome: $nome_pianeta})
WITH p
MATCH (r:Ristorante {nome: $nome_ristorante})
MERGE (r)-[:SITUATO_SU]->(p)
RETURN p
"""

CREATE_TECNICA_QUERY = \
"""
USE pizzadb
MERGE (t:Tecnica {nome: $nome_tecnica})
WITH t
MATCH (p:Piatto {nome: $nome_piatto})
MERGE (p)-[:CUCINATO_MEDIANTE]->(t)
RETURN t
"""

CREATE_LICENZA_QUERY2 = \
"""
USE pizzadb
MATCH (l:Licenza {nome: $nome_licenza})
MATCH (r:Ristorante {nome: $nome_ristorante})
MERGE (r)-[rel:HA_LICENZA]->(l)
SET rel.grado = $grado
RETURN l
"""
CREATE_LICENZA_QUERY = \
"""
USE pizzadb
MATCH (l:Licenza {nome: $nome_licenza})
MATCH (c:Chef {nome: $nome_ristorante})
MERGE (c)-[rel:HA_LICENZA]->(l)
SET rel.grado = $grado
RETURN l
"""

CREATE_ELENCO_LICENZE_QUERY = \
"""
USE pizzadb
MERGE (l:Licenza {nome: $nome_licenza, sigla: $sigla_licenza})
SET l.gradi = $gradi
RETURN l
"""

def remove_all():
    return REMOVE_ALL

def read_all_ingredients():
    return READ_ALL_INGREDIENTS

def create_restaurant():
    return CREATE_RISTORANTE_QUERY

def create_dish():
    return CREATE_PIATTO_QUERY

def create_ing():
    return CREATE_INGREDIENTE_QUERY

def create_chef():
    return CREATE_CHEF_QUERY

def create_planet():
    return CREATE_PLANET_QUERY

def create_tec():
    return CREATE_TECNICA_QUERY

def create_lic():
    return CREATE_ELENCO_LICENZE_QUERY

def create_lic_rest():
    return CREATE_LICENZA_QUERY

def create_planet():
    return CREATE_PLANET_QUERY
