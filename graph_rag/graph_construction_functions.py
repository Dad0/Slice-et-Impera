import roman
import csv
import json

def crea_ristorante(db_driver, nome_ristorante, create_restaurant):
    try:
        # Usa la sessione con 'with' per garantire che venga chiusa correttamente
        with db_driver.session() as session:
            # Esegui la query per creare il nodo
            result = session.run(create_restaurant, nome=nome_ristorante)
            # Restituisce True se il nodo è stato creato correttamente
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False  # In caso di errore, restituisce False

def estrai_ristorante(db_driver, path, create_restaurant):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        nome_ristorante = ristorante['ristorante'].upper()  # Converti il nome in maiuscolo
        print(ristorante['ristorante'])
        crea_ristorante(db_driver, nome_ristorante, create_restaurant)
    return

def estrai_piatto_per_ristorante(db_driver, path, create_dish):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        nome_ristorante = ristorante['ristorante'].upper()  # Converti il nome in maiuscolo
        for menu in ristorante['menu']:
            nome_piatto = menu['piatto'].upper()  # Converti il nome del piatto in maiuscolo
            print(nome_piatto)
            print(nome_ristorante)
            crea_piatto_per_ristorante(db_driver, nome_piatto, nome_ristorante, create_dish)
    return

def crea_piatto_per_ristorante(driver, nome_piatto, nome_ristorante, create_dish):
    try:
        with driver.session() as session:
            result = session.run(create_dish, nome_piatto=nome_piatto, nome_ristorante=nome_ristorante)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False

def estrai_ingrediente_per_piatto(db_driver, path, create_ing):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        print(ristorante['ristorante'])
        for menu in ristorante['menu']:
                print(ristorante['ristorante'])
                print(menu['ingredienti'])
                nome_piatto = menu['piatto'].upper()
                for ingrediente in menu['ingredienti']:  # Itera ogni tecnica
                    nome_ingrediente = ingrediente.upper()
                    crea_ingrediente_per_piatto(db_driver, nome_ingrediente, nome_piatto, create_ing)
    return

def crea_ingrediente_per_piatto(driver, nome_ingrediente, nome_piatto, create_ing):
    try:
        with driver.session() as session:
            # Verifica se il piatto esiste
            result_piatto = session.run(
                "USE pizzadb MATCH (p:Piatto {nome: $nome_piatto}) RETURN p",
                nome_piatto=nome_piatto
            )
            if result_piatto.single() is None:
                print(f"ERRORE: Il piatto {nome_piatto} non esiste nel database.")
                return False

            # Esegui la query per creare la relazione
            result = session.run(create_ing, nome_ingrediente=nome_ingrediente, nome_piatto=nome_piatto)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False

def drop_all_constraints_and_indexes(driver):
    with driver.session() as session:
        # Rimuove tutti i vincoli
        #constraints = session.run("SHOW CONSTRAINTS")
        constraints = session.run("USE pizzadb SHOW CONSTRAINTS")
        for record in constraints:
            print(f"USE pizzadb DROP CONSTRAINT {record['name']}")
            session.run(f"USE pizzadb DROP CONSTRAINT {record['name']}")

        # Rimuove tutti gli indici
        indexes = session.run("USE pizzadb SHOW INDEXES")
        for record in indexes:
            session.run(f"USE pizzadb DROP INDEX {record['name']}")

        # Elimina tutti i nodi
        session.run("USE pizzadb MATCH (n) DETACH DELETE n")

        print("✅ Database completamente pulito da indici e vincoli!")

def remove_all(driver, remove_all):
    drop_all_constraints_and_indexes(driver)
    with driver.session() as session:
        result = session.run(remove_all)
    return

def read_all_ingredients(driver, read_all_ingredients_query):
    with driver.session() as session:
        result = session.run(read_all_ingredients_query)
        ingredients = []
        for record in result:
            #print(record)
            ingredients.append(record["i"]["nome"])
        return ingredients

def estrai_chef_per_ristorante(db_driver, path, create_chef):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        print(ristorante['ristorante'])
        for menu in ristorante['menu']:
                print(ristorante['ristorante'])
                print(ristorante['chef'])
                nome_chef = ristorante['chef'].upper()
                nome_ristorante = ristorante['ristorante'].upper()
                crea_chef_per_ristorante(db_driver, nome_chef, nome_ristorante, create_chef)
    return

