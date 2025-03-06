import os
from typing import Dict, List, Any, Annotated
import json
import logging
import re
import csv
from langgraph.types import Send
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from graph_rag import cypher_correction as cc

def extract_cypher_query_from_log():
    import re
    log_file_path = r'C:\Users\Awotc\PycharmProjects\Kaggle DataPizza\agents\neo4j_queries.log'  # Modifica con il path corretto del file

    # Apriamo e leggiamo il contenuto del file di log
    with open(log_file_path, 'r') as log_file:
        log = log_file.read()
    match = re.search(r'RUN "cypher(.*?)" {}', log, re.DOTALL)

    if match:
        cypher_query = match.group(1).strip()
        return cypher_query
    else:
        return -1

def intersect_lists_of_lists(lists: List[List[str]]) -> List[str]:
    # Controlla se c'è almeno una lista vuota e stampa un warning
    if any(len(lst) == 0 for lst in lists):
        print("Attenzione: almeno una delle liste è vuota.")
        return -1
    # Filtra le liste non vuote
    non_empty_lists = [lst for lst in lists if lst]

    # Se non ci sono liste non vuote, restituisci una lista vuota
    if not non_empty_lists:
        return []

    # Converti la prima lista in un set per iniziare l'intersezione
    intersection_result = set(non_empty_lists[0])

    # Calcola l'intersezione con le altre liste
    for lst in non_empty_lists[1:]:
        intersection_result &= set(lst)

    # Converte l'intersezione finale di nuovo in una lista
    return list(intersection_result)

