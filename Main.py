"""
Questo script si occupa esclusivamente di
- estrazione dati
- preprocessing
- costruzione della Graph RAG

La Graph RAG creata tramite questo script è stata salvata nella cartella "DUMP DB"

L'idea è che ci debba essere una cartella "original data" con all'interno l'intero contenuto di
HackAPizza Dataset, e una cartella "processed data" che viene invece man mano popolata dai file
processati

Slice et Impera\original data\ -> le 4 cartelle di HackAPizza dataset + il file delle domande
Slice et Impera\processed data\ -> Cartella vuota che si popolerà man mano

ps: per chiarezza, ho spostato i processed data "vecchi" in un backup, così da lasciare la
cartella vuota. In quel mare di file dai nomi ambigui, quello definitivo utilizzato per
costruire la RAG era "menu_update_final_updated_chef_updated.json"
"""

import utils_functions.preprocessing_functions as pf
import utils_functions.preprocessing_prompts as pp
import json
from dotenv import load_dotenv
import os
import importlib

# Caricamento variabili
load_dotenv()

# path docx codice galattico (file all'interno di original data\Codice Galattico\)
PATH_CODICE_GALATTICO_DOCX = os.getenv("PATH_CODICE_GALATTICO_DOCX")
# path pdf manuale cucina (file all'interno di original data\Misc\)
PATH_MANUALE_CUCINA_PDF = os.getenv("PATH_MANUALE_CUCINA_PDF")
# path folder con i vari menu originali in pdf (all'interno di \original data\Menu)
PATH_MENU_DIR = os.getenv("PATH_MENU_DIR")

# path distanze e dish mapping (file all'interno di original data\Misc\)
PATH_DISTANZE = os.getenv("PATH_DISTANZE")
DISH_DICT = os.getenv("DISH_DICT")

PATH_MENU_DIR_PROCESSED = pf.transform_path2(PATH_MENU_DIR)

# ================================================================================
# CODICE GALATTICO
# ================================================================================

"""
In questa sezione viene estratto il capitolo relativo alle tecniche dal codice galattico, 
e vengono estratte le tecniche e le licenze richieste. Il json risultante viene salvato
all'interno della variabile PATH_TECNICHE.
"""

# Converti in markdown (non standardizzato) il codice galattico presente in "original data" e salvalo in "processed data"
codice_galattico_md = pf.docx_to_markdown(PATH_CODICE_GALATTICO_DOCX, pf.transform_path(PATH_CODICE_GALATTICO_DOCX, "md"))
# Estrai capitolo con tutte le tecniche e salvalo in "capitolo_tecniche"
capitolo_tecniche = pf.extract_section(codice_galattico_md, 4, 5)
# Estrai json con tecniche e licenze richieste, tramite GPT 4o-mini (nb: non sempre alla prima run prende tutte le tecniche)
PATH_TECNICHE_JSON = pf.extract_info(pf.transform_path(PATH_CODICE_GALATTICO_DOCX, "json"), pp.generate_technique_extraction_prompt(capitolo_tecniche), "_tecniche", "gpt-4o-mini-2024-07-18")

# ================================================================================
# MANUALE CUCINA
# ================================================================================

"""
In questa sezione vengono estratti i capitoli relativi alle licenze e agli ordini del
manuale di cucina, e i conseguenti elenchi di licenze e ordini. 
I json risultanti vengono salvati all'interno delle variabili PATH_ELENCO_LICENZE_JSON e
PATH_ELENCO_ORDINI_JSON.
"""

# Converti in markdown (non standardizzato) il manuale cucina presente in "original data" e salvalo in "processed data"
md_text2 = pf.pdf_to_markdown(PATH_MANUALE_CUCINA_PDF, pf.transform_path(PATH_MANUALE_CUCINA_PDF, "md"))

# Estrai capitolo con tutte le licenze e salvalo in "capitolo_elenco_licenze"
capitolo_elenco_licenze = pf.extract_section(md_text2, "Capitolo 1", "Capitolo 2")
# Estrai json con elenco licenze, tramite GPT 4o-mini
PATH_ELENCO_LICENZE_JSON = pf.extract_info(pf.transform_path(PATH_MANUALE_CUCINA_PDF, "json"), pp.generate_licenses_extraction_prompt(capitolo_elenco_licenze), "_elenco_licenze")