def crea_chef_per_ristorante(driver, nome_chef, nome_ristorante, create_chef):
    try:
        with driver.session() as session:
            result = session.run(create_chef, nome_chef=nome_chef, nome_ristorante=nome_ristorante)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False

def estrai_ristorante_per_pianeta(db_driver, path, create_planet):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        print(ristorante['ristorante'])
        print(ristorante)
        for menu in ristorante['menu']:
                print(ristorante['ristorante'])
                print(ristorante['pianeta'])
                nome_ristorante = ristorante['ristorante'].upper()
                nome_pianeta = ristorante['pianeta'].upper()

                crea_ristorante_per_pianeta(db_driver, nome_ristorante, nome_pianeta, create_planet)
    return

def crea_ristorante_per_pianeta(driver, nome_ristorante, nome_pianeta, create_planet):
    try:
        with driver.session() as session:
            result = session.run(create_planet, nome_ristorante=nome_ristorante, nome_pianeta=nome_pianeta)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False

def crea_tecnica_per_piatto(driver, nome_tecnica, nome_piatto, create_tec):
    try:
        with driver.session() as session:
            result = session.run(create_tec, nome_tecnica=nome_tecnica, nome_piatto=nome_piatto)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False

def estrai_tecniche_per_piatto(db_driver, path, create_tec):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        print(ristorante['ristorante'])
        for menu in ristorante['menu']:
            print(menu['piatto'])
            print(menu['tecniche'])
            for tecnica in menu['tecniche']:  # Itera ogni tecnica
                nome_tecnica = tecnica.upper()
                nome_piatto = menu['piatto'].upper()
                crea_tecnica_per_piatto(db_driver, nome_tecnica, nome_piatto, create_tec)  # Passa tecnica singolarmente
    return

def crea_elenco_licenze(db_driver, licenze, create_lic):
    try:
        with db_driver.session() as session:
            for licenza in licenze:
                print(licenza["livelli"])
                licenze_numeriche = converti_livelli(licenza["livelli"])
                print(licenze_numeriche)
                session.run(create_lic,
                            nome_licenza=licenza["nome"].upper(),
                            sigla_licenza=licenza["sigla"].upper(),
                            gradi=licenze_numeriche)
        print("Licenze inserite correttamente in Neo4j.")
    except Exception as e:
        print(f"Errore durante l'inserimento delle licenze in Neo4j: {e}")

def estrai_elenco_licenze(db_driver, path, create_lic):
    try:
        with open(path, "r", encoding="utf-8") as f:
            licenze = json.load(f)
        crea_elenco_licenze(db_driver, licenze, create_lic)
    except Exception as e:
        print(f"Errore durante la lettura del file JSON: {e}")

def converti_livelli(lista):
    """
    Converte i numeri romani in interi se presenti in una lista.
    Se l'input non è una lista, restituisce una lista vuota.

    - Se l'elemento è una stringa che inizia per "Livello ":
         * Se la parte successiva è un numero (es. "0"), lo converte in int.
         * Se contiene un segno "+" (es. "VI+"), lo converte in numero (aggiungendo 0.5 per indicare il "+").
         * Altrimenti prova a convertire la parte in numero romano.
         * Se la conversione fallisce (ad esempio per "n"), lascia l'elemento invariato.
    - Altrimenti, aggiunge l'elemento così com'è.
    """
    if not isinstance(lista, list):
        return []

    risultati = []
    for elemento in lista:
        if isinstance(elemento, str) and elemento.startswith("Livello "):
            parte_numerica = elemento.replace("Livello ", "").strip()
            # Caso: la parte è un numero (es. "0")
            if parte_numerica.isdigit():
                risultati.append(int(parte_numerica))
            # Caso: presenza di un segno "+"
            elif "+" in parte_numerica:
                parte_pulita = parte_numerica.replace("+", "").strip()
                try:
                    if parte_pulita.isdigit():
                        num = int(parte_pulita)
                    else:
                        num = roman.fromRoman(parte_pulita.upper())
                    # Aggiungiamo 0.5 per indicare il "+"
                    risultati.append(num + 1)
                except roman.InvalidRomanNumeralError:
                    risultati.append(elemento)
            # Caso normale: proviamo a convertire da romano
            else:
                # Se la parte è "n", non aggiungiamo nulla
                if parte_numerica.lower() == 'n':
                    continue
                try:
                    num = roman.fromRoman(parte_numerica.upper())
                    risultati.append(num)
                except roman.InvalidRomanNumeralError:
                    risultati.append(elemento)
        else:
            risultati.append(elemento)
    return risultati