def load_dish_dict(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def append_dish_indices(row_id, dish_names, dish_dict, csv_filename, empty_result=0):

    # Trova gli indici per ogni piatto presente nel dizionario
    #print(f"PIATTI = {dish_names}")
    #print(f"DICT = {dish_dict}")

    if empty_result == 1:
        # Per ora, se non sai il risultato, spara a caso il 23, e spera in bene :)
        result_str = "23"
    else:
        dish_dict = {k.upper(): v for k, v in dish_dict.items()}
        indices = [str(dish_dict[dish]) for dish in dish_names if dish in dish_dict]
        result_str = ",".join(indices)

    print(result_str)

    try:
        file_exists = os.path.exists(csv_filename)

        with open(csv_filename, mode='a', newline='', encoding='utf-8') as f:
            if not file_exists:
                f.write("row_id,result\n")
            f.write(f"{row_id},\"{result_str}\"\n")
    except Exception as e:
        print("ERRORE DURANTE LA SCRITTURA")

def setup_logger(nome_entità):
    # Creazione della cartella logs se non esiste
    os.makedirs("logs", exist_ok=True)

    # Definizione del nome del file di log basato sul nome dell'entità
    log_filename = f"logs/{nome_entità}.log"

    # Configurazione del logger
    logger = logging.getLogger(nome_entità)
    logger.setLevel(logging.INFO)  # Imposta il livello di log

    # Creazione di un handler per scrivere i log su file
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Aggiunta dell'handler al logger
    if not logger.handlers:  # Evita di aggiungere più handler allo stesso logger
        logger.addHandler(file_handler)

    return logger

def clean_cypher_query(query: str) -> str:
    return query.lstrip("cypher\n").strip()


import re


def replace_query_names3(text, mappings):
    """
    Sostituisce, nel testo, ogni occorrenza di 'queryName' (in maniera case-insensitive)
    con il relativo 'bestMatch' fornito in mappings. Se il bestMatch contiene parole aggiuntive
    (cioè un prefisso) rispetto a queryName, tali parole vengono calcolate dinamicamente e considerate
    nella sostituzione, in modo da evitare di duplicare informazioni già presenti nel testo.

    Ad esempio, se:
      text = "sono accessibili ai membri dell'Ordine della 'Galassia di Andromeda'"
      queryName = "Galassia di Andromeda"
      bestMatch = "ORDINE DELLA GALASSIA DI ANDROMEDA"
    allora l'output sarà:
      "sono accessibili ai membri dell'ORDINE DELLA GALASSIA DI ANDROMEDA"

    Parametri:
      - text: la stringa su cui effettuare le sostituzioni.
      - mappings: lista di dizionari, ciascuno con le chiavi 'queryName' e 'bestMatch'.

    Restituisce:
      - Il testo modificato.
    """
    modified_text = text
    for mapping in mappings:
        query_name = mapping['queryName']
        best_match = mapping['bestMatch']

        # Calcola l'eventuale prefisso in eccesso presente in best_match rispetto a query_name.
        # Ad esempio, se best_match è "ORDINE DELLA GALASSIA DI ANDROMEDA" e query_name è "Galassia di Andromeda",
        # allora extra sarà "ORDINE DELLA".
        extra = best_match.upper().replace(query_name.upper(), "").strip()

        if extra:
            # Costruisce un pattern che intercetta, in modo case-insensitive,
            # l'eventuale presenza opzionale del prefisso extra, eventuali virgolette e il query_name.
            pattern = re.compile(
                r"(?i)(?:"
                + re.escape(extra)
                + r"\s+)?[\"']?"
                + re.escape(query_name)
                + r"[\"']?"
            )
        else:
            # Se non c'è un prefisso extra, utilizza un semplice pattern case-insensitive.
            pattern = re.compile(re.escape(query_name), re.IGNORECASE)

        modified_text = pattern.sub(best_match, modified_text)
    return modified_text
def replace_query_names_sembra_ottimo(text, mappings):
    """
    Sostituisce, nel testo, ogni occorrenza di 'queryName' (case-insensitive)
    con il relativo 'bestMatch', tenendo conto di variazioni minori nel testo.
    """

    modified_text = text
    for mapping in mappings:
        query_name = mapping['queryName']
        best_match = mapping['bestMatch']

        # Scomponiamo la query_name in parole per consentire variazioni nelle virgolette
        words = query_name.split()
        pattern = r"(?i)\b" + r"\s*['\"]?\s*".join(map(re.escape, words)) + r"\b"

        modified_text = re.sub(pattern, best_match, modified_text)

    return modified_text


# def replace_query_names(text, mappings):
#     """
#     Sostituisce, nel testo, ogni occorrenza di 'queryName' (case-insensitive)
#     con il relativo 'bestMatch', tollerando variazioni minori (spazi, virgolette opzionali).
#
#     Dopo la sostituzione, per ciascun bestMatch, se l'occorrenza non è interamente
#     racchiusa tra apici singoli, viene sostituita con la versione racchiusa da apici.
#     Inoltre, se non c'è uno spazio tra il token precedente e gli apici, ne viene aggiunto uno.
#
#     Esempio:
#       text = "- non utilizzano la tecnica della 'FERMENTAZIONE QUANTICO BIOMETRICA'
#               ma utilizzano sia il Taglio', sia la tecnica della 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA'"
#       mappings = [
#           {'queryName': 'taglio', 'bestMatch': 'TECNICHE DI TAGLIO', 'jaroWinkler_distance': 0},
#           {'queryName': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', 'bestMatch': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', 'jaroWinkler_distance': 0},
#           {'queryName': 'FERMENTAZIONE QUANTICO BIOMETRICA', 'bestMatch': 'FERMENTAZIONE QUANTICO BIOMETRICA', 'jaroWinkler_distance': 0}
#       ]
#
#       Risultato atteso:
#       "- non utilizzano la tecnica della 'FERMENTAZIONE QUANTICO BIOMETRICA'
#        ma utilizzano sia il 'TECNICHE DI TAGLIO', sia la tecnica della 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA'"
#     """
#     modified_text = text
#     # Fase 1: Sostituzione dei queryName con bestMatch (ignora variazioni di spazi e virgolette)
#     for mapping in mappings:
#         query_name = mapping['queryName']
#         best_match = mapping['bestMatch']
#         # Costruisce un pattern flessibile per intercettare query_name con eventuali virgolette o spazi extra
#         words = query_name.split()
#         pattern = r"(?i)\b" + r"\s*['\"]?\s*".join(map(re.escape, words)) + r"\b"
#         modified_text = re.sub(pattern, best_match, modified_text)
#
#     # Fase 2: Aggiunge gli apici se il bestMatch non è completamente racchiuso da essi.
#     for mapping in mappings:
#         best_match = mapping['bestMatch']
#         # Il pattern intercetta best_match con eventuali spazi e apici opzionali
#         pattern = re.compile(
#             r"(?i)(?P<lquote>')?\s*" + re.escape(best_match) + r"\s*(?P<rquote>')?"
#         )
#
#         def wrap_quotes(m):
#             # Ottieni la posizione del match
#             pos = m.start()
#             # Se entrambi gli apici sono presenti, restituisce il match invariato
#             if m.group('lquote') == "'" and m.group('rquote') == "'":
#                 return m.group(0)
#             # Altrimenti, controlla se c'è uno spazio prima del match nel testo originale
#             # Se non c'è spazio, aggiungilo
#             prefix = ""
#             if pos > 0 and m.string[pos - 1] != " ":
#                 prefix = " "
#             return prefix + f"'{best_match}'"
#
#         modified_text = pattern.sub(wrap_quotes, modified_text)
#
#     return modified_text

def replace_query_names(text, mappings):
    """
    Sostituisce, nel testo, ogni occorrenza di 'queryName' (case-insensitive)
    con il relativo 'bestMatch', tollerando variazioni minori (spazi, virgolette opzionali).

    Dopo la sostituzione, per ciascun bestMatch, se l'occorrenza non è interamente
    racchiusa tra apici singoli, viene sostituita con la versione racchiusa da apici.
    Inoltre, se non c'è uno spazio tra il token precedente e gli apici, ne viene aggiunto uno.

    Esempio:
      text = "- non utilizzano la tecnica della 'FERMENTAZIONE QUANTICO BIOMETRICA'
              ma utilizzano sia il Taglio', sia la tecnica della 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA'"
      mappings = [
          {'queryName': 'taglio', 'bestMatch': 'TECNICHE DI TAGLIO', ...},
          {'queryName': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', 'bestMatch': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', ...},
          {'queryName': 'FERMENTAZIONE QUANTICO BIOMETRICA', 'bestMatch': 'FERMENTAZIONE QUANTICO BIOMETRICA', ...}
      ]

      Risultato atteso:
      "- non utilizzano la tecnica della 'FERMENTAZIONE QUANTICO BIOMETRICA'
       ma utilizzano sia il 'TECNICHE DI TAGLIO', sia la tecnica della 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA'"
    """
    modified_text = text
    # Fase 1: Sostituzione dei queryName con bestMatch (ignora variazioni di spazi e virgolette)
    for mapping in mappings:
        query_name = mapping['queryName']
        best_match = mapping['bestMatch']
        # Costruisce un pattern flessibile per intercettare query_name con eventuali virgolette o spazi extra
        words = query_name.split()
        pattern = r"(?i)\b" + r"\s*['\"]?\s*".join(map(re.escape, words)) + r"\b"
        modified_text = re.sub(pattern, best_match, modified_text)

    # Fase 2: Aggiunge gli apici se il bestMatch non è completamente racchiuso da essi.
    # Il pattern usa lookbehind/lookahead per assicurarsi di matchare solo occorrenze isolate.
    for mapping in mappings:
        best_match = mapping['bestMatch']
        pattern = re.compile(
            r"(?i)(?<!\w)(?P<lquote>')?\s*" + re.escape(best_match) + r"\s*(?P<rquote>')?(?!\w)"
        )

        def wrap_quotes(m):
            # Se entrambi gli apici sono presenti, restituisce il match invariato
            if m.group('lquote') == "'" and m.group('rquote') == "'":
                return m.group(0)
            # Se manca l'apice a sinistra o a destra, restituisce best_match racchiuso tra apici
            # Mantenendo uno spazio se il match non ne aveva
            return f"'{best_match}'"

        modified_text = pattern.sub(wrap_quotes, modified_text)

    return modified_text

# text = "- non utilizzano la tecnica della 'FERMENTAZIONE QUANTICO BIOMETRICa ma utilizzano sia il 'Taglio', sia la tecnica della 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA'"
# mappings = [{'queryName': 'taglio', 'bestMatch': 'TECNICHE DI TAGLIO', 'jaroWinkler_distance': 0}, {'queryName': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', 'bestMatch': 'COTTURA SOTTOVUOTO FRUGALE ENERGETICAMENTE NEGATIVA', 'jaroWinkler_distance': 0}, {'queryName': 'FERMENTAZIONE QUANTICO BIOMETRICA', 'bestMatch': 'FERMENTAZIONE QUANTICO BIOMETRICA', 'jaroWinkler_distance': 0}]
# print(replace_query_names(text, mappings))

def replace_query_names2(text, mappings):
    """
    Sostituisce, nel testo, ogni occorrenza di 'queryName' (ignora il case)
    con il relativo 'bestMatch' fornito in mappings.

    Parametri:
      - text: la stringa su cui effettuare le sostituzioni.
      - mappings: lista di dizionari, ciascuno con le chiavi 'queryName' e 'bestMatch'.

    Restituisce:
      - Il testo modificato.
    """
    modified_text = text
    for mapping in mappings:
        query_name = mapping['queryName']
        best_match = mapping['bestMatch']
        # Compilo un pattern regex che ignora il case
        pattern = re.compile(re.escape(query_name), re.IGNORECASE)
        modified_text = pattern.sub(best_match, modified_text)
    return modified_text

def merge_list_of_lists(a: List[List[str]], b: List[List[str]]) -> List[List[str]]:
    #print("Merge input a:", a)
    #print("Merge input b:", b)
    # Se una delle liste è vuota, restituisce l'altra
    if not a:
        return b
    if not b:
        return a
    # Aggiungi tutte le liste di b alla lista a senza appiattirle
    result = a + b
    #print("Merge result:", result)
    return result

# In disuso ora che uso solo lev...
def costruisci_query(query_names, entity_name, cosine_threshold=0.6, jaro_threshold=0.1, property="nome"):
    # Costruzione della parte della query per la cosine similarity
    query = f"""
    USE pizzadb
    // LIST COSINE SIMILARITY + JARO-WINKLER DISTANCE per una lista di {entity_name}
    WITH {query_names} AS queryNames
    UNWIND queryNames AS queryName
    MATCH (i:{entity_name})
    WITH i, queryName, i.{property} AS targetName
    WHERE i.{property} IS NOT NULL

    // Generazione degli n-grams per la query e per il target (con n=3)
    WITH i, queryName, targetName,
         [x IN range(0, size(queryName) - 3) | substring(queryName, x, 3)] AS query_ngrams,
         [x IN range(0, size(targetName) - 3) | substring(targetName, x, 3)] AS target_ngrams
    // Calcolo del prodotto scalare (dot product) tra gli n-grams comuni
    WITH i, query_ngrams, target_ngrams, queryName, targetName,
         REDUCE(s = 0, n IN query_ngrams | s + CASE WHEN n IN target_ngrams THEN 1 ELSE 0 END) AS dot_product,
         sqrt(size(query_ngrams)) AS query_magnitude,
         sqrt(size(target_ngrams)) AS target_magnitude
    // Calcolo della cosine similarity
    WITH i, query_magnitude, target_magnitude, dot_product, queryName, targetName,
         CASE
             WHEN query_magnitude > 0 AND target_magnitude > 0 THEN dot_product / (query_magnitude * target_magnitude)
             ELSE 0
         END AS cosine_similarity

    // Calcolo della Jaro-Winkler Distance
    WITH i, cosine_similarity, queryName, targetName,
         apoc.text.jaroWinklerDistance(queryName, targetName) AS jaroWinkler_distance

    // Filtraggio con entrambi i criteri
    WHERE cosine_similarity > {cosine_threshold} OR jaroWinkler_distance < {jaro_threshold}
    RETURN queryName, i.{property}, cosine_similarity, jaroWinkler_distance
    ORDER BY queryName, cosine_similarity DESC, jaroWinkler_distance ASC
    """
    return query

def costruisci_query2(query_names, entity_name, property="nome"):
    query = f"""
        USE pizzadb
        WITH {query_names} AS queryNames
        UNWIND queryNames AS queryName
        MATCH (i:{entity_name})
        WITH i, queryName, i.{property} AS targetName
        WHERE targetName IS NOT NULL

        // Calcola la Jaro-Winkler distance tra la query e il target
        WITH i, queryName, targetName, apoc.text.levenshteinDistance(queryName, targetName) AS jaroWinkler_distance
        ORDER BY queryName, jaroWinkler_distance ASC

        // Raggruppa per queryName e seleziona il risultato con la distanza più bassa
        WITH queryName, head(collect({{node: i, targetName: targetName, jaroWinkler_distance: jaroWinkler_distance}})) AS bestResult
        RETURN queryName, bestResult.targetName AS bestMatch, bestResult.jaroWinkler_distance AS jaroWinkler_distance
        ORDER BY queryName
    """
    return query

def fix_encoding(text):
    try:
        return text.encode('latin1').decode('utf-8')
    except Exception:
        return text

def leggi_csv(path, n_righe=50):
    righe_letto = []

    with open(path, newline='', encoding='utf-8', errors='replace') as file:
        reader = csv.reader(file)
        header = next(reader)  # Salta l'header
        for i, riga in enumerate(reader):
            if i >= n_righe:
                break
            riga_correzione = [fix_encoding(colonna) for colonna in riga]
            righe_letto.append(riga_correzione[0])

    return righe_letto

def extract_entities(json_data):
    # Se nomi non esiste o esiste ma è vuoto, non creare un agente apposta!
    json_result = {chiave: valore for chiave, valore in json_data.items() if valore["nomi"] and any(valore["nomi"])}

    if isinstance(json_result, dict):
        #print("E' già un dizionario")
        dati = json_result
    else:
        dati = json.loads(json_result)

    return dati

def askRAG(db_driver, query_for_typos):
    with db_driver.session() as session:
        result  = session.run(query_for_typos)
        return result.data()  # Restituisce i risultati come lista di dizionari

def create_sends(entity, dicts):
    sends = []
    for e, d in zip(entity, dicts):
        send_data = {"single_entity_name": e}
        send_data.update(d)

        sends.append(Send("EntityAgent", send_data))
    return sends

def get_single_entity_dict(state):
    return {k: v for k, v in state.items() if k != "single_entity_name"}

def replace_with_upper_case_insensitive2(text, words_list):
    for word in words_list:

        # Primo tentativo: sostituzione standard case-insensitive
        updated_text = re.sub(r'(?i)\b' + re.escape(word) + r'\b', word.upper(), text)

        # Se il testo non è cambiato, significa che non è stata trovata la corrispondenza esatta.
        if updated_text == text:

            tokens = word.split()
            pattern_ignore_quotes = r"(?i)\b" + r"\s*['’]?\s*".join(map(re.escape, tokens)) + r"\b"
            updated_text = re.sub(pattern_ignore_quotes, word.upper(), text)

        text = updated_text  # Aggiorna il testo per la prossima iterazione
    return text



import re
import difflib
from typing import List, Tuple


import re

def replace_with_upper_case_insensitive(text, words_list):
    for word in words_list:
        # Usa negative lookbehind e lookahead per definire i confini,
        # in modo da non limitarsi ai soli confini di parola (\b)
        pattern = r'(?i)(?<!\w)' + re.escape(word) + r'(?!\w)'
        updated_text = re.sub(pattern, word.upper(), text)

        # Se la sostituzione standard non ha avuto effetto, prova una variante
        if updated_text == text:
            tokens = word.split()
            pattern_ignore_quotes = (
                r'(?i)(?<!\w)' +
                r'\s*["\']?' +
                r"\s*".join(map(re.escape, tokens)) +
                r'\s*["\']?(?!\w)'
            )
            updated_text = re.sub(pattern_ignore_quotes, word.upper(), text)
        text = updated_text  # Aggiorna il testo per la prossima iterazione
    return text



def process_entity(single_entity_name, single_entity_dict, db_driver, nomi_upper, max_length):
    """
    Processa l'entità in base al nome e alle impostazioni nel dizionario.

    Parametri:
      - single_entity_name: nome dell'entità corrente (es. "Tecnica", "Ristorante", ...)
      - single_entity_dict: dizionario con le proprietà dell'entità
      - db_driver: driver per eseguire la query
      - af: oggetto che contiene le funzioni per costruire ed eseguire la query
      - nomi_upper: nome o lista di nomi da utilizzare nella query (già in maiuscolo)
      - max_length: valore usato per alcune condizioni logiche (es. per "Licenza" e "Chef")

    Ritorna:
      - Il dizionario aggiornato dell'entità e i risultati ottenuti dalla query.
    """

    def execute_query(query_entity, property_val):
        """
        Costruisce ed esegue la query per una determinata entità e proprietà.
        Deduplica i risultati e li restituisce.
        """
        query_for_typos = costruisci_query2(nomi_upper, entity_name=query_entity, property=property_val)
        risultati = askRAG(db_driver, query_for_typos)
        print(f"RISULTATI per {single_entity_name}: {risultati}")
        unique_results = {tuple(d.items()) for d in risultati}
        risultati = [dict(t) for t in unique_results]
        #print(f"RISULTATI per {single_entity_name}: {risultati}")
        return risultati

    # Configurazioni per casi specifici
    configurations = {
        "Tecnica": {
            "condition": lambda: single_entity_dict.get("tecnica generica", "").lower() == "si",
            "query_entity": "Tecnica",
            "property": "tipologia"
        },
        "Ristorante": {
            "condition": lambda: single_entity_dict.get("su pianeta", "").lower() == "si",
            "query_entity": "Pianeta",
            "property": "nome"
        },
        "Licenza": {
            "condition": lambda: max_length <= 3 and nomi_upper != "qualunque",
            "query_entity": "Licenza",
            "property": "sigla"
        },
        "Chef": {
            "condition": lambda: True,
            # Se max_length<=3 esegue la query su "Licenza" con "sigla", altrimenti su "Licenza" con "nome"
            "query_entity": lambda: "Licenza",
            "property": lambda: "sigla" if max_length <= 3 else "nome"
        },
        "Distanza": {
            "condition": lambda: True,
            "query_entity": "Pianeta",
            "property": "nome"
        }
        # "Legale" verrà gestito separatamente
    }

    risultati = None

    # Gestione dell'entità "Legale": nessuna query eseguita
    if single_entity_name == "Legale":
        print("Nessuna query eseguita per 'Legale'.")
    elif single_entity_name in configurations and configurations[single_entity_name]["condition"]():
        config = configurations[single_entity_name]
        # Valuta eventuali lambda per ottenere i valori dinamici
        query_entity = config["query_entity"]() if callable(config["query_entity"]) else config["query_entity"]
        property_val = config["property"]() if callable(config["property"]) else config["property"]
        risultati = execute_query(query_entity, property_val)
    else:
        # Caso di default: usa l'entità corrente e la proprietà "nome"
        risultati = execute_query(single_entity_name, "nome")

    # Se l'entità non è "Legale" e abbiamo risultati, aggiorna il dizionario
    if single_entity_name != "Legale" and risultati is not None:
        single_entity_dict["descrizione"] = replace_query_names(single_entity_dict["descrizione"], risultati)
        #print(f"\nQuesto è il nodo {single_entity_name}")
        single_entity_dict["nomi"] = [item['bestMatch'] for item in risultati]

    return single_entity_dict, risultati

def build_query_for_entity(single_entity_name, single_entity_dict, risultati, max_length, get_validate_cypher):
    """
    Costruisce la query per l'entità in base alle impostazioni fornite.

    Parametri:
      - single_entity_name: nome dell'entità (es. "Tecnica", "Ristorante", etc.)
      - single_entity_dict: dizionario contenente le proprietà dell'entità
      - risultati: lista di risultati ottenuti dalla query precedente
      - max_length: valore usato per alcune condizioni (es. per "Licenza" e "Chef")
      - get_validate_cypher: funzione (o callable) per validare Cypher (ritorna True/False)
      - af: oggetto che contiene metodi come replace_query_names()

    Ritorna:
      - La stringa finale della query da usare.
    """

    # Aggiorna il dizionario se l'entità non è "Legale"
    if single_entity_name != "Legale":
        single_entity_dict["descrizione"] = replace_query_names(single_entity_dict["descrizione"], risultati)
        #print(f"\nQuesto è il nodo {single_entity_name}")
        single_entity_dict["nomi"] = [item['bestMatch'] for item in risultati]

    # Inizia a costruire la query riga per riga
    query_lines = []
    query_lines.append("Trova i piatti che:")
    query_lines.append(f"- {single_entity_dict['descrizione']}")

    # Lista di regole da aggiungere in modo condizionale
    rules = []

    # Regole per "Tecnica"
    if single_entity_name == "Tecnica":
        rules.append({
            "condition": lambda: single_entity_dict.get("tecnica generica", "").lower() == "si",
            "text": "- Usa la proprietà 'tipologia' del nodo Tecnica nella query"
        })
        rules.append({
            "condition": lambda: single_entity_dict.get("tecnica generica", "").lower() == "no",
            "text": "- Usa la proprietà 'nome' del nodo Tecnica nella query"
        })

    # Regole per "Ristorante"
    if single_entity_name == "Ristorante":
        rules.append({
            "condition": lambda: single_entity_dict.get("su pianeta", "").lower() == "si",
            "text": "- Usa la relazione Ristorante 'SITUATO_SU' Pianeta per trovare il collegamento di un ristorante con un pianeta, ma ricordati che il tuo obiettivo finale è trovare i piatti offerti dal ristorante"
        })
        rules.append({
            "condition": lambda: single_entity_dict.get("su pianeta", "").lower() == "no",
            "text": "- Usa la proprietà 'nome' del nodo Ristorante nella query"
        })

    # Regole per "Licenza" e "Chef" in base a max_length
    if single_entity_name in ["Licenza", "Chef"]:
        rules.append({
            "condition": lambda: max_length <= 3,
            "text": "- Usa la proprietà 'sigla' del nodo Licenza nella query"
        })
        rules.append({
            "condition": lambda: max_length > 3,
            "text": "- Usa la proprietà 'nome' del nodo Licenza nella query"
        })

    # Regole specifiche per "Licenza"
    if single_entity_name == "Licenza":
        rules.append({
            "condition": lambda: True,
            "text": ("- REGOLA IMPORTANTE: Se la query richiede di verificare la proprietà 'livello' o 'grado' in una relazione, "
                     "assicurati di usare la proprietà 'grado' della relazione stessa in 'RICHIEDE_LICENZA', non delle entità nodali "
                     "(come nel nodo 'Licenza', 'Chef', o 'Tecnica'). In particolare, nelle relazioni 'RICHIEDE_LICENZA', cerca e usa "
                     "sempre la proprietà 'grado' di tale relazione per il filtro, e non quella del nodo 'Licenza'. Usa la sintassi corretta "
                     "in Cypher per accedere ai dati della relazione, ad esempio usando 'r.grado' quando la relazione è indicata come 'r'")
        })
        rules.append({
            "condition": lambda: True,
            "text": "- INFORMAZIONE IMPORTANTE: Ogni licenza può avere diversi gradi, ma puoi assumere che 0 sia il grado base"
        })

    # Regola specifica per "Chef"
    if single_entity_name == "Chef":
        rules.append({
            "condition": lambda: True,
            "text": ("- REGOLA IMPORTANTE: Se la query richiede di verificare la proprietà 'livello' o 'grado' in una relazione, "
                     "assicurati di usare la proprietà 'grado' della relazione stessa in 'HA_LICENZA', non delle entità nodali "
                     "(come nel nodo 'Licenza', 'Chef', o 'Tecnica'). In particolare, nelle relazioni 'HA_LICENZA', cerca e usa "
                     "sempre la proprietà 'grado' di tale relazione per il filtro, e non quella del nodo 'Licenza'. Usa la sintassi corretta "
                     "in Cypher per accedere ai dati della relazione, ad esempio usando 'h.grado' quando la relazione è indicata come 'h'")
        })

    # Regola per "Ingrediente"
    if single_entity_name == "Ingrediente":
        rules.append({
            "condition": lambda: get_validate_cypher(),
            "text": ("INFORMAZIONE IMPORTANTE: Se (e solo se) hai bisogno di escludere i piatti contenenti un certo ingrediente, "
                     "puoi usare `NOT EXISTS { MATCH (p)-[:CONTIENE]->(i:Ingrediente) WHERE i.nome IN [...] }`.")
        })

    # Regole per "Distanza"
    if single_entity_name == "Distanza":
        rules.append({
            "condition": lambda: True,
            "text": ("- Usa la relazione Ristorante 'SITUATO_SU' Pianeta per trovare il collegamento di un ristorante con un pianeta, "
                     "ma ricordati che il tuo obiettivo finale è trovare i piatti offerti dal ristorante")
        })
        rules.append({
            "condition": lambda: True,
            "text": ("- Usa la proprietà 'distanza' della relazione 'HA_DISTANZA' per trovare la distanza tra pianeti, "
                     "ma ricordati che il tuo obiettivo finale è trovare i piatti offerti da uno o più ristoranti")
        })

    # Regola per "Abilitazione"
    if single_entity_name == "Abilitazione":
        rules.append({
            "condition": lambda: True,
            "text": ("- Usa la relazione Tecnica 'PUO_ESSERE_OPERATA_CORRETAMENTE_DA' Chef per trovare gli chef abilitati ad eseguire una tecnica, "
                     "ma ricordati che il tuo obiettivo finale è trovare i piatti offerti dal ristorante")
        })

    # Regola per "Legale"
    if single_entity_name == "Legale":
        rules.append({
            "condition": lambda: True,
            "text": ("- Usa la proprietà booleana 'legale' del nodo 'Legale' per trovare i piatti che rientrano nella legalità, "
                     "ma ricordati che il tuo obiettivo finale è trovare i piatti offerti dal ristorante")
        })

    # Aggiunge al testo della query tutte le regole che soddisfano la loro condizione
    for rule in rules:
        if rule["condition"]():
            query_lines.append(rule["text"])

    # Regole finali comuni
    query_lines.append("- REGOLA IMPORTANTE: ogni query deve dare come output sempre e solo i nomi dei piatti.")
    if single_entity_name != "Legale":
        query_lines.append("- REGOLA IMPORTANTE2: cerca sempre di capire se un'entità dev'essere presente insieme ad altre entità in contemporanea oppure no.")
    else:
        query_lines.append("- REGOLA IMPORTANTE2: non ti servono relazioni di alcun tipo per questa query. Ti basta controllare il campo 'legale' di un piatto per capire se rientra nella legalità o no.")

    # Unisce le righe in un'unica stringa separata da newline
    query_for_entity = "\n".join(query_lines)
    return query_for_entity

import logging

def execute_initial_query(single_entity_name, query_for_entity, validate_cypher, gr, logger_error):
    """
    Esegue la query iniziale tramite gr.askChatty, catturando i log in "neo4j_queries.log".

    Parametri:
      - query_for_entity: la query da inviare
      - validate_cypher: funzione/criterio per validare la query
      - db_driver: driver per l'interazione con il database Neo4j
      - gr: modulo/oggetto che contiene il metodo askChatty per l'esecuzione della query
      - logger_error: logger configurato per Neo4j

    Ritorna:
      - result: il risultato ottenuto dalla query
      - generated_cypher: la query generata (o grezza) da gr.askChatty
      - error: eventuale eccezione intercettata (None se nessun errore)
    """
    error = None
    generated_cypher = None
    result = None
    try:
        # Cattura i log in un file temporaneo
        with open("neo4j_queries" + "_" + f"{single_entity_name}" + ".log", "w") as log_file:
            console_handler = logging.StreamHandler(log_file)
            console_handler.setLevel(logging.DEBUG)
            logger_error.addHandler(console_handler)

            result, generated_cypher = gr.askChatty(query_for_entity, validate_cypher)

            logger_error.removeHandler(console_handler)
        print(result)
    except Exception as e:
        error = e
        # Se serve, è possibile ottenere l'intero traceback:
        # error_trace = traceback.format_exc()
        # logging.error(f"Errore Neo4j: {e}\nQuery: {generated_cypher or 'N/A'}\nTraceback:\n{error_trace}")
    return result, generated_cypher, error

def extract_dishes_from_result(result):
    """
    Estrae i nomi dei piatti dal risultato della query.

    Parametri:
      - result: lista di dizionari restituiti dalla query

    Ritorna:
      - dishes: lista dei nomi dei piatti estratti
    """
    dishes = []
    if result:
        for piatto in result:
            try:
                # Presupponiamo che il primo valore del dizionario contenga il nome del piatto
                dish = list(piatto.values())[0]
                dishes.append(dish)
            except Exception:
                continue
    return dishes

def correct_query_if_needed(query_for_entity, generated_cypher, error, validate_cypher, db_driver):
    """
    Se la query iniziale non restituisce risultati, tenta di correggerla usando cc.askChatty_for_cypher_with_example.

    Parametri:
      - query_for_entity: query iniziale usata per generare il messaggio di correzione
      - generated_cypher: la query grezza generata in precedenza
      - error: eventuale eccezione intercettata nell'esecuzione iniziale
      - validate_cypher: funzione/criterio per validare la query
      - db_driver: driver per interagire con Neo4j
      - cc: modulo/oggetto contenente il metodo askChatty_for_cypher_with_example
      - af: modulo/oggetto con metodi di supporto (clean_cypher_query, etc.)

    Ritorna:
      - corrected_cypher: la query corretta dopo il tentativo di correzione
      - result: risultato ottenuto eseguendo la query corretta
      - dishes: lista dei piatti estratti dalla query corretta
    """
    print("\nLa query non ha portato risultati, provo a correggerla")
    print(f"\nQuery che sto per mandare al db: \n{generated_cypher}")
    result = None
    corrected_cypher = None

    if error:
        print("Sto mandando la query a Neo4j con tanto di errore")
        error_message = f"\n\nConsider that this cypher query has generated this error:\n{error}"
        result, corrected_cypher = cc.askChatty_for_cypher_with_example(
            query_for_entity,
            clean_cypher_query(generated_cypher) + error_message,
            validate_cypher
        )
    else:
        print("Sto mandando la query a Neo4j senza errori")
        result, corrected_cypher = cc.askChatty_for_cypher_with_example(
            query_for_entity,
            clean_cypher_query(generated_cypher),
            validate_cypher
        )
    print(f"Query corretta: {corrected_cypher}")
    print(f"Risultato ottenuto dopo la correzione: {result}")
    corrected_cypher = clean_cypher_query(corrected_cypher[0]["query"])
    print(f"Ecco la nuova query corretta dopo lo strip: \n{corrected_cypher}")
    print("La mando al db")
    try:
        result = askRAG(db_driver, corrected_cypher)
    except:
        print("Nessun risultato dalla query corretta :(")
    print(f"Piatti ottenuti: {result}")
    dishes = extract_dishes_from_result(result)
    print(dishes)
    return corrected_cypher, result, dishes

# def process_query(query_for_entity, validate_cypher, db_driver, gr, cc, logger_error):
def process_query(single_entity_name, query_for_entity, db_driver, validate_cypher, gr, cc, logger_error):
    """
    Esegue la query iniziale, gestisce eventuali errori e corregge la query se non sono ottenuti risultati.

    Parametri:
      - query_for_entity: query da inviare al database
      - validate_cypher: funzione/criterio per la validazione della query
      - db_driver: driver per Neo4j
      - gr: modulo/oggetto per l'esecuzione iniziale della query (metodo askChatty)
      - cc: modulo/oggetto per la correzione della query (metodo askChatty_for_cypher_with_example)
      - af: modulo/oggetto di supporto contenente metodi utili (clean_cypher_query, extract_cypher_query_from_log, askRAG, ecc.)
      - logger: logger principale
      - logger_error: logger specifico per Neo4j

    Ritorna:
      - generated_cypher: la query (eventualmente corretta)
      - dishes: lista dei piatti ottenuti
    """
    #print(f"Sono in process query {query_for_entity}")
    # result, generated_cypher, error = execute_initial_query(query_for_entity, validate_cypher, db_driver, gr,
    #                                                         logger_error)

    result, generated_cypher, error = execute_initial_query(single_entity_name, query_for_entity, validate_cypher, gr, logger_error)


    if error:
        print(f"ERRORE:\n{error}")
        generated_cypher = extract_cypher_query_from_log()
        print(f"Query che ha dato errore: {generated_cypher}")
    else:
        # Pulisce la query generata
        generated_cypher = clean_cypher_query(generated_cypher[0]["query"])

    dishes = extract_dishes_from_result(result)

    # Se non sono stati ottenuti piatti, tenta di correggere la query
    if len(dishes) == 0:
        print(f"Cypher generata che non ha portato a risultati:\n{generated_cypher}")

        generated_cypher, result, dishes = correct_query_if_needed(
            query_for_entity, generated_cypher, error, validate_cypher, db_driver
        )

    return generated_cypher, dishes

def setup_logging_for_entity(entity_name: str):
    """
    Configura il logging per l'entità specificata.

    Vengono creati:
      - Un logger personalizzato per l'entità, ottenuto tramite setup_logger (già definito in af).
      - Un logger "neo4j" configurato per scrivere in un file di log con nome dedicato all'entità.

    Parametri:
      - entity_name (str): Nome dell'entità (es. "Tecnica", "Ristorante", etc.)

    Ritorna:
      - tuple: (logger, logger_error)
          * logger: il logger principale per l'entità.
          * logger_error: il logger configurato per Neo4j, con livello DEBUG.
    """
    # Ottieni il logger personalizzato per l'entità (si assume che setup_logger sia definita in af)
    logger = setup_logger(entity_name)

    # Configura il logging di base per scrivere su un file specifico per l'entità
    logging.basicConfig(
        filename=f"neo4j_queries_{entity_name}.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding='utf-8'
    )

    # Crea/ottieni il logger dedicato a Neo4j e imposta il livello DEBUG
    logger_error = logging.getLogger("neo4j")
    logger_error.setLevel(logging.DEBUG)

    return logger, logger_error

def evaluate(Tree, node, data):
    """
    Valuta ricorsivamente l'albero sintattico prodotto dal parser Lark.

    Parametri:
      - node: nodo dell'albero (Tree o stringa)
      - data: dizionario con i dati (piatti) associati ad ogni entità

    Ritorna:
      Il risultato dell'operazione (lista di piatti).
    """
    if isinstance(node, str):
        return data[node]
    if not isinstance(node, Tree):
        return node

    if node.data == "union":
        # Calcola il primo termine e unisce gli eventuali termini successivi
        result_eval = evaluate(Tree, node.children[0], data)
        for child in node.children[1:]:
            result_eval = list(set(result_eval) | set(evaluate(Tree, child, data)))
        return result_eval
    elif node.data == "intersection":
        # Calcola il primo termine e interseca gli eventuali termini successivi
        result_eval = evaluate(Tree, node.children[0], data)
        for child in node.children[1:]:
            result_eval = list(set(result_eval) & set(evaluate(Tree, child, data)))
        return result_eval
    else:
        return evaluate(Tree, node.children[0], data)

def aggiungi_consigli(question: str, entita_coinvolte: list, consigli: dict) -> str:
    """
    Aggiunge alla domanda l'elenco delle entità coinvolte e i relativi consigli.

    Parametri:
      - question: domanda iniziale
      - entita_coinvolte: lista delle entità da utilizzare
      - consigli: dizionario con i messaggi di consiglio per ciascuna entità

    Ritorna:
      La domanda aggiornata con i consigli aggiunti.
    """
    # Creazione della stringa con le entità coinvolte nel formato richiesto
    entita_str = ", ".join(f"'{entita}'" for entita in entita_coinvolte)

    # Aggiunta dell'elenco delle entità alla domanda
    question += f"\n\nLe entità che devi utilizzare sono le seguenti: {entita_str}"

    # Aggiunta dei consigli corrispondenti alle entità coinvolte
    for entita in entita_coinvolte:
        if entita in consigli:
            question += f"\n{consigli[entita]}"

    # Aggiunta della frase finale
    question += "\n\nNon utilizzare altre entità per nessun motivo."
    return question

def evaluate_entities_query(i, state: dict, all_entities: list, ap, QuestionRewriter) -> any:
    """
    Valuta la domanda e restituisce il risultato finale in base alle entità coinvolte.

    Se sono coinvolte almeno due entità, la funzione:
      - Ottiene il prompt di sistema tramite ap.get_set_evaluator_prompt()
      - Recupera l'ultima domanda presente in state["messages"]
      - Aggiunge alla domanda i consigli relativi alle entità coinvolte
      - Costruisce un prompt per il LLM e invia la domanda tramite un modello GPT-4 (con output strutturato)
      - Usa il risultato (formula) per parsarlo con Lark e valutarlo combinando i risultati (piatti) associati a ciascuna entità
      - Stampa e restituisce il risultato finale

    Se viene trovata un'unica entità, restituisce direttamente il risultato associato.

    Parametri:
      - state: dizionario contenente le chiavi "messages" e "dishes"
      - all_entities: lista delle entità coinvolte
      - ap: oggetto con il metodo get_set_evaluator_prompt() per ottenere il prompt di sistema

    Ritorna:
      Il risultato finale (lista di piatti o singolo piatto) ottenuto dalla valutazione.
    """
    # Se sono coinvolte almeno due entità
    if len(all_entities) >= 2:
        system = ap.get_set_evaluator_prompt()
        question = state["messages"][-1].content

        # Dizionario dei consigli per ciascuna entità
        consigli = {
            "Ingrediente": "Considera che il nodo Ingrediente si occupa di trovare i piatti che contengono o non contengono determinati ingredienti",
            "Tecnica": "Considera che il nodo Tecnica si occupa di trovare i piatti che contengono o non contengono determinate tecniche di cucina",
            "Ristorante": "Considera che il nodo Ristorante si occupa di trovare i piatti di un determinato ristorante o su un determinato pianeta",
            "Licenza": "Considera che il nodo Licenza si occupa di trovare i piatti che richiedono una licenza di un certo grado",
            "Chef": "Considera che il nodo Chef si occupa di trovare i piatti preparati da uno chef con una licenza di un certo grado",
            "Distanza": "Considera che il nodo Distanza si occupa di trovare i piatti preparati in ristoranti che distano una certa distanza da un pianeta",
            "Ordine": "Considera che il nodo Ordine si occupa di trovare i piatti che fanno parte di un determinato ordine",
            "Abilitazione": "Considera che il nodo Abilitazione si occupa di trovare i piatti che utilizzano tecniche di cottura che richiedono uno chef abilitato correttamente",
            "Legale": "Considera che il nodo Legale si occupa di trovare i piatti che soddisfano determinate normative legali riguardo agli ingredienti"
        }

        # Aggiorna la domanda con i consigli e la stampa
        question = aggiungi_consigli(question, all_entities, consigli)
        print(f"\nLa domanda iniziale era{question}")

        # Costruisci il prompt per il LLM usando ChatPromptTemplate (già importato nel modulo)
        query_cleaner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: {question}"),
            ]
        )

        # Inizializza il modello LLM e configura l'output strutturato (utilizzando il modello GPT-4o)
        llm = ChatOpenAI(model="gpt-4o")
        structured_llm = llm.with_structured_output(QuestionRewriter)
        grader_llm = query_cleaner_prompt | structured_llm

        # Invoca il LLM per riscrivere/valutare la domanda
        result = grader_llm.invoke({"question": question})

        # Rimuovi eventuali virgolette se necessario (linea commentata)
        # result.reply = result.reply.replace('"', "'")
        print(result.reply)
        logger = setup_logger("Set evaluator")
        log_message = "\n" + str(i) + " " + result.reply + "\n"
        logger.info(log_message)

        # Crea un dizionario che associa ad ogni entità il relativo risultato (piatti)
        data = {}
        for i, ent in enumerate(all_entities):
            data[ent] = state["dishes"][i]

        # Importa Lark e Tree per il parsing della formula
        from lark import Lark, Tree

        # Definizione della grammatica per il parser Lark
        grammar = """
            start: union_expr
            union_expr: intersection_expr ("∪" intersection_expr)*   -> union
            intersection_expr: atom ("∩" atom)*                       -> intersection
            atom: "(" union_expr ")" | SYMBOL
            SYMBOL: /[a-zA-Z_][a-zA-Z0-9_]*/

            %import common.WS
            %ignore WS
        """

        # Crea il parser con la grammatica definita
        parser = Lark(grammar, parser="lalr")


        # Ottieni la formula (risposta) dal LLM, parseala e valuta l'albero ottenuto
        formula = result.reply
        parsed_tree = parser.parse(formula)
        result_final = evaluate(Tree, parsed_tree, data)

        print("RISULTATO FINALE")
        print(result_final)
        return result_final

    # Se è presente una sola entità, restituisce direttamente il risultato associato
    else:
        result_single = state["dishes"][0]
        print(f"L'unica entità trovata ha dato come risultati:\n{result_single}")
        return result_single