# Estrai capitolo con elenco ordini e salvalo in "capitolo_elenco_ordini"
capitolo_elenco_ordini = pf.extract_section(md_text2, "Capitolo 2", "Capitolo 3")
# Estrai json con elenco ordini, tramite GPT 4o-mini
PATH_ELENCO_ORDINI_JSON = pf.extract_info(pf.transform_path(PATH_MANUALE_CUCINA_PDF, "json"), pp.generate_orders_extraction_prompt(capitolo_elenco_ordini), "_elenco_ordini")

# ================================================================================
# MENU
# ================================================================================

"""
In questa sezione vengono estratti ingredienti e tecniche.
Successivamente vengono estratti anche nomi dei ristoranti, chef, pianeti e licenze.
Infine viene creato un unico json chiamato all_extracted_info_v1 contenente tutte le informazioni estratte.
"""

# Converti i vari pdf in html
pf.convert_pdfs_to_html_with_size(PATH_MENU_DIR, PATH_MENU_DIR_PROCESSED)

# Crea cartella ristoranti con all'interno un txt per ogni piatto, partendo dagli html
pf.process_all_html_files(PATH_MENU_DIR_PROCESSED, PATH_MENU_DIR_PROCESSED)

# Trova i ristoranti con i menu non discorsivi
lista_ristoranti_con_menu_discorsivi = pf.find_html_files_with_large_ingredient(PATH_MENU_DIR_PROCESSED)

# Sposta le cartelle dei ristoranti nelle rispettive cartelle "Menu discorsivi" e "Menu non discorsivi"
PATH_MENU_DISCORSIVI, PATH_MENU_LISTA = pf.organize_folders(os.path.join(PATH_MENU_DIR_PROCESSED, "Ristoranti"), lista_ristoranti_con_menu_discorsivi)

# Crea file con piatti e ingredienti per i menu discorsivi e non, e unisci i json in modo da averne uno per ogni ristorante
pf.process_files_in_folders(pf.transform_path2(PATH_MENU_DISCORSIVI), pp.generate_ingredients_from_menu_extraction_prompt, "_piatti_e_ingredienti", pf.get_all_text, "gpt-4o")
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_DISCORSIVI), "_piatti_e_ingredienti")

pf.process_files_in_folders(pf.transform_path2(PATH_MENU_LISTA), pp.generate_ingredients_from_menu_extraction_prompt2, "_piatti_e_ingredienti", pf.get_ingredients, "gpt-4o-mini-2024-07-18")
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_LISTA), "_piatti_e_ingredienti")

# Sposta i file uniti nella cartella menu
pf.move_files_by_suffix(PATH_MENU_DIR_PROCESSED, PATH_MENU_DIR_PROCESSED, "_piatti_e_ingredienti_totali_per_ristorante")

# Cambia i nomi dei piatti con quelli più simili presenti nel dizionario
pf.find_most_similar_and_replace_wrapper(PATH_MENU_DIR_PROCESSED, DISH_DICT, "_piatti_e_ingredienti_totali_per_ristorante")


# Stesso identico procedimento con piatti e tecniche
pf.process_files_in_folders(pf.transform_path2(PATH_MENU_DISCORSIVI), pp.generate_techniques_from_menu_extraction_prompt, "_piatti_e_tecniche", pf.get_all_text, "gpt-4o")
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_DISCORSIVI),"_piatti_e_tecniche")

pf.process_files_in_folders(pf.transform_path2(PATH_MENU_LISTA), pp.generate_ingredients_from_menu_extraction_prompt3, "_piatti_e_tecniche", pf.get_techniques, "gpt-4o-mini-2024-07-18")
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_LISTA),"_piatti_e_tecniche")

# Sposta i file uniti nella cartella menu
pf.move_files_by_suffix(PATH_MENU_DIR_PROCESSED, PATH_MENU_DIR_PROCESSED, "_piatti_e_tecniche_totali_per_ristorante")