def estrai_licenze_per_ristorante(db_driver, path, create_lic):
    import json

    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Itera i ristoranti nel JSON
    for ristorante in data:
        # Controlla se esiste una chiave valida per il nome
        nome_ristorante = ristorante.get('chef')
        if not nome_ristorante:
            print(f"Errore: Non è stato possibile trovare il nome del ristorante. Dati ignorati: {ristorante}")
            continue

        print(f"Ristorante: {nome_ristorante}")

        # Itera tutte le licenze del ristorante
        for licenza in ristorante.get('licenze', []):
            # Controlla che la licenza abbia le chiavi richieste
            if 'nome_licenza' not in licenza or 'grado_licenza' not in licenza:
                print(f"Errore: Licenza incompleta. Dati ignorati: {licenza}")
                continue

            #print(f"Licenza: {licenza['nome_licenza']}, Grado: {licenza['grado_licenza']}")

            # Passa i dati a Neo4j per scriverli nel database
            print(create_lic)
            success = crea_licenza_per_ristorante(
                db_driver,
                nome_licenza=licenza['nome_licenza'].upper(),
                grado_licenza=licenza['grado_licenza'],
                nome_ristorante=nome_ristorante.upper(),
                create_lic=create_lic
            )

            if success:
                pass
                #print(f"Licenza '{licenza['nome_licenza']}' creata con successo!")
            else:
                print(f"Errore nella creazione della licenza: {licenza['nome_licenza']}")

def crea_licenza_per_ristorante(driver, nome_licenza, grado_licenza, nome_ristorante, create_lic):
    try:
        # Conversione del grado in intero
        try:
            if grado_licenza.isdigit():
                grado = int(grado_licenza)
            else:
                grado_licenza = grado_licenza.upper().replace(" ", "")  # Rimuove spazi extra
                if grado_licenza.endswith("+"):
                    grado = roman.fromRoman(grado_licenza[:-1]) + 1  # Rimuove il "+" e aggiunge 1
                else:
                    grado = roman.fromRoman(grado_licenza)
        except Exception as e:
            raise ValueError(f"Errore nella conversione del grado per la licenza '{nome_licenza}': {e}")

        # Verifica che la licenza esista in anagrafica e che il grado sia valido
        verifica_licenza_e_grado(driver, nome_licenza, grado)

        with driver.session() as session:
            result = session.run(
                create_lic,
                nome_licenza=nome_licenza,
                nome_ristorante=nome_ristorante,
                grado=grado
            )
            record = result.single()
            if record is None:
                raise ValueError(
                    f"Errore: relazione non creata per ristorante '{nome_ristorante}' e licenza '{nome_licenza}'.")
            return True
    except Exception as e:
        print(f"Errore durante la creazione della licenza: {e}")
        return False

def verifica_licenza_e_grado(driver, nome_licenza, grado):
    with driver.session() as session:
        result = session.run(
            """
            USE pizzadb
            MATCH (l:Licenza {nome: $nome_licenza})
            RETURN COALESCE(l.livelli, []) AS livelli
            """,
            nome_licenza=nome_licenza
        )
        record = result.single()
        if record is None:
            raise ValueError(f"Licenza '{nome_licenza}' non trovata in anagrafica.")

        livelli = record.get("livelli", [])

        # Se la licenza ha livelli definiti e il grado non è presente, lo aggiungiamo
        if grado not in livelli:
            livelli.append(grado)
            session.run(
                """
                USE pizzadb
                MATCH (l:Licenza {nome: $nome_licenza})
                SET l.livelli = $livelli
                """,
                nome_licenza=nome_licenza,
                livelli=livelli
            )
            print(f"Aggiunto grado {grado} alla licenza '{nome_licenza}'.")

