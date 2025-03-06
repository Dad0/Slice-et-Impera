import os
import utils_functions.preprocessing_functions as pf
import utils_functions.preprocessing_prompts as pp
import json
from dotenv import load_dotenv
import os
import importlib
import roman
import csv

# Caricamento variabili
load_dotenv()

PATH_CODICE_GALATTICO = os.getenv("PATH_CODICE_GALATTICO")
PATH_MENU_DIR = os.getenv("PATH_MENU_DIR")
PATH_MANUALE_CUCINA = os.getenv("PATH_MANUALE_CUCINA")
PATH_MENU_DISCORSIVI = os.getenv("PATH_MENU_DISCORSIVI")
PATH_MENU_LISTA = os.getenv("PATH_MENU_LISTA")
DISH_DICT = os.getenv("DISH_DICT")
PATH_JSON_MERGED = os.getenv("PATH_JSON_MERGED")
PATH_JSON_MERGED_CORRECTED = os.getenv("PATH_JSON_MERGED_CORRECTED")
PATH_TECNICHE = os.getenv("PATH_TECNICHE")
PATH_ELENCO_PIATTI_MERGED = os.getenv("PATH_ELENCO_PIATTI_MERGED")
PATH_JSON_MERGED_CORRECTED2 = os.getenv("PATH_JSON_MERGED_CORRECTED2")
PATH_JSON_LICENCES_ELENCO = os.getenv("PATH_JSON_LICENCES_ELENCO")
PATH_JSON_ORDINI = os.getenv("PATH_JSON_ORDINI")
PATH_MENU_DIR_PROCESSED = os.getenv("PATH_MENU_DIR_PROCESSED")

PATH_ELENCO_INGREDIENTI_MERGED = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED")
PATH_ELENCO_INGREDIENTI_MERGED2 = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED2")
PATH_ELENCO_INGREDIENTI_MERGED3 = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED3")
PATH_ELENCO_INGREDIENTI_MERGED4 = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED4")
PATH_ELENCO_INGREDIENTI_MERGED5 = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED5")

PATH_ELENCO_TECNICHE_MERGED = os.getenv("PATH_ELENCO_TECNICHE_MERGED")
PATH_ELENCO_TECNICHE_MERGED2 = os.getenv("PATH_ELENCO_TECNICHE_MERGED2")
PATH_ELENCO_TECNICHE_MERGED3 = os.getenv("PATH_ELENCO_TECNICHE_MERGED3")
PATH_ELENCO_TECNICHE_MERGED4 = os.getenv("PATH_ELENCO_TECNICHE_MERGED4")

PATH_TECNICHE_AFTER_REVIEW = os.getenv("PATH_TECNICHE_AFTER_REVIEW")
PATH_ING_AFTER_REVIEW = os.getenv("PATH_ING_AFTER_REVIEW")
PATH_FINAL_MENU = os.getenv("PATH_FINAL_MENU")
PATH_ELENCO_TECNICHE_MERGED5 = os.getenv("PATH_ELENCO_TECNICHE_MERGED5")
PATH_ELENCO_INGREDIENTI_MERGED6 = os.getenv("PATH_ELENCO_INGREDIENTI_MERGED6")
PATH_ELENCO_PIATTI_MERGED2 = os.getenv("PATH_ELENCO_PIATTI_MERGED2")
PATH_MENU_FINAL = os.getenv("PATH_MENU_FINAL")
PATH_DISTANZE = os.getenv("PATH_DISTANZE")

###################################################################################################################
# CODICE GALATTICO
###################################################################################################################

# Converti in markdown (non standardizzato)
md_text = pf.docx_to_markdown(PATH_CODICE_GALATTICO, pf.transform_path(PATH_CODICE_GALATTICO, "md"))
# Estrai capitolo [...)
capitolo_tecniche = pf.extract_section(md_text, 4, 5)
# Estrai json con tecniche e licenze richieste
pf.extract_info(pf.transform_path(PATH_CODICE_GALATTICO, "json"), pp.generate_technique_extraction_prompt(capitolo_tecniche), "_tecniche")

###################################################################################################################
# MANUALE CUCINA
###################################################################################################################

# Converti in markdown (non standardizzato)
md_text2 = pf.pdf_to_markdown(PATH_MANUALE_CUCINA, pf.transform_path(PATH_MANUALE_CUCINA, "md"))