# Cambia i nomi dei piatti con quelli più simili presenti nel dizionario
pf.find_most_similar_and_replace_wrapper(PATH_MENU_DIR_PROCESSED, DISH_DICT, "_piatti_e_tecniche_totali_per_ristorante")


# Converti menu in .txt che hanno ancora la descrizione del ristorante, per estrarre nome ristorante, chef, pianeta e licenze
pf.convert_pdfs_to_md(PATH_MENU_DIR, PATH_MENU_DIR_PROCESSED)
# Estrai ristorante, pianeta, chef e licenze
pf.extract_menu(PATH_MENU_DIR_PROCESSED, pp.generate_licenses_from_menu_extraction_prompt, "_pianeti_chef_e_licenze")

# Fai un merge dei vari json ottenuti dai menu per avere un unico json
risultato = pf.merge_all_restaurants(PATH_MENU_DIR_PROCESSED)
ALL_EXTRACTED_INFO_V1 = os.path.join(PATH_MENU_DIR_PROCESSED, "all_extracted_info_v1.json")
with open(ALL_EXTRACTED_INFO_V1, 'w', encoding='utf-8') as f:
    json.dump(risultato, f, indent=4, ensure_ascii=False)

# Se una emoji è a fianco al nome di un piatto, mettila nella sezione "ordini"
pf.process_emoji_in_menu(ALL_EXTRACTED_INFO_V1)

# Se una tecnica è finita tra gli ingredienti, mettila tra le tecniche (se non c'è già)
ALL_EXTRACTED_INFO_V2 = pf.correct_techniques_in_merged(ALL_EXTRACTED_INFO_V1, PATH_TECNICHE_JSON)

# Estrai tutti gli ingredienti e tutte le tecniche per un check
PATH_ELENCO_INGREDIENTI, PATH_ELENCO_TECNICHE, PATH_ELENCO_PIATTI = pf.extract_and_save_ingredients_techniques_and_dishes(ALL_EXTRACTED_INFO_V2)

# Se una licenza ha un nome incorretto, se la distanza non è troppo grande cambiala, altrimenti stampa
ALL_EXTRACTED_INFO_V3 = pf.correct_licenses_in_merged(ALL_EXTRACTED_INFO_V2, PATH_ELENCO_LICENZE_JSON)

# Modifica il file in modo da sostituire simbolo dell'ordine con nome dell'ordine
ALL_EXTRACTED_INFO_V4 = pf.sostituisci_ordine_con_nome(PATH_ELENCO_ORDINI_JSON, ALL_EXTRACTED_INFO_V3)

# ================================================================================
# INGREDIENTI
# ================================================================================
"""
In questa sezione vengono modificate le liste di ingredienti in base a similarità ottenute tramite metriche di
jaro-winkler e cosine similarity. L'idea è che, se due ingredienti hanno nomi simili, allora probabilmente sono la stessa cosa,
ed è possibile riuscire ad avere un solo nome per entrambi.
Ovviamente ogni run potrebbe aver estratto ingredienti diversi, e di conseguenza potrebbero essere necessarie tresholds
leggermente diverse. Per riuscire agevolmente a capire se la treshold è troppo bassa / alta, è possibile vedere
il file json prodotto da "estrai_differenze_json". Se la treshold è troppo bassa, il file json prodotto avrà un dizionario con
alcune entry incorrette, e bisognerà quindi alzare la treshold per ottenere un approccio più cautelativo.
"""

# Treshold per jaro-winkler
threshold = 0.93
dict_after_jw = pf.group_list_dict(PATH_ELENCO_INGREDIENTI, threshold, pf.jaro_winkler_similarity, "ingredients_dict_after_jw")
list_after_jw = pf.group_list(PATH_ELENCO_INGREDIENTI, threshold, pf.jaro_winkler_similarity, "ingredients_list_after_jw")
menu_updated_path = pf.sostituisci_ingredienti(dict_after_jw, ALL_EXTRACTED_INFO_V4, "all_extracted_info_v4_after_jw_ing")
pf.estrai_differenze_json(dict_after_jw)