def extract_techniques_recursively2(d):
    """
    Estrae i nomi delle tecniche dal JSON in UPPER CASE.
    Naviga ricorsivamente per gestire categorie e sotto-categorie.
    Considera che una tecnica è individuata quando si trova un dizionario con la chiave "requisiti".
    """
    techniques = set()

    if isinstance(d, dict):
        for key, value in d.items():
            # Se il valore è un dizionario e contiene "requisiti", allora consideriamo 'key' come nome della tecnica
            if isinstance(value, dict) and "requisiti" in value:
                techniques.add(key.upper())
            else:
                techniques.update(extract_techniques_recursively(value))
    elif isinstance(d, list):
        for item in d:
            techniques.update(extract_techniques_recursively(item))

    return techniques

def roman_to_int(s):
    """Converte un numero romano in un intero."""
    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    s = s.upper()
    total = 0
    prev = 0
    for char in reversed(s):
        value = roman.get(char, 0)
        if value < prev:
            total -= value
        else:
            total += value
            prev = value
    return total

def convert_livello(l):
    """Converte il livello in intero; se è un numero romano lo trasforma."""
    try:
        return int(l)
    except ValueError:
        return roman_to_int(l)

def extract_techniques_recursively(d):
    """
    Estrae i nomi delle tecniche dal JSON in UPPER CASE.
    Naviga ricorsivamente per gestire categorie e sotto-categorie.
    Una tecnica è individuata se il dizionario ha la chiave "requisiti".
    """
    techniques = set()
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) and "requisiti" in value:
                techniques.add(key.upper())
            else:
                techniques.update(extract_techniques_recursively(value))
    elif isinstance(d, list):
        for item in d:
            techniques.update(extract_techniques_recursively(item))
    return techniques

def iterate_techniques(d, tipologia=None):
    """
    Scorre ricorsivamente il dizionario e restituisce triplette
    (nome_tecnica, dettagli, tipologia) per ogni tecnica (cioè che contiene "requisiti").

    Se tipologia è None, al primo livello la chiave corrente viene considerata come tipologia.
    """
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) and "requisiti" in value:
                # Se siamo in un nodo tecnica, usiamo la tipologia corrente (passata o quella attuale)
                yield key, value, tipologia
            else:
                new_tipologia = tipologia if tipologia is not None else key
                yield from iterate_techniques(value, tipologia=new_tipologia)
    elif isinstance(d, list):
        for item in d:
            yield from iterate_techniques(item, tipologia=tipologia)

def process_json_and_create_relationships2(db_driver, json_path):
    # Legge il JSON da file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    techniques_container = data.get("tecniche")
    if techniques_container is None:
        raise ValueError("Il JSON non contiene la chiave 'tecniche'.")

    # Funzione interna per iterare ricorsivamente sulle tecniche
    def iterate_techniques(d):
        """
        Scorre ricorsivamente il dizionario e restituisce coppie (nome_tecnica, dettagli)
        per ogni dizionario che rappresenta una tecnica (cioè che contiene "requisiti").
        """
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, dict) and "requisiti" in value:
                    yield key, value
                else:
                    yield from iterate_techniques(value)
        elif isinstance(d, list):
            for item in d:
                yield from iterate_techniques(item)

    # Estrae tutti i nomi delle tecniche (in UPPER CASE) per riferimento
    technique_names = extract_techniques_recursively2(techniques_container)

    with db_driver.session() as session:
        for tech_name, tech_details in iterate_techniques(techniques_container):
            if not tech_name or tech_name.upper() not in technique_names:
                continue

            # Verifica se la tecnica esiste già nel database (aggiungendo LIMIT 1 per evitare warning)
            result_tech = session.run(
                """
                USE pizzadb
                MATCH (t:Tecnica)
                WHERE toUpper(apoc.text.clean(t.nome)) = toUpper(apoc.text.clean($tech_name))
                RETURN t
                LIMIT 1
                """,
                tech_name=tech_name
            )
            if result_tech.single() is None:
                session.run(
                    """
                    USE pizzadb
                    CREATE (t:Tecnica {nome: $tech_name})
                    """,
                    tech_name=tech_name
                )
                print(f"Tecnica '{tech_name}' aggiunta al DB.")

            # Processa i requisiti della tecnica
            for req in tech_details.get("requisiti", []):
                license_sigla = req.get("sigla")
                livello = req.get("livello")

                if not license_sigla:
                    continue

                # Verifica che la licenza esista (aggiungendo LIMIT 1 anche qui, se necessario)
                result_license = session.run(
                    """
                    USE pizzadb
                    MATCH (l:Licenza)
                    WHERE toUpper(apoc.text.clean(l.sigla)) = toUpper(apoc.text.clean($license_sigla))
                    RETURN l
                    LIMIT 1
                    """,
                    license_sigla=license_sigla
                )
                if result_license.single() is None:
                    raise ValueError(f"La licenza con sigla '{license_sigla}' non esiste nel DB pizzadb.")

                # Crea (o MERGE) la relazione tra tecnica e licenza con la proprietà "livello"
                session.run(
                    """
                    USE pizzadb
                    MATCH (t:Tecnica)
                    WHERE toUpper(apoc.text.clean(t.nome)) = toUpper(apoc.text.clean($tech_name))
                    MATCH (l:Licenza)
                    WHERE toUpper(apoc.text.clean(l.sigla)) = toUpper(apoc.text.clean($license_sigla))
                    MERGE (t)-[r:RICHIEDE_LICENZA]->(l)
                    SET r.grado = $grado
                    """,
                    tech_name=tech_name,
                    license_sigla=license_sigla,
                    livello=livello
                )
    print("Tutte le relazioni sono state create correttamente.")