# Estrai capitolo [...)
capitolo_elenco_licenze = pf.extract_section(md_text2, "Capitolo 1", "Capitolo 2")
# Estrai json con elenco licenze
pf.extract_info(pf.transform_path(PATH_MANUALE_CUCINA, "json"), pp.generate_licenses_extraction_prompt(capitolo_elenco_licenze), "_elenco_licenze")

# Estrai capitolo [...)
capitolo_elenco_ordini = pf.extract_section(md_text2, "Capitolo 2", "Capitolo 3")
# Estrai json con elenco ordini
pf.extract_info(pf.transform_path(PATH_MANUALE_CUCINA, "json"), pp.generate_orders_extraction_prompt(capitolo_elenco_ordini), "_elenco_ordini")

###################################################################################################################
# MENU
###################################################################################################################
#Test menu preciso
importlib.reload(pf)
importlib.reload(pp)

# Converti menu in .txt normali
pf.convert_pdfs_to_markdown5(PATH_MENU_DIR, pf.transform_path2(PATH_MENU_DIR))
# Convertili prendendoti le grandezze dei font per ogni linea
pf.convert_pdfs_to_txt_with_size(PATH_MENU_DIR, pf.transform_path2(PATH_MENU_DIR))
# Converti in html
pf.convert_pdfs_to_html_with_size(PATH_MENU_DIR, pf.transform_path2(PATH_MENU_DIR))

# Crea cartella ristoranti con all'interno un txt per piatto
pf.process_all_html_files(pf.transform_path2(PATH_MENU_DIR), pf.transform_path2(PATH_MENU_DIR))

"""
Qui, per fare velocemente, ho manualmente creato 2 cartelle in PATH_MENU_DIR, denominate "Menu discorsivi" e "Menu lista".
In ogni cartella ho copiato le 15 cartelle corrispondenti ai menu discorsivi e ai menu fatti a lista.
"""

# Crea file con piatti e ingredienti per i menu discorsivi e non
pf.process_files_in_folders(pf.transform_path2(PATH_MENU_DISCORSIVI), pp.generate_ingredients_from_menu_extraction_prompt, "_piatti_e_ingredienti", pf.get_all_text)
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_DISCORSIVI), "_piatti_e_ingredienti.json")

pf.process_files_in_folders(pf.transform_path2(PATH_MENU_LISTA), pp.generate_ingredients_from_menu_extraction_prompt2, "_piatti_e_ingredienti", pf.get_ingredients)
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_LISTA), "_piatti_e_ingredienti.json")

"""
Qui andavo a prendere gli ultimi file creati (i merge con tutti i piatti e ingredienti per ogni ristorante, ovvero 30 file json, e li mettevo in PATH_MENU_DIR.
Poi runnavo la seguente funzione che va a correggere i nomi dei piatti, basandosi sul dish mapping
"""
pf.find_most_similar_and_replace_wrapper(pf.transform_path2(PATH_MENU_DIR), DISH_DICT, "_piatti_e_ingredienti")

# Stesso identico procedimento con piatti e tecniche
pf.process_files_in_folders(pf.transform_path2(PATH_MENU_DISCORSIVI), pp.generate_techniques_from_menu_extraction_prompt, "_piatti_e_tecniche", pf.get_all_text)
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_DISCORSIVI),"_piatti_e_tecniche.json")

pf.process_files_in_folders(pf.transform_path2(PATH_MENU_LISTA), pp.generate_ingredients_from_menu_extraction_prompt3, "_piatti_e_tecniche", pf.get_techniques)
pf.unisci_json_in_cartella(pf.transform_path2(PATH_MENU_LISTA),"_piatti_e_tecniche.json")

# Anche qui, sposto i 30 file creati e poi processo (mi ero ripromesso di automatizzare la cosa, ma non ce l'ho fatta, sorry)
pf.find_most_similar_and_replace_wrapper(pf.transform_path2(PATH_MENU_DIR), DISH_DICT, "_piatti_e_tecniche")

# Estrai ristorante, pianeta, chef e licenze
pf.extract_menu(pf.transform_path2(PATH_MENU_DIR), pp.generate_licenses_from_menu_extraction_prompt, "_pianeti_chef_e_licenze")