# Treshold per cosine similarity
threshold = 0.7
dict_after_jw_and_cos = pf.group_list_dict(list_after_jw, threshold, pf.cosine_similarity, "ingredients_dict_after_jw_and_cos")
list_after_jw_and_cos = pf.group_list(list_after_jw, threshold, pf.cosine_similarity, "ingredients_list_after_jw_and_cos")
menu_updated_path = pf.sostituisci_ingredienti(dict_after_jw_and_cos, menu_updated_path, "all_extracted_info_v4_after_jw_and_cos_ing")
pf.estrai_differenze_json(dict_after_jw_and_cos)

# Unifica i valori facendo si che gli ingredienti che fanno match tra loro ma che hanno nomi diversi vengano sostituiti con il nome più corto
final_dict_path, fina_list_path = pf.processa_json(dict_after_jw_and_cos, "final_dict_ing", "final_list_ing")
ALL_EXTRACTED_INFO_V5 = pf.sostituisci_ingredienti(final_dict_path, menu_updated_path, "all_extracted_info_V5")
pf.estrai_differenze_json(final_dict_path)

# Test
target_string = "NDUJA"
threshold_value = 0.8
# Lev
print(pf.filter_similar_strings(target_string.upper(), fina_list_path, threshold_value))
threshold_value = 0.8
# Jw
print(pf.filter_similar_strings2(target_string.upper(), fina_list_path, threshold_value))
threshold_value = 0.9
# Cos
print(pf.filter_similar_strings3(target_string.upper(), fina_list_path, threshold_value))

# ================================================================================
# TECNICHE
# ================================================================================

"""
Tutto analogo, ma per le tecniche
"""

# Treshold per jaro-winkler
threshold = 0.94
dict_after_jw = pf.group_list_dict(PATH_ELENCO_TECNICHE, threshold, pf.jaro_winkler_similarity, "techniques_dict_after_jw")
list_after_jw = pf.group_list(PATH_ELENCO_TECNICHE, threshold, pf.jaro_winkler_similarity, "techniques_list_after_jw")
menu_updated_path = pf.sostituisci_tecniche(dict_after_jw, ALL_EXTRACTED_INFO_V5, "all_extracted_info_v5_after_jw_tec")
pf.estrai_differenze_json(dict_after_jw)

# Treshold per cosine similarity
threshold = 0.75
dict_after_jw_and_cos = pf.group_list_dict(list_after_jw, threshold, pf.cosine_similarity, "techniques_dict_after_jw_and_cos")
list_after_jw_and_cos = pf.group_list(list_after_jw, threshold, pf.cosine_similarity, "techniques_list_after_jw_and_cos")
menu_updated_path = pf.sostituisci_tecniche(dict_after_jw_and_cos, menu_updated_path, "all_extracted_info_v5_after_jw_and_cos_tec")
pf.estrai_differenze_json(dict_after_jw_and_cos)

# Unifica i valori facendo si che le tecniche che fanno match tra loro ma che hanno nomi diversi vengano sostituiti con il nome più LUNGO
final_dict_path, fina_list_path = pf.processa_json2(dict_after_jw_and_cos, "final_dict_ing_and_tec", "final_list_ing_and_tec")
ALL_EXTRACTED_INFO_V6 = pf.sostituisci_tecniche(final_dict_path, menu_updated_path, "all_extracted_info_V6")
pf.estrai_differenze_json(final_dict_path)

# Test
target_string = "COTTURA SOTTOVUOTO"
threshold_value = 0.8
# Lev
print(pf.filter_similar_strings(target_string.upper(), final_dict_path, threshold_value))
threshold_value = 0.8
# Jw
print(pf.filter_similar_strings2(target_string.upper(), final_dict_path, threshold_value))
threshold_value = 0.75
# Cos
print(pf.filter_similar_strings3(target_string.upper(), final_dict_path, threshold_value))

# Sostituisci tecniche con quelle trovate nel codice galattico, se la somiglianza è abbastanza alta
menu_updated_path = pf.find_and_replace_techniques_in_restaurants3(ALL_EXTRACTED_INFO_V6, PATH_TECNICHE_JSON, 0.95, 0.65, "PADELL")