def process_json_and_create_order_relationships(db_driver, json_path):
    # Legge il JSON da file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Se il JSON è un dizionario che contiene "ristoranti", lo usa; altrimenti, se è una lista, lo usa direttamente
    if isinstance(data, dict):
        ristoranti = data.get("ristoranti", [])
    elif isinstance(data, list):
        ristoranti = data
    else:
        raise ValueError("Il contenuto del file JSON non è in un formato valido.")

    with db_driver.session() as session:
        for ristorante in ristoranti:
            for piatto in ristorante.get("menu", []):
                # Convertiamo il nome del piatto in maiuscolo
                piatto_nome = piatto.get("piatto", "").upper()
                ordine_nomi = piatto.get("ordine", [])

                for ordine in ordine_nomi:
                    # Convertiamo il nome dell'ordine in maiuscolo
                    ordine_upper = ordine.upper()

                    # Verifica se l'ordine esiste già nel DB (usando il nome già in maiuscolo)
                    result_ordine = session.run(
                        """
                        USE pizzadb
                        MATCH (o:Ordine)
                        WHERE o.nome = $ordine
                        RETURN o
                        """,
                        ordine=ordine_upper
                    )

                    if result_ordine.single() is None:
                        # Se l'ordine non esiste, lo crea con il nome in maiuscolo
                        session.run(
                            """
                            USE pizzadb
                            CREATE (o:Ordine {nome: $ordine})
                            """,
                            ordine=ordine_upper
                        )
                        print(f"Ordine '{ordine_upper}' aggiunto al DB.")

                    # Collega il piatto all'ordine, facendo il match con i nomi in maiuscolo
                    session.run(
                        """
                        USE pizzadb
                        MATCH (p:Piatto)
                        WHERE p.nome = $piatto_nome
                        MATCH (o:Ordine)
                        WHERE o.nome = $ordine
                        MERGE (p)-[:APPARTIENE_A_ORDINE]->(o)
                        """,
                        piatto_nome=piatto_nome,
                        ordine=ordine_upper
                    )
                    print(f"Collegato piatto '{piatto_nome}' all'ordine '{ordine_upper}'.")

    print("Tutte le relazioni tra piatti e ordini sono state create correttamente.")