# Fai un merge dei vari json ottenuti dai menu per avere un unico json
risultato = pf.merge_all_restaurants(PATH_MENU_DIR_PROCESSED)
output_path = os.path.join(pf.transform_path2(PATH_MENU_DIR), "merged_results.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(risultato, f, indent=4, ensure_ascii=False)


# Se una emoji è a fianco al nome di un piatto, mettila nella sezione "ordini"
pf.process_emoji_in_menu(PATH_JSON_MERGED)

# Se una tecnica è finita tra gli ingredienti, mettila tra le tecniche (se non c'è già) e salva tutto in merged_results2
pf.correct_techniques_in_merged(PATH_JSON_MERGED, PATH_JSON_MERGED_CORRECTED, PATH_TECNICHE)

# Estrai tutti gli ingredienti e tutte le tecniche per un check
pf.extract_and_save_ingredients_techniques_and_dishes(PATH_JSON_MERGED_CORRECTED, PATH_ELENCO_INGREDIENTI_MERGED, PATH_ELENCO_TECNICHE_MERGED, PATH_ELENCO_PIATTI_MERGED)

# Se una licenza ha un nome incorretto, se la distanza non è troppo grande cambiala, altrimenti stampa. Salva tutto in merged_results3
pf.correct_licenses_in_merged(PATH_JSON_MERGED_CORRECTED, PATH_JSON_MERGED_CORRECTED2, PATH_JSON_LICENCES_ELENCO)

# Modifica il file in modo da sostituire simbolo dell'ordine con nome dell'ordine
ristoranti_modificati = pf.sostituisci_ordine_con_nome(PATH_JSON_ORDINI, PATH_JSON_MERGED_CORRECTED2, "new_merge.json")

# PROCESSA INGREDIENTI
json_path = PATH_ELENCO_INGREDIENTI_MERGED
threshold = 0.93
dict_after_jw = pf.group_list_dict(json_path, threshold, pf.jaro_winkler_similarity, "ingredients_dict_after_jw")
list_after_jw = pf.group_list(json_path, threshold, pf.jaro_winkler_similarity, "ingredients_list_after_jw")
json_path = PATH_ELENCO_INGREDIENTI_MERGED2
menu_updated_path = pf.sostituisci_ingredienti(dict_after_jw, json_path, "menu_after_jw_ing")
pf.estrai_differenze_json(PATH_ELENCO_INGREDIENTI_MERGED3)

threshold = 0.7
dict_after_jw_and_cos = pf.group_list_dict(list_after_jw, threshold, pf.cosine_similarity, "ingredients_dict_after_jw_and_cos")
list_after_jw_and_cos = pf.group_list(list_after_jw, threshold, pf.cosine_similarity, "ingredients_list_after_jw_and_cos")
menu_updated_path = pf.sostituisci_ingredienti(dict_after_jw_and_cos, menu_updated_path, "menu_after_jw_and_cos_ing")
pf.estrai_differenze_json(PATH_ELENCO_INGREDIENTI_MERGED4)

final_dict_path, fina_list_path = pf.processa_json(dict_after_jw_and_cos, "final_dict_ing", "final_list_ing")
pf.sostituisci_ingredienti(final_dict_path, menu_updated_path, "menu_with_reviewed_ing")
pf.estrai_differenze_json(PATH_ELENCO_INGREDIENTI_MERGED5)

# Test
target_string = "RADICI DI SINGOLARITA"
threshold_value = 0.8
print(pf.filter_similar_strings(target_string.upper(), fina_list_path, threshold_value))
threshold_value = 0.75
print(pf.filter_similar_strings2(target_string.upper(), fina_list_path, threshold_value))
threshold_value = 0.9
print(pf.filter_similar_strings3(target_string.upper(), fina_list_path, threshold_value))

# PROCESSA TECNICHE
json_path = PATH_ELENCO_TECNICHE_MERGED  # Sostituisci con il percorso corretto
threshold = 0.94
dict_after_jw = pf.group_list_dict(json_path, threshold, pf.jaro_winkler_similarity, "techniques_dict_after_jw")
list_after_jw = pf.group_list(json_path, threshold, pf.jaro_winkler_similarity, "techniques_list_after_jw")
menu_updated_path = pf.sostituisci_tecniche(dict_after_jw, menu_updated_path, "menu_after_jw_tec")
pf.estrai_differenze_json(PATH_ELENCO_TECNICHE_MERGED2)

threshold = 0.75
dict_after_jw_and_cos = pf.group_list_dict(list_after_jw, threshold, pf.cosine_similarity, "techniques_dict_after_jw_and_cos")
list_after_jw_and_cos = pf.group_list(list_after_jw, threshold, pf.cosine_similarity, "techniques_list_after_jw_and_cos")
menu_updated_path = pf.sostituisci_tecniche(dict_after_jw_and_cos, menu_updated_path, "menu_after_jw_and_cos_tec")
pf.estrai_differenze_json(PATH_ELENCO_TECNICHE_MERGED3)

#dict_after_jw_and_cos = pf.group_list_dict2(dict_after_jw, threshold, pf.cosine_similarity, "techniques_dict_after_jw_and_cos_longest_better")
#list_after_jw_and_cos = pf.group_list2(list_after_jw, threshold, pf.cosine_similarity, "techniques_list_after_jw_and_cos_longest_better")

importlib.reload(pf)
final_dict_path, fina_list_path = pf.processa_json2(dict_after_jw_and_cos, "final_dict_ing_and_tec", "final_list_ing_and_tec")
pf.sostituisci_tecniche(final_dict_path, menu_updated_path, "menu_with_reviewed_ing_and_tec")
pf.estrai_differenze_json(PATH_ELENCO_TECNICHE_MERGED4)

# Test
target_string = "COTTURA SOTTOVUOTO FRUGALE"
threshold_value = 0.8
print(pf.filter_similar_strings(target_string.upper(), final_dict_path, threshold_value))
threshold_value = 0.8
print(pf.filter_similar_strings2(target_string.upper(), final_dict_path, threshold_value))
threshold_value = 0.75
print(pf.filter_similar_strings3(target_string.upper(), final_dict_path, threshold_value))

importlib.reload(pf)
path_tecniche = PATH_TECNICHE
menu_new = PATH_TECNICHE_AFTER_REVIEW
menu_updated_path = pf.find_and_replace_techniques_in_restaurants3(menu_new, PATH_TECNICHE, 0.95, 0.65, "PADELL")


# Merge di ingredienti e tecniche aggiornate
input_ingr = PATH_ING_AFTER_REVIEW
output_file = "menu_update_final.json"
pf.merge_menus(menu_updated_path, input_ingr, output_file)


# Correggo ingredienti basandomi sulla lista degli ingredienti nei menu non discorsivi, che in teoria è piuttosto accurata e affidabile..

rest_list = ["Anima Cosmica", "Armonia Universale", "Cosmica Essenza", "L'Eco di Pandora", "Eredità Galattica Hub Temporale della Gastronomia Interstellare",
             "L'Essenza dell'Infinito","L'Equilibrio Quantico","L'Essenza di Asgard","L'Oasi delle Dune Stellari",
             "Le Stelle che Ballano","Ristorante delle Dune Stellari","Sala del Valhalla","Sapore del Dune",
             "Stelle dell'Infinito Celestiale","Tutti a TARSvola"]
pf.extract_and_save_ingredients_techniques_and_dishes_only_selected_restaurants(PATH_JSON_MERGED_CORRECTED, PATH_ELENCO_INGREDIENTI_MERGED, PATH_ELENCO_TECNICHE_MERGED, PATH_ELENCO_PIATTI_MERGED, rest_list)

importlib.reload(pf)
importlib.reload(pp)
# Ora sostituisco ingredienti
menu_updated_path = pf.find_and_replace_techniques_in_restaurants4(PATH_FINAL_MENU, PATH_ELENCO_INGREDIENTI_MERGED,
                                                                   0.95, 0.65, "")

# Diversifico gli chef in base al nome!
pf.update_chefs_in_restaurants(menu_updated_path)
menu_updated_path = PATH_MENU_FINAL

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
gf.estrai_elenco_licenze(db_driver, PATH_JSON_LICENCES_ELENCO, gc.create_lic())

# Crea licenze collegate al ristorante, e verifica che siano coerenti con quelle ufficiali prese dall'elenco
gf.estrai_licenze_per_ristorante(db_driver, menu_updated_path, gc.create_lic_rest())

# Collega tecniche a licenze
path_tecniche_e_requisiti = PATH_TECNICHE
gf.process_json_and_create_relationships2(db_driver, path_tecniche_e_requisiti)

# Crea e collega ordini
gf.process_json_and_create_order_relationships(db_driver, menu_updated_path)

# Carica distanze pianeti
gf.carica_distanze(db_driver, PATH_DISTANZE)

# Aggiungi illegalità dei piatti dopo averli estratti
importlib.reload(gf)
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
importlib.reload(gf)
importlib.reload(gc)
# Rimuovi tutto (se mai ci fosse qualche problema)
gf.remove_all(db_driver, gc.remove_all())