# Creo nuove liste di ingredienti, tecniche e nomi dei piatti, basandomi sui menu non discorsivi, che in teoria sono piuttosto accurati e affidabili, così da fare un check
pf.extract_and_save_ingredients_techniques_and_dishes_only_selected_restaurants(ALL_EXTRACTED_INFO_V1,PATH_ELENCO_INGREDIENTI, PATH_ELENCO_TECNICHE, PATH_ELENCO_PIATTI, lista_ristoranti_con_menu_discorsivi)

# Sostituisci ingredienti trovati nei menu non discorsivi con quelli molto simili che sono all'interno del mio json
menu_updated_path = pf.find_and_replace_techniques_in_restaurants4(ALL_EXTRACTED_INFO_V6, PATH_ELENCO_INGREDIENTI,
                                                                   0.95, 0.65, "")

# Diversifica gli chef in base al nome, per evitare che due chef con lo stesso nome vengano considerati la stessa persona
menu_updated_path = pf.update_chefs_in_restaurants(menu_updated_path)

###################################################################################################################
# Costruzione GRAPH RAG
###################################################################################################################

from neo4j import GraphDatabase
import graph_rag.graph_construction_functions as gf
import graph_rag.graph_construction_queries as gc

URI = "bolt://localhost:7687"  # Cambia con il tuo indirizzo se necessario
USERNAME = "neo4j"
PASSWORD = "Lapizzaèsemprelapizza!:)"

db_driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD), database="pizzadb")

# Crea ristoranti
gf.estrai_ristorante(db_driver, menu_updated_path, gc.create_restaurant())

# Crea piatti ristorante
gf.estrai_piatto_per_ristorante(db_driver, menu_updated_path, gc.create_dish())

# Crea ingredienti per ogni piatto
gf.estrai_ingrediente_per_piatto(db_driver, menu_updated_path, gc.create_ing())

# Crea chef per ogni ristorante
gf.estrai_chef_per_ristorante(db_driver, menu_updated_path, gc.create_chef())

# Estrai i pianeti per ogni ristorante
gf.estrai_ristorante_per_pianeta(db_driver, menu_updated_path, gc.create_planet())

# Crea tecniche per ogni piatto
gf.estrai_tecniche_per_piatto(db_driver, menu_updated_path, gc.create_tec())

# Crea licenze da elenco licenze (ancora da collegare ai ristoranti)
gf.estrai_elenco_licenze(db_driver, PATH_ELENCO_LICENZE_JSON, gc.create_lic())

# Crea licenze collegate al ristorante, e verifica che siano coerenti con quelle ufficiali prese dall'elenco
gf.estrai_licenze_per_ristorante(db_driver, menu_updated_path, gc.create_lic_rest())

# Collega tecniche a licenze
path_tecniche_e_requisiti = PATH_TECNICHE_JSON
gf.process_json_and_create_relationships2(db_driver, path_tecniche_e_requisiti)

# Crea e collega ordini
gf.process_json_and_create_order_relationships(db_driver, menu_updated_path)

# Carica distanze pianeti
gf.carica_distanze(db_driver, PATH_DISTANZE)

# Aggiungi illegalità dei piatti dopo averli estratti
lista_piatti_legali = ["Il Risveglio del Drago Celeste", "Cosmic Harmony Infusion", "Sinfonia Multiversale in Otto Movimenti"]
lista_piatti_legali = [x.upper() for x in lista_piatti_legali]
gf.aggiorna_proprieta_legale(db_driver, lista_piatti_legali)

# Aggiungi relazioni per chef abilitati correttamente
gf.add_operated_relationship(db_driver)

def create_indexes(driver):
   with driver.session() as session:
       # Recupera tutte le etichette presenti nel database
       result = session.run("USE pizzadb CALL db.labels()")
       labels = [record[0] for record in result]

       for label in labels:
           session.run(f"USE pizzadb CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.nome IS UNIQUE")

       print(f"Creati constraint di unicità su {len(labels)} etichette: {labels}")

create_indexes(db_driver)

importlib.reload(pf)

# Rimuovi tutto (se mai ci fosse qualche problema)
#gf.remove_all(db_driver, gc.remove_all())