def process_json_and_create_relationships2(db_driver, json_path):
    # Legge il JSON da file usando UTF-8
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    techniques_container = data.get("tecniche")
    if techniques_container is None:
        raise ValueError("Il JSON non contiene la chiave 'tecniche'.")

    # Estrae tutti i nomi delle tecniche (in UPPER CASE) per riferimento
    technique_names = extract_techniques_recursively(techniques_container)

    with db_driver.session() as session:
        for tech_name, tech_details, tipologia in iterate_techniques(techniques_container):
            if not tech_name or tech_name.upper() not in technique_names:
                continue

            # Convertiamo in UPPER CASE il nome della tecnica e la tipologia
            tech_name_up = tech_name.upper()
            tipologia_up = tipologia.upper() if tipologia else ""

            # Verifica se la tecnica esiste già nel database (aggiungendo LIMIT 1 per evitare warning)
            result_tech = session.run(
                """
                USE pizzadb
                MATCH (t:Tecnica)
                WHERE toUpper(apoc.text.clean(t.nome)) = toUpper(apoc.text.clean($tech_name))
                RETURN t.tipologia AS tipologia
                LIMIT 1
                """,
                tech_name=tech_name_up
            )
            record = result_tech.single()
            if record is None:
                # La tecnica non esiste: la crea con tipologia
                session.run(
                    """
                    USE pizzadb
                    CREATE (t:Tecnica {nome: $tech_name, tipologia: $tipologia})
                    """,
                    tech_name=tech_name_up,
                    tipologia=tipologia_up
                )
                print(f"Tecnica '{tech_name_up}' con tipologia '{tipologia_up}' aggiunta al DB.")
            else:
                # La tecnica esiste: se la tipologia non è definita o vuota, la aggiorna
                existing_tipologia = record.get("tipologia")
                if existing_tipologia is None or existing_tipologia.strip() == "":
                    session.run(
                        """
                        USE pizzadb
                        MATCH (t:Tecnica)
                        WHERE toUpper(apoc.text.clean(t.nome)) = toUpper(apoc.text.clean($tech_name))
                        SET t.tipologia = $tipologia
                        """,
                        tech_name=tech_name_up,
                        tipologia=tipologia_up
                    )
                    print(f"Tecnica '{tech_name_up}' aggiornata con tipologia '{tipologia_up}'.")
                else:
                    print(f"Tecnica '{tech_name_up}' già presente con tipologia '{existing_tipologia}'.")

            # Processa i requisiti della tecnica
            for req in tech_details.get("requisiti", []):
                license_sigla = req.get("sigla")
                livello = req.get("livello")  # il livello letto dal JSON

                if not license_sigla:
                    continue

                # Converte il livello in intero
                livello_int = convert_livello(livello)

                # Verifica che la licenza esista (usando UPPER per uniformità)
                result_license = session.run(
                    """
                    USE pizzadb
                    MATCH (l:Licenza)
                    WHERE toUpper(apoc.text.clean(l.sigla)) = toUpper(apoc.text.clean($license_sigla))
                    RETURN l
                    LIMIT 1
                    """,
                    license_sigla=license_sigla.upper()
                )
                if result_license.single() is None:
                    raise ValueError(f"La licenza con sigla '{license_sigla}' non esiste nel DB pizzadb.")

                # Crea (o MERGE) la relazione tra tecnica e licenza con la proprietà "grado"
                session.run(
                    """
                    USE pizzadb
                    MATCH (t:Tecnica)
                    WHERE toUpper(apoc.text.clean(t.nome)) = toUpper(apoc.text.clean($tech_name))
                      AND toUpper(coalesce(t.tipologia, "")) = toUpper(apoc.text.clean($tipologia))
                    MATCH (l:Licenza)
                    WHERE toUpper(apoc.text.clean(l.sigla)) = toUpper(apoc.text.clean($license_sigla))
                    MERGE (t)-[r:RICHIEDE_LICENZA]->(l)
                    SET r.grado = $grado
                    """,
                    tech_name=tech_name_up,
                    tipologia=tipologia_up,
                    license_sigla=license_sigla.upper(),
                    grado=livello_int
                )
    print("Tutte le relazioni sono state create correttamente.")

def carica_distanze(db_driver, csv_path):
    # Leggi il CSV
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Legge la prima riga (intestazioni colonne)

        # I pianeti sono nelle intestazioni delle colonne, esclusa la prima ("/")
        pianeti = headers[1:]
        distanze = []

        # Leggi i dati delle distanze e converti in numeri (integri)
        for row in reader:
            # Convertiamo i valori in interi, anche se sono stringhe
            distanze.append([int(cell) if cell else 0 for cell in row[1:]])

    # Ora distanze è una matrice numerica
    with db_driver.session() as session:
        for i in range(len(pianeti)):
            for j in range(i, len(pianeti)):  # Creiamo solo una relazione per ogni coppia (i,j)

                pianeta1 = pianeti[i].upper()
                pianeta2 = pianeti[j].upper()

                # Otteniamo la distanza
                distanza = distanze[i][j]
                print(f"Distanza tra {pianeta1} e {pianeta2}: {distanza}")

                # Crea la relazione con attributo distanza
                session.run(
                    """
                    USE pizzadb
                    MATCH (p1:Pianeta {nome: $pianeta1})
                    MATCH (p2:Pianeta {nome: $pianeta2})
                    MERGE (p1)-[r:HA_DISTANZA {distanza: $distanza}]->(p2)
                    """,
                    pianeta1=pianeta1,
                    pianeta2=pianeta2,
                    distanza=distanza
                )

                # Relazione anche nella direzione opposta (perché la distanza è bidirezionale)
                session.run(
                    """
                    USE pizzadb
                    MATCH (p1:Pianeta {nome: $pianeta1})
                    MATCH (p2:Pianeta {nome: $pianeta2})
                    MERGE (p2)-[r:HA_DISTANZA {distanza: $distanza}]->(p1)
                    """,
                    pianeta1=pianeta1,
                    pianeta2=pianeta2,
                    distanza=distanza
                )

        print("Le distanze sono state caricate correttamente nel database.")

def estrai_ristorante_per_pianeta(db_driver, path, create_planet):
    # Carica il JSON dal file
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for ristorante in data:
        print(ristorante['ristorante'])
        print(ristorante)
        for menu in ristorante['menu']:
                print(ristorante['ristorante'])
                print(ristorante['pianeta'])
                nome_ristorante = ristorante['ristorante'].upper()
                nome_pianeta = ristorante['pianeta'].upper()
                crea_ristorante_per_pianeta(db_driver, nome_ristorante, nome_pianeta, create_planet)
    return

def crea_ristorante_per_pianeta(driver, nome_ristorante, nome_pianeta, create_planet):
    try:
        with driver.session() as session:
            result = session.run(create_planet, nome_ristorante=nome_ristorante, nome_pianeta=nome_pianeta)
            return result.single() is not None
    except Exception as e:
        print(f"Errore: {e}")
        return False


def aggiorna_proprieta_legale(driver_db, lista_piatti_non_legali):
    """
    Imposta la proprietà 'legale' a true su tutti i nodi Piatto,
    e poi aggiorna a false i nodi Piatto il cui 'nome' è presente in lista_piatti_non_legali.

    :param driver_db: Istanza del driver Neo4j.
    :param lista_piatti_non_legali: Lista di stringhe con i nomi dei piatti che NON sono legali.
    :return: Tuple con il numero di nodi aggiornati a true e poi il numero di nodi aggiornati a false.
    """
    with driver_db.session() as sessione:
        totale_piatti = sessione.write_transaction(_imposta_legale_true)
        totale_non_legali = sessione.write_transaction(_imposta_legale_false, lista_piatti_non_legali)
        print(
            f"Aggiornati {totale_piatti} piatti a legale = true, di cui {totale_non_legali} rimarcati come non legali (false)")
        return totale_piatti, totale_non_legali


def _imposta_legale_true(transazione):
    query = """
    MATCH (p:Piatto)
    SET p.legale = true
    RETURN count(p) AS totale
    """
    risultato = transazione.run(query)
    record = risultato.single()
    return record["totale"] if record else 0


def _imposta_legale_false(transazione, lista_piatti_non_legali):
    query = """
    MATCH (p:Piatto)
    WHERE p.nome IN $lista_piatti_non_legali
    SET p.legale = false
    RETURN count(p) AS totale
    """
    risultato = transazione.run(query, lista_piatti_non_legali=lista_piatti_non_legali)
    record = risultato.single()
    return record["totale"] if record else 0

def add_operated_relationship(driver_db):
    try:
        with driver_db.session() as session:
            result = session.write_transaction(_create_relationships)
            print(f"Created {result} PUO_ESSERE_OPERATA_CORRETAMENTE_DA relationships.")
    finally:
        driver_db.close()

def _create_relationships(tx):
    query = """
    MATCH (t:Tecnica)-[req:RICHIEDE_LICENZA]->(lic:Licenza)
    MATCH (c:Chef)-[has:HA_LICENZA]->(lic)
    WHERE toInteger(has.grado) >= toInteger(req.grado)
    MERGE (t)-[:PUO_ESSERE_OPERATA_CORRETAMENTE_DA]->(c)
    RETURN count(*) AS count
    """
    result = tx.run(query)
    record = result.single()
    return record["count"] if record else 0