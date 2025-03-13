from openai import OpenAI
from docx import Document
import statistics
import shutil
import fitz
import unicodedata
import jellyfish
import os
import json
import math
from collections import Counter

def docx_to_markdown(docx_path, md_path):
    """
    Converte un file .docx in .md, assegnando i livelli in base alla struttura gerarchica dei capitoli.

    Args:
        docx_path (str): Il percorso del file .docx da convertire.
        md_path (str): Il percorso del file .md di output.

    Returns:
        str: Il contenuto del file Markdown generato.
    """
    doc = Document(docx_path)
    md_text = ""

    for para in doc.paragraphs:
        # Estrai il testo e rimuovi eventuali spazi vuoti
        text = para.text.strip()

        # Salta i paragrafi vuoti
        if not text:
            continue

        # Gestione dei titoli numerati (Capitolo, Sottocapitolo, ecc.)
        if text[0].isdigit():
            # Trova il livello di heading in base ai punti (es. "1.", "1.1", "1.1.1")
            level = text.count(".") + 1
            md_text += f"{'#' * level} {text}\n\n"

        # Liste puntate (esempio: testo che inizia con un "-")
        elif text.startswith("-"):
            md_text += f"- {text}\n"

        # Liste numerate (esempio: testo che inizia con un numero seguito da un punto)
        elif text[0].isdigit() and text[1] == ".":
            md_text += f"1. {text}\n"

        # Paragrafi normali (testo non strutturato)
        else:
            md_text += f"{text}\n\n"

    # Salva il contenuto Markdown nel file
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"✅ Conversione completata: {md_path}")

    return md_text

def extract_section(text, start_section, end_section):
    """
    Estrae una sezione di testo delimitata da due intestazioni.

    Args:
        text (str): Il testo completo da cui estrarre la sezione.
        start_section (str): L'intestazione di inizio della sezione.
        end_section (str): L'intestazione di fine della sezione.

    Returns:
        str: La sezione di testo estratta, senza le intestazioni, oppure una stringa vuota se la sezione non viene trovata.
    """
    pattern = rf"#\s*{start_section}(.*?)(?=#\s*{end_section}|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def transform_path(original_path: str, new_extension: str):
    """
    Trasforma un percorso di file sostituendo 'original data' con 'processed data' e cambiando l'estensione del file.

    Args:
        original_path (str): Il percorso originale del file.
        new_extension (str): La nuova estensione da assegnare al file.

    Returns:
        str: Il nuovo percorso del file con 'processed data' e la nuova estensione.
    """

    # Verifica che la stringa 'original data' sia nel percorso
    if "original data" not in original_path:
        raise ValueError("Il percorso non contiene 'original data'.")

    # Crea il nuovo percorso sostituendo 'original data' con 'processed data'
    new_path = original_path.replace("original data", "processed data")

    # Separa il percorso in nome del file e estensione
    file_name, file_extension = os.path.splitext(new_path)

    # Cambia l'estensione in base al parametro passato
    new_path = file_name + "." + new_extension

    # Estrai la cartella del nuovo percorso
    new_dir = os.path.dirname(new_path)

    # Usa os.path.normpath() per correggere i separatori di percorso
    new_dir = os.path.normpath(new_dir)  # Normalizza il percorso

    # Crea la cartella se non esiste
    os.makedirs(new_dir, exist_ok=True)

    return new_path

def transform_path2(original_path: str):
    """
    Sostituisce 'original data' con 'processed data' nel path e crea la cartella se non esiste.

    Args:
        original_path (str): Il percorso originale del file.

    Returns:
        str: Il nuovo percorso del file con 'processed data'.
    """

    # Verifica che la stringa 'original data' sia nel percorso
    if "original data" not in original_path:
        raise ValueError("Il percorso non contiene 'original data'.")

    # Crea il nuovo percorso sostituendo 'original data' con 'processed data'
    new_path = original_path.replace("original data", "processed data")

    # Estrai la cartella del nuovo percorso
    new_dir = os.path.dirname(new_path)

    # Usa os.path.normpath() per correggere i separatori di percorso
    new_dir = os.path.normpath(new_dir)  # Normalizza il percorso

    # Crea la cartella se non esiste
    os.makedirs(new_dir, exist_ok=True)

    return new_path

def extract_info(json_path, prompt, suffix, model):
    """
    Estrae informazioni chiave da un menù utilizzando l'API di OpenAI e salva il risultato in un file JSON.

    Args:
        json_path (str): Il percorso del file JSON di input.
        prompt (str): Il prompt da inviare all'API di OpenAI.
        suffix (str): Il suffisso da aggiungere al nome del file di output.

    Raises:
        RuntimeError: Se si verifica un errore durante la chiamata all'API OpenAI.
    """

    # Inizializza il client OpenAI con la chiave API
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "Sei un critico culinario esperto. Estrai, senza aggiungere commenti, le informazioni chiave da un menù delimitato da [START_TEXT] e [END_TEXT] e restituisci un JSON con la struttura richiesta."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        cleaned_response = clean_response(response)
        cleaned_response_dict = convert_to_dict(cleaned_response)

        path_json = add_suffix_to_filename(json_path, suffix)

        save_json_to_file(cleaned_response_dict, path_json)

    except Exception as e:
        raise RuntimeError(f"Errore durante la chiamata all'API OpenAI: {e}")

    return path_json

def clean_response(response):
    """
    Pulisce la risposta dell'API OpenAI rimuovendo i delimitatori di codice JSON.

    Args:
        response (object): La risposta dell'API OpenAI contenente il contenuto del messaggio.

    Returns:
        str: La risposta pulita senza i delimitatori di codice JSON.
    """
    cleaned_response = response.choices[0].message.content
    return re.sub(r"^```json\n|\n```$", "", cleaned_response.strip())

def convert_to_dict(json_string: str):
    """
    Converte una stringa JSON in un dizionario Python.

    Args:
        json_string (str): La stringa JSON da convertire.

    Returns:
        dict: Il dizionario Python risultante dalla conversione, oppure None se si verifica un errore di decodifica JSON.
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(e)
        return None

def add_suffix_to_filename(file_path: str, suffix: str) -> str:
    """
    Aggiunge un suffisso al nome di un file prima dell'estensione.

    Args:
        file_path (str): Il percorso completo del file.
        suffix (str): Il suffisso da aggiungere al nome del file.

    Returns:
        str: Il percorso completo del file con il suffisso aggiunto.
    """
    dir_name, base_name = os.path.split(file_path)  # Divide il percorso in directory e nome file
    name, ext = os.path.splitext(base_name)  # Divide il nome del file dall'estensione
    new_file_name = f"{name}{suffix}{ext}"  # Aggiunge il suffisso prima dell'estensione
    return os.path.join(dir_name, new_file_name)  # Ricompone il percorso completo

def convert_pdfs_to_html_with_size(input_path: str, output_path: str, threshold: float = 10.0,
                                   size_threshold: float = 14.0):
    """
    Converte tutti i PDF in una directory in file HTML, preservando il testo e applicando
    una formattazione che ingrandisce le sezioni di testo in base alla dimensione originale.

    Per ogni span di testo nel PDF:
      - Se la dimensione del font è maggiore o uguale a size_threshold, lo span viene visualizzato
        con il font-size corrispondente (e in grassetto).
      - Altrimenti, il testo viene visualizzato con il font-size originale.

    Quando si passa da una pagina all'altra, se la coordinata x0 del primo blocco della nuova pagina
    è diversa da quella dell'ultimo blocco della pagina precedente, viene inserita una separazione (con <br>).

    Args:
        input_path (str): La directory contenente i file PDF.
        output_path (str): La directory dove salvare i file HTML.
        threshold (float, optional): La soglia (in punti) per il gap verticale tra le linee (default: 10.0).
        size_threshold (float, optional): La soglia oltre la quale il testo viene considerato "grande" (default: 14.0).
    """
    import os, fitz

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input directory '{input_path}' does not exist.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            # Inizializza il contenuto HTML con il doctype e i tag base
            html_content = (
                "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n"
                f"<title>{file_name}</title>\n</head>\n<body>\n"
            )
            previous_last_x0 = None  # x0 dell'ultimo blocco della pagina precedente
            previous_y1 = None  # y1 della linea precedente (per il gap verticale)

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    page_dict = page.get_text("dict")
                    blocks = page_dict.get("blocks", [])

                    if not blocks:
                        print(f"Warning: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    # Ordina i blocchi in base alla coordinata y (dall'alto verso il basso)
                    blocks.sort(key=lambda b: b["bbox"][1])
                    current_first_x0 = blocks[0]["bbox"][0] if blocks else None
                    current_last_x0 = blocks[-1]["bbox"][0] if blocks else None

                    # Se la nuova pagina inizia con un x0 diverso, inserisce una separazione
                    if page_num > 0 and previous_last_x0 is not None and current_first_x0 is not None:
                        if current_first_x0 != previous_last_x0:
                            html_content += "<br><br>\n"

                    # Processa i blocchi della pagina
                    for block in blocks:
                        for line in block.get("lines", []):
                            line_html = ""
                            # Inserisce un'interruzione se c'è un gap verticale significativo
                            if previous_y1 is not None and (line["bbox"][1] - previous_y1) > threshold:
                                html_content += "<br>\n"
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                font_size = span.get("size", 12)
                                if text:
                                    if font_size >= size_threshold:
                                        # Per testo "grande": applica lo stile con il font-size e in grassetto
                                        line_html += (
                                            f'<span style="font-size:{font_size}px; font-weight:bold;">'
                                            f'{text}</span> '
                                        )
                                    else:
                                        line_html += f'<span style="font-size:{font_size}px;">{text}</span> '
                            if line_html.strip():
                                html_content += line_html.strip() + "<br>\n"
                                previous_y1 = line["bbox"][3]

                    previous_last_x0 = current_last_x0
                    print(f"Finished processing page {page_num + 1} of '{file_name}'")

            html_content += "</body>\n</html>"
            html_file_name = os.path.splitext(file_name)[0] + ".html"
            html_path = os.path.join(output_path, html_file_name)
            with open(html_path, "w", encoding="utf-8") as html_file:
                html_file.write(html_content)
            print(f"File '{file_name}' converted successfully to '{html_file_name}'.")

    print(f"Conversion completed. HTML files saved in '{output_path}'.")

def process_all_html_files(input_dir: str, output_base_dir: str):
    """
    Cerca tutti i file .html in 'input_dir' e, per ciascuno:
      1) Crea (se non esiste) la cartella "Ristoranti" all'interno di 'output_base_dir'.
      2) All'interno della cartella "Ristoranti", crea una sottocartella con lo stesso nome del file HTML (senza estensione).
      3) Richiama la funzione process_html_and_create_dish_files, passando il percorso del file HTML
         e il percorso della sottocartella appena creata.

    Args:
        input_dir (str): Directory in cui cercare i file HTML.
        output_base_dir (str): Directory base in cui verrà creata la cartella "Ristoranti" e le relative sottocartelle.
    """

    # Crea la cartella "Ristoranti" se non esiste
    ristoranti_folder = os.path.join(output_base_dir, "Ristoranti")
    if not os.path.exists(ristoranti_folder):
        os.makedirs(ristoranti_folder)

    # Itera su tutti i file in input_dir
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".html"):
            html_path = os.path.join(input_dir, file_name)
            # Rimuove l'estensione per ottenere il nome della sottocartella
            folder_name, _ = os.path.splitext(file_name)
            output_folder = os.path.join(ristoranti_folder, folder_name)

            # Crea la sottocartella se non esiste
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            print(f"Elaborazione del file: {html_path}")
            print(f"Output: {output_folder}")

            # Richiama la funzione process_html_and_create_dish_files per questo file HTML
            process_html_and_create_dish_files2(html_path, output_folder)





def find_html_files_with_large_ingredient(directory: str) -> list:
    """
    Scansiona tutti i file HTML nella cartella 'directory' e, per ciascuno:
      1) Estrae tutti i tag <span> con uno stile contenente 'font-size'.
      2) Calcola la mediana dei font-size trovati.
      3) Cerca la parola "ingredient" (case-insensitive) all'interno dei <span>.
      4) Se almeno una occorrenza di "ingredient" appare in un <span> il cui font-size
         è almeno il 20% maggiore della mediana (ossia, >= 1.2 * mediana),
         il file viene considerato "positivo" e il suo nome viene salvato.

    Ritorna la lista dei nomi dei file HTML che soddisfano il criterio.
    """
    matching_files = []

    # Itera su tutti i file della directory
    for file_name in os.listdir(directory):
        if file_name.lower().endswith(('.html', '.htm')):
            file_path = os.path.join(directory, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            spans = soup.find_all("span")
            font_sizes = []

            # Estrae i font-size dai tag <span> (se specificato nello style)
            for span in spans:
                style = span.get("style", "")
                match = re.search(r'font-size:\s*([\d.]+)px', style)
                if match:
                    try:
                        fs = float(match.group(1))
                        font_sizes.append(fs)
                    except ValueError:
                        continue

            # Se non troviamo font-size, passiamo al file successivo
            if not font_sizes:
                continue

            # Calcola la mediana dei font-size
            median_font_size = statistics.median(font_sizes)
            found_large_ingredient = False

            # Cerca la parola "ingredient" in ogni <span>
            for span in spans:
                text = span.get_text()
                if re.search(r'ingredient', text, flags=re.IGNORECASE):
                    style = span.get("style", "")
                    match = re.search(r'font-size:\s*([\d.]+)px', style)
                    if match:
                        try:
                            fs = float(match.group(1))
                        except ValueError:
                            continue
                        # Definiamo "grande" un font-size almeno 20% superiore alla mediana
                        if fs >= 1.2 * median_font_size:
                            found_large_ingredient = True
                            break

            # Se abbiamo trovato "ingredient" con font grande, aggiungiamo il file alla lista
            if found_large_ingredient:
                matching_files.append(file_name)

    matching_files = [x.split(".html")[0] for x in matching_files]
    return matching_files

def organize_folders(source_path: str, target_names: list):
    """
    Cerca, nella cartella source_path, le sottocartelle che hanno il nome uguale a un elemento di target_names.
    Le cartelle il cui nome corrisponde vengono spostate nella cartella "Menu non discorsivi" (che si trova
    nel path superiore a source_path). Le altre sottocartelle vengono spostate in "Menu discorsivi".
    Se le cartelle di destinazione non esistono, vengono create.

    Args:
        source_path (str): il percorso della cartella in cui cercare le sottocartelle.
        target_names (list): lista di nomi (stringhe) da cercare.

    Returns:
        None
    """
    # Otteniamo il path del livello superiore rispetto a source_path
    parent_path = os.path.dirname(source_path)

    # Definiamo i path di destinazione
    non_discorsivi_path = os.path.join(parent_path, "Menu non discorsivi")
    discorsivi_path = os.path.join(parent_path, "Menu discorsivi")

    # Creiamo le cartelle di destinazione se non esistono
    os.makedirs(non_discorsivi_path, exist_ok=True)
    os.makedirs(discorsivi_path, exist_ok=True)

    # Iteriamo su tutti gli elementi presenti in source_path
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)
        # Consideriamo solo le sottocartelle
        if os.path.isdir(item_path):
            # Se il nome della cartella è nella lista target_names, la spostiamo in "Menu non discorsivi"
            if item in target_names:
                destination = os.path.join(non_discorsivi_path, item)
            else:
                destination = os.path.join(discorsivi_path, item)
            # Spostiamo la cartella
            shutil.move(item_path, destination)
            print(f"Spostata '{item}' in '{destination}'.")

    return discorsivi_path, non_discorsivi_path


def move_files_by_suffix(source_path: str, destination_path: str, suffix: str):
    """
    Cerca i file in source_path (anche nelle sottocartelle) che terminano con la stringa 'suffix' (senza considerare l'estensione).
    Se il file non è già in destination_path, lo sposta lì.

    Args:
        source_path (str): Percorso della cartella sorgente.
        destination_path (str): Percorso della cartella di destinazione.
        suffix (str): Stringa con cui devono terminare i nomi dei file (esclusa l'estensione).

    Returns:
        None
    """
    # Crea la cartella di destinazione se non esiste
    os.makedirs(destination_path, exist_ok=True)

    # Scansiona ricorsivamente tutti i file nella cartella sorgente
    for root, _, files in os.walk(source_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Estrarre nome file senza estensione
            name, _ = os.path.splitext(file_name)

            # Controlla se il nome termina con il suffisso specificato
            if name.endswith(suffix):
                # Percorso di destinazione
                new_path = os.path.join(destination_path, file_name)

                # Se il file NON è già in destination_path, spostalo
                if os.path.abspath(root) != os.path.abspath(destination_path):
                    shutil.move(file_path, new_path)
                    print(f"Spostato: {file_name} → {destination_path}")



###
def pdf_to_markdown(pdf_path, md_path):
    """Converte un file .pdf in .md, assegnando i livelli in base alla struttura gerarchica dei capitoli."""
    doc = fitz.open(pdf_path)
    md_text = ""
    print("OK")
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")

        for block in blocks:
            text = block[4].strip()

            if not text:
                continue

            # Identifica capitoli con la dicitura "Capitolo n"
            match = re.match(r"Capitolo (\d+)", text, re.IGNORECASE)
            if match:
                md_text += f"# {text}\n\n"
                continue  # Passa al prossimo blocco senza elaborare ulteriormente il testo

            # Liste puntate
            elif text.startswith("-"):
                md_text += f"{text}\n"
            # Liste numerate
            elif re.match(r'^\d+\.\s', text):
                md_text += f"{text}\n"
            # Paragrafi normali
            else:
                md_text += f"{text}\n\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"✅ Conversione completata: {md_path}")

    return md_text





def transform_path3(original_path: str, new_extension: str):
    """Sostituisce 'original data' con 'processed data' nel path e crea la cartella se non esiste."""

    # Separa il percorso in nome del file e estensione
    file_name, file_extension = os.path.splitext(original_path)

    # Cambia l'estensione in base al parametro passato
    new_path = file_name + "." + new_extension

    # Usa os.path.normpath() per correggere i separatori di percorso
    new_dir = os.path.normpath(new_path)  # Normalizza il percorso

    return new_path




def clean_text(text):
    # Rimuove i newline (\n) e sostituisce con uno spazio
    cleaned_text = text.replace("\n", " ")

    # Rimuove i backslash usati per l'escaping di virgolette e apostrofi
    cleaned_text = cleaned_text.replace(r"\"", "\"").replace(r"\'", "'")

    # Rimuove spazi multipli creati dalla rimozione dei newline
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text




def save_json_to_file(data, file_path: str):
    """
    Salva un dizionario JSON in un file con indentazione leggibile.
    :param data: Il dizionario JSON da salvare
    :param file_path: Il percorso del file di destinazione
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        raise RuntimeError(f"Errore durante il salvataggio del file JSON: {e}")





def parse_menu_text_to_json(text: str) -> list:
    """
    Converte un testo di menu in una lista di dizionari JSON,
    dove il primo elemento di ogni blocco è il nome del piatto e gli altri sono le tecniche di cottura.

    :param text: Testo contenente i piatti e le tecniche di cottura, separati da newline.
    :return: Lista di dizionari con "nome_piatto" e "nomi_tecniche".
    """
    dishes = []
    blocks = text.strip().split("\n\n")  # Divide i piatti separati da doppio newline

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if lines:
            dish_name = lines[0]  # Il primo elemento è il nome del piatto
            techniques = lines[1:]  # Tutti gli altri sono tecniche di cottura

            dishes.append({
                "nome_piatto": dish_name,
                "nomi_tecniche": techniques
            })

    return dishes




def format_menu_text(text: str) -> str:
    """
    Applica delle regole di formattazione al testo:
      - Inserisce spaziatura extra attorno alle intestazioni note (Menu, Ingredienti, Tecniche).
      - Inserisce una riga vuota prima e dopo le righe che sembrano essere titoli di piatti.

    Nota: Le regole possono essere raffinate in base al formato specifico dei tuoi PDF.
    """
    # Aggiungi newline extra attorno a intestazioni note
    for keyword in ["Menu", "Ingredienti", "Tecniche"]:
        # Sostituisce la parola chiave assicurandosi che sia su una linea isolata
        text = re.sub(rf"\s*{keyword}\s*", f"\n{keyword}\n", text)

    # Aggiungi una riga vuota prima e dopo potenziali titoli di piatti.
    # Supponiamo che un titolo di piatto sia una linea breve che inizia con una lettera maiuscola e non contenga ":".
    # Questa regola va raffinata in base ai tuoi casi specifici.
    def aggiungi_spazio(match):
        return f"\n\n{match.group(1).strip()}\n\n"

    # Questo pattern cerca linee che iniziano con una lettera maiuscola e contengono al massimo 5-6 parole
    # (questo per evitare di intervenire su paragrafi lunghi)
    pattern = re.compile(r"(?m)^(?:\s*)([A-Z][\w\s'\"-]{0,60})(?=\n)")
    text = pattern.sub(aggiungi_spazio, text)

    # Rimuovi eventuali spazi extra multipli
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def convert_pdfs_to_markdown(input_path: str, output_path: str):
    """
    Converte tutti i PDF in una directory in file Markdown, preservando solo il testo originale
    e segnalando la presenza di icone o immagini con un placeholder.

    :param input_path: Percorso della cartella contenente i PDF.
    :param output_path: Percorso della cartella in cui salvare i Markdown.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La directory di input '{input_path}' non esiste.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)

            with fitz.open(pdf_path) as pdf_document:
                markdown_content = ""

                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]

                    # Estrai il testo senza modifiche
                    markdown_content += page.get_text("text") + "\n\n"

            markdown_content = format_menu_text(markdown_content)

            # Salvataggio del test
            markdown_file_name = os.path.splitext(file_name)[0] + ".txt"
            markdown_path = os.path.join(output_path, markdown_file_name)

            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)

    print(f"Conversione completata. File markdown salvati in '{output_path}'.")


def convert_pdfs_to_markdown2(input_path: str, output_path: str, threshold: float = 10.0):
    """
    Converte tutti i PDF in una directory in file Markdown, preservando il testo originale
    e cercando di ricostruire la formattazione visiva (interlinee e separazione di sezioni)
    sfruttando i blocchi di testo del PDF.

    Il parametro 'threshold' indica la soglia (in unità del PDF, solitamente punti)
    oltre la quale si considera che esista uno spazio verticale significativo tra due blocchi.

    :param input_path: Percorso della cartella contenente i PDF.
    :param output_path: Percorso della cartella in cui salvare i file Markdown.
    :param threshold: Soglia per determinare l'inserimento di newline extra.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La directory di input '{input_path}' non esiste.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            markdown_content = ""

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    blocks = page.get_text("blocks")

                    if not blocks:  # Se non ci sono blocchi, salta questa pagina
                        print(f"Attenzione: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    # Stampa il primo blocco per capire la struttura
                    print(f"Blocco 0: {blocks[0]}")  # Aggiungi una stampa dei blocchi

                    # Ordinamento dei blocchi per coordinata verticale
                    blocks.sort(key=lambda b: b[1])

                    previous_y1 = None
                    for block in blocks:
                        # Stampa il tipo di ogni blocco per vedere come gestirlo
                        print(f"Blocco: {block}")

                        # Controlliamo la struttura di ogni blocco
                        if len(block) == 6:
                            x0, y0, x1, y1, block_text, _ = block
                        elif len(block) == 5:  # Alcuni blocchi potrebbero avere una struttura diversa
                            x0, y0, x1, y1, block_text = block
                        else:
                            continue  # Ignoriamo eventuali blocchi con un numero di elementi imprevisto

                        # Verifica del gap tra i blocchi
                        if previous_y1 is not None and (y0 - previous_y1) > threshold:
                            markdown_content += "\n\n"
                        # Aggiungi il testo del blocco
                        markdown_content += block_text.strip() + "\n"
                        previous_y1 = y1

                    # Separazione tra le pagine
                    markdown_content += "\n\n"

            # Salvataggio del file (usa l'estensione .txt oppure .md in base alle preferenze)
            markdown_file_name = os.path.splitext(file_name)[0] + ".txt"
            markdown_path = os.path.join(output_path, markdown_file_name)
            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)

    print(f"Conversione completata. File markdown salvati in '{output_path}'.")


def convert_pdfs_to_markdown3(input_path: str, output_path: str, threshold: float = 10.0):
    """
    Converte tutti i PDF in una directory in file Markdown, preservando il testo originale
    e cercando di ricostruire la formattazione visiva (interlinee e separazione di sezioni)
    sfruttando i blocchi di testo del PDF.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La directory di input '{input_path}' non esiste.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            markdown_content = ""
            previous_y1 = None
            previous_page = -1  # Variabile per tenere traccia della pagina precedente

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    blocks = page.get_text("blocks")

                    if not blocks:  # Se non ci sono blocchi, salta questa pagina
                        print(f"Attenzione: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    # Stampa dei blocchi per una diagnosi
                    print(f"\nDiagnosi dei blocchi sulla pagina {page_num + 1}:")
                    for i, block in enumerate(blocks):
                        print(f"Blocco {i}: {block}")

                    # Ordinamento dei blocchi per coordinata verticale
                    blocks.sort(key=lambda b: b[1])

                    for block in blocks:
                        # Verifica che il blocco abbia almeno 5 elementi (coordinate + testo)
                        if len(block) >= 5:
                            # Estrai il testo dal 5° elemento (indice 4) della tupla
                            block_text = block[4]
                        else:
                            continue  # Ignora i blocchi che non contengono il testo

                        # Aggiungi una stampa del testo grezzo per controllo
                        print(f"Contenuto del blocco: '{block_text}'")  # Print del testo

                        # Verifica del gap tra i blocchi (usato per determinare se aggiungere una nuova riga)
                        if previous_y1 is not None and (block[1] - previous_y1) > threshold:
                            markdown_content += "\n"  # Aggiungi una separazione (due newline) se il gap tra i blocchi è maggiore del threshold

                        # Aggiungi il testo del blocco, sostituendo '\\n' con veri newline per il formato finale
                        if block_text.strip():  # Assicurati che il testo non sia vuoto o solo spazi
                            markdown_content += block_text.replace('\\n',
                                                                   '\n').strip() + "\n"  # Sostituisci '\\n' con vero newline

                        previous_y1 = block[3]  # Salva la coordinata y finale per il prossimo confronto

                    # Separazione tra le pagine: aggiungi solo se non è già stato fatto per la pagina precedente
                    #if previous_page != page_num:
                    #    markdown_content += "\n\n"
                    #previous_page = page_num  # Aggiorna la pagina precedente

            # Aggiunta di un controllo finale per la validità del contenuto
            if not markdown_content.strip():
                print(f"Avviso: Il file '{file_name}' non contiene testo valido da scrivere.")
                continue

            # Salvataggio del file (usa l'estensione .txt oppure .md in base alle preferenze)
            markdown_file_name = os.path.splitext(file_name)[0] + ".txt"
            markdown_path = os.path.join(output_path, markdown_file_name)

            # Scrittura del contenuto nel file
            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)

            print(f"File '{file_name}' convertito con successo.")

    print(f"Conversione completata. File markdown salvati in '{output_path}'.")


def convert_pdfs_to_markdown4(input_path: str, output_path: str, threshold: float = 10.0):
    """
    Converte tutti i PDF in una directory in file Markdown, preservando il testo originale
    e cercando di ricostruire la formattazione visiva (interlinee e separazione di sezioni)
    sfruttando i blocchi di testo del PDF.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La directory di input '{input_path}' non esiste.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            markdown_content = ""
            previous_y1 = None
            previous_x0 = None  # Per tenere traccia della posizione del primo blocco dell'ultima pagina elaborata

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    blocks = page.get_text("blocks")

                    if not blocks:  # Se non ci sono blocchi, salta questa pagina
                        print(f"Attenzione: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    for i, block in enumerate(blocks):
                        print(f"Blocco {i}: {block}")

                    # Ordinamento dei blocchi per coordinata verticale
                    blocks.sort(key=lambda b: b[1])

                    first_block_x0 = blocks[0][0] if blocks else None  # Primo valore x0 della nuova pagina

                    for block in blocks:
                        # Verifica che il blocco abbia almeno 5 elementi (coordinate + testo)
                        if len(block) >= 5:
                            block_text = block[4]  # Estrai il testo
                        else:
                            continue  # Ignora i blocchi che non contengono il testo

                        print(f"Contenuto del blocco: '{block_text}'")  # Print del testo
                        # Se siamo a una nuova pagina e x0 è diverso dall'ultima pagina, aggiungi un newline
                        if page_num > 0 and previous_x0 is not None and first_block_x0 is not None:
                            print(f"Ultimo previous salvato = {previous_x0}")
                            print(f"Attuale blocco 0: {first_block_x0}")
                            if first_block_x0 != previous_x0:
                                markdown_content += "\n"

                        # Verifica del gap tra i blocchi (usato per determinare se aggiungere una nuova riga)
                        if previous_y1 is not None and (block[1] - previous_y1) > threshold:
                            markdown_content += "\n"

                        # Aggiungi il testo del blocco
                        if block_text.strip():
                            markdown_content += block_text.replace('\\n', '\n').strip() + "\n"

                        previous_y1 = block[3]  # Salva la coordinata y finale per il prossimo confronto

                    previous_x0 = first_block_x0  # Aggiorna il primo valore x0 della pagina
                    print(f"Ultimo previous appena salvato = {previous_x0}")

            # Aggiunta di un controllo finale per la validità del contenuto
            if not markdown_content.strip():
                print(f"Avviso: Il file '{file_name}' non contiene testo valido da scrivere.")
                continue

            # Salvataggio del file markdown
            markdown_file_name = os.path.splitext(file_name)[0] + ".txt"
            markdown_path = os.path.join(output_path, markdown_file_name)

            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)

            print(f"File '{file_name}' convertito con successo.")

    print(f"Conversione completata. File markdown salvati in '{output_path}'.")




def convert_pdfs_to_md(input_path: str, output_path: str, threshold: float = 10.0):
    """
    Converte tutti i PDF in una directory in file Markdown, preservando il testo originale
    e ricostruendo la formattazione visiva (interlinee e separazione di sezioni) sfruttando
    i blocchi di testo del PDF.

    Quando si passa da una pagina all'altra, se il valore x0 del primo blocco della nuova pagina
    è diverso dal valore x0 dell'ultimo blocco della pagina precedente, viene inserito un newline.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La directory di input '{input_path}' non esiste.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            markdown_content = ""
            previous_last_x0 = None  # Per tenere traccia del valore x0 dell'ultimo blocco della pagina precedente
            previous_y1 = None

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    blocks = page.get_text("blocks")

                    if not blocks:
                        print(f"Attenzione: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    # Ordinamento dei blocchi per coordinata verticale
                    blocks.sort(key=lambda b: b[1])

                    # Trova il valore x0 del primo blocco della pagina corrente
                    current_first_x0 = blocks[0][0] if blocks else None
                    # Trova il valore x0 dell'ultimo blocco della pagina corrente
                    current_last_x0 = blocks[-1][0] if blocks else None

                    # Se siamo in una pagina successiva, confronta il primo x0 della pagina corrente
                    # con l'ultimo x0 della pagina precedente
                    if page_num > 0 and previous_last_x0 is not None and current_first_x0 is not None:
                        if current_first_x0 != previous_last_x0:
                            markdown_content += "\n"  # Inserisci newline se sono diversi

                    # Ora processa i blocchi della pagina corrente
                    for block in blocks:
                        # Controlla che il blocco contenga almeno 5 elementi
                        if len(block) >= 5:
                            block_text = block[4]
                        else:
                            continue

                        # Debug: stampa il contenuto del blocco
                        print(f"Contenuto del blocco: '{block_text}'")

                        # Se c'è un gap verticale significativo tra il blocco corrente e il precedente, aggiungi un newline
                        if previous_y1 is not None and (block[1] - previous_y1) > threshold:
                            markdown_content += "\n"

                        if block_text.strip():
                            markdown_content += block_text.replace('\\n', '\n').strip() + "\n"

                        previous_y1 = block[3]  # Aggiorna il valore y finale del blocco

                    # Alla fine della pagina, aggiorna il previous_last_x0 con il valore x0 dell'ultimo blocco della pagina corrente
                    previous_last_x0 = current_last_x0
                    print(f"Pagina {page_num + 1} terminata: previous_last_x0 aggiornato a {previous_last_x0}")

            if not markdown_content.strip():
                print(f"Avviso: Il file '{file_name}' non contiene testo valido da scrivere.")
                continue

            markdown_file_name = os.path.splitext(file_name)[0] + ".txt"
            markdown_path = os.path.join(output_path, markdown_file_name)
            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)

            print(f"File '{file_name}' convertito con successo.")

    print(f"Conversione completata. File markdown salvati in '{output_path}'.")


def convert_pdfs_to_txt_with_size(input_path: str, output_path: str, threshold: float = 10.0,
                                  size_threshold: float = 14.0):
    """
    Converte tutti i PDF in una directory in file txt, preservando il testo e una parte
    della formattazione visiva originale.

    Per ogni span di testo nel PDF:
      - Se la dimensione del font è maggiore o uguale a size_threshold, lo span viene preceduto
        dal marker "## " per evidenziare il testo di grande dimensione.
      - In ogni caso, viene riportato (in parentesi) il valore della dimensione,
        così da “vedere” la grandezza originale.

    Durante il passaggio da una pagina all'altra, se la coordinata x0 del primo blocco della nuova
    pagina è diversa da quella dell'ultimo blocco della pagina precedente, viene inserita una nuova riga.

    :param input_path: Directory contenente i file PDF.
    :param output_path: Directory dove salvare i file txt.
    :param threshold: Soglia per il gap verticale (in punti) per inserire una nuova riga (default: 10.0).
    :param size_threshold: Soglia oltre la quale il testo viene considerato “grande” e preceduto da "## " (default: 14.0).
    """
    import os, fitz

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input directory '{input_path}' does not exist.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_name in os.listdir(input_path):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_path, file_name)
            txt_content = ""
            previous_last_x0 = None  # x0 dell'ultimo blocco della pagina precedente
            previous_y1 = None  # y1 della linea precedente (per gap verticale)

            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    # Estrae le informazioni dettagliate (inclusa la dimensione dei caratteri)
                    page_dict = page.get_text("dict")
                    # Per debug: puoi decommentare la print seguente
                    # print(page_dict)
                    blocks = page_dict.get("blocks", [])

                    if not blocks:
                        print(f"Warning: La pagina {page_num + 1} di '{file_name}' è vuota o non contiene testo.")
                        continue

                    # Ordina i blocchi per la coordinata y (cioè dall'alto verso il basso)
                    blocks.sort(key=lambda b: b["bbox"][1])
                    current_first_x0 = blocks[0]["bbox"][0] if blocks else None
                    current_last_x0 = blocks[-1]["bbox"][0] if blocks else None

                    # Se si passa a una nuova pagina con x0 diverso, aggiunge una riga vuota
                    if page_num > 0 and previous_last_x0 is not None and current_first_x0 is not None:
                        if current_first_x0 != previous_last_x0:
                            txt_content += "\n"

                    # Processa ogni blocco della pagina
                    for block in blocks:
                        for line in block.get("lines", []):
                            line_text = ""
                            # Se c'è un gap verticale (superiore a threshold) tra le linee, inserisce una nuova riga
                            if previous_y1 is not None and (line["bbox"][1] - previous_y1) > threshold:
                                txt_content += "\n"

                            # Per ogni linea, processa gli span (cioè le “porzioni” di testo con formattazione omogenea)
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                font_size = span.get("size", 12)  # Valore di default se non presente
                                if text:
                                    # Qui puoi decidere se mostrare o meno il valore numerico della dimensione.
                                    font_info = f" ({font_size}px)"  # opzionale, se vuoi vedere il valore
                                    if font_size >= size_threshold:
                                        # Per testo “grande”: aggiunge il marker "## "
                                        line_text += "## " + text + font_info + " "
                                    else:
                                        line_text += text + font_info + " "
                            if line_text.strip():
                                txt_content += line_text.strip() + "\n"
                                # Aggiorna previous_y1 con la coordinata inferiore (y1) della linea corrente
                                previous_y1 = line["bbox"][3]

                    previous_last_x0 = current_last_x0
                    print(
                        f"Finished processing page {page_num + 1} of '{file_name}': previous_last_x0 updated to {previous_last_x0}")

            if not txt_content.strip():
                print(f"Warning: Il file '{file_name}' non contiene testo valido da scrivere.")
                continue

            txt_file_name = os.path.splitext(file_name)[0] + ".txt"
            txt_path = os.path.join(output_path, txt_file_name)
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(txt_content)

            print(f"File '{file_name}' converted successfully.")

    print(f"Conversion completed. txt files saved in '{output_path}'.")


def process_html_and_create_dish_files(html_path: str, output_dir: str):
    """
    Legge un file HTML e:
      1) Estrae il titolo (dal tag <title>) e ne rimuove l'estensione,
      2) Crea un dizionario in cui:
             - la chiave è la dimensione in pixel (es. 12.0, 15.0, 20.0, …)
             - il valore è la lista dei testi (presi dai tag <span>) con quella dimensione.
      3) Tra le chiavi, il font-size che ha un numero di valori compreso tra 7 e 15
         viene considerato quello dei "piatti".
      4) Utilizzando la “timeline” degli elementi (tag <span> e <br> in ordine),
         per ogni occorrenza (di un <span> con quel font-size) viene creato un file txt.
         In ogni file verrà scritto il testo, rispettando spazi e newline, partendo dal
         titolo del piatto (incluso) fino al titolo del piatto successivo (escluso) o fino
         alla fine del documento.

      Il nome di ciascun file sarà: nome_del_ristorante_nome_del_piatto.txt
      (il nome del ristorante è ricavato dal tag <title> rimuovendo l'estensione).

      Modifica: se due span consecutivi (ignorando eventuali <br> intermedi) hanno lo stesso font-size,
      vengono uniti in un unico titolo (ipotesi: il nome del piatto è lungo e si è spezzato a capo).
      Se invece il gruppo è di più di 2, non viene effettuata la fusione.
    """
    # Legge il contenuto dell'HTML
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # 1) Estrae il titolo e rimuove l'estensione (ad es. ".pdf")
    raw_title = soup.title.text.strip() if soup.title else "Unknown"
    restaurant_name, _ = os.path.splitext(raw_title)

    # 2) Estrae gli elementi dal body mantenendo l'ordine.
    # Cerchiamo sia tag <span> che <br>.
    # Ogni elemento verrà rappresentato come un dizionario:
    #   {"type": "span", "font_size": valore (float), "text": testo} oppure
    #   {"type": "br", "text": "\n"}
    elements = []
    # Usiamo .find_all con recursive=True per ottenere gli elementi in ordine di apparizione
    for elem in soup.body.find_all(["span", "br"], recursive=True):
        if elem.name == "span":
            style = elem.get("style", "")
            # Usa una regex per estrarre il font-size
            match = re.search(r'font-size:\s*([\d.]+)px', style)
            if match:
                try:
                    font_size = float(match.group(1))
                except ValueError:
                    font_size = None
            else:
                font_size = None
            text = elem.get_text(strip=True)
            elements.append({"type": "span", "font_size": font_size, "text": text})
        elif elem.name == "br":
            # Per ogni <br> aggiungiamo un newline
            elements.append({"type": "br", "text": "\n"})

    # 2bis) Costruisce il dizionario: chiave = font_size, valore = lista di testi (da <span>)
    font_dict = {}
    for item in elements:
        if item["type"] == "span" and item["font_size"] is not None:
            fs = item["font_size"]
            font_dict.setdefault(fs, []).append(item["text"])

    # 3) Individua quale chiave (font_size) ha tra 7 e 15 occorrenze (si assume sia quella dei piatti)
    dish_font_sizes = [fs for fs, texts in font_dict.items() if 7 <= len(texts) <= 15]
    if not dish_font_sizes:
        print("Nessun font_size con numero di occorrenze compreso tra 7 e 15 è stato trovato.")
        return
    elif len(dish_font_sizes) > 1:
        # Se ce ne sono più di uno, scegliamo quello con il maggior numero di occorrenze
        dish_font_size = max(dish_font_sizes, key=lambda fs: len(font_dict[fs]))
    else:
        dish_font_size = dish_font_sizes[0]

    print(f"Font size individuato per i piatti: {dish_font_size}px (con {len(font_dict[dish_font_size])} occorrenze)")

    # 4) Individua gli indici in cui compaiono le etichette dei piatti e gestisci la fusione
    # Se due span consecutivi (ignorando i <br>) hanno lo stesso dish_font_size, li uniamo.
    dish_entries = []  # lista di tuple: (indice_in_elements, dish_title)
    i = 0
    while i < len(elements):
        item = elements[i]
        if item["type"] == "span" and item["font_size"] == dish_font_size:
            candidate_indices = [i]
            j = i + 1
            # Scorri gli elementi successivi ignorando eventuali <br>
            while j < len(elements):
                if elements[j]["type"] == "br":
                    j += 1
                elif elements[j]["type"] == "span" and elements[j]["font_size"] == dish_font_size:
                    candidate_indices.append(j)
                    j += 1
                else:
                    break
            if len(candidate_indices) == 2:
                # Se sono esattamente due, li uniamo in un unico titolo e salviamo il merge_count=2
                merged_text = " ".join(elements[k]["text"] for k in candidate_indices)
                # Sovrascrive la seconda parte con stringa vuota per evitare doppioni
                # elements[candidate_indices[1]]["text"] = ""
                elements[candidate_indices[1]]["text"] = None  # Ignora questa parte dopo

                dish_entries.append((candidate_indices[0], merged_text, len(candidate_indices)))
            else:
                # Altrimenti, li aggiungiamo singolarmente (merge_count=1)
                for k in candidate_indices:
                    dish_entries.append((k, elements[k]["text"], 1))
            i = j
        else:
            i += 1

    if not dish_entries:
        print("Nessun piatto individuato nella struttura degli elementi.")
        return

    # Assicuriamoci che gli elementi siano ordinati in base all'indice (lo sono già)
    dish_entries.sort(key=lambda x: x[0])

    # Prepara la directory di output, se non esiste
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 5) Per ogni piatto, crea un file txt con il testo che va dal titolo del piatto
    #    fino al titolo del piatto successivo (escluso) oppure fino alla fine del documento.
    for idx, (start_index, dish_title, merge_count) in enumerate(dish_entries):
        # L'indice finale è il prossimo dish oppure la fine della lista
        end_index = dish_entries[idx + 1][0] if idx + 1 < len(dish_entries) else len(elements)
        # Inizia il contenuto con il titolo fuso (dish_title)
        segment_parts = [dish_title]
        # Aggiunge il resto degli elementi, saltando quelli fusi (merge_count elementi)
        for item in elements[start_index + merge_count:end_index]:
            if item["text"] is None:
                continue  # Evita di aggiungere il testo già fuso

            segment_parts.append(item["text"])
        dish_content = "".join(segment_parts)

        # Costruiamo il nome del file: "nome_del_ristorante_nome_del_piatto.txt"
        # Puliamo eventuali caratteri non ammessi nel nome del file
        safe_restaurant = re.sub(r'[\\/*?:"<>|]', "", restaurant_name).strip()
        safe_dish = re.sub(r'[\\/*?:"<>|]', "", dish_title).strip()
        file_name = f"{safe_restaurant}_{safe_dish}.txt"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as outf:
            outf.write(dish_content)

        print(f"Creato file: {file_name}")

    print("Elaborazione completata.")
from bs4 import BeautifulSoup, NavigableString

def process_html_and_create_dish_files2(html_path: str, output_dir: str):
    """
    Legge un file HTML e:
      1) Estrae il titolo (dal tag <title>) e ne rimuove l'estensione,
      2) Crea una timeline degli elementi (nodi di testo, <span> e <br>) in ordine,
         in modo da preservare gli spazi presenti tra i tag.
      3) Costruisce un dizionario in cui:
             - la chiave è la dimensione in pixel (es. 10.0, 12.0, …)
             - il valore è la lista dei testi (dal tag <span>) con quella dimensione.
         Tra le chiavi, quella con un numero di occorrenze compreso tra 7 e 15 viene
         considerata quella dei "piatti".
      4) Utilizzando la timeline degli elementi, per ogni occorrenza (di un <span> con
         quel font-size) viene creato un file txt che contiene il testo (con spazi e newline)
         a partire dal titolo del piatto (incluso) fino al titolo del piatto successivo (escluso)
         o fino alla fine del documento.
         Se due <span> consecutivi (ignorando eventuali <br> e nodi di testo composti solo da spazi)
         hanno lo stesso font-size, vengono uniti (se esattamente due, altrimenti non si uniscono).
      5) Il nome di ciascun file sarà: nome_del_ristorante_nome_del_piatto.txt
         (il nome del ristorante è ricavato dal tag <title> rimuovendo l'estensione).
    """

    # Legge il contenuto dell'HTML
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")

    # 1) Estrae il titolo e rimuove l'estensione (es. ".pdf")
    raw_title = soup.title.text.strip() if soup.title else "Unknown"
    restaurant_name, _ = os.path.splitext(raw_title)

    # 2) Estrae gli elementi dal body mantenendo l'ordine.
    # Utilizziamo recursiveChildGenerator per catturare anche i nodi di testo.
    elements = []
    for node in soup.body.recursiveChildGenerator():
        if isinstance(node, NavigableString):
            # Se il nodo di testo appartiene ad un <span>, lo ignoro perché il tag <span>
            # verrà già processato; altrimenti lo aggiungo così com'è (per preservare spazi e punteggiatura)
            if node.parent and node.parent.name == "span":
                continue
            text = str(node)
            elements.append({"type": "text", "text": text})
        elif node.name == "span":
            style = node.get("style", "")
            match = re.search(r'font-size:\s*([\d.]+)px', style)
            if match:
                try:
                    font_size = float(match.group(1))
                except ValueError:
                    font_size = None
            else:
                font_size = None
            # Non usiamo strip() per preservare eventuali spazi iniziali/finali
            text = node.get_text()
            elements.append({"type": "span", "font_size": font_size, "text": text})
        elif node.name == "br":
            elements.append({"type": "br", "text": "\n"})

    # 2bis) Costruisce il dizionario: chiave = font_size, valore = lista di testi (dal tag <span>)
    font_dict = {}
    for item in elements:
        if item["type"] == "span" and item.get("font_size") is not None:
            fs = item["font_size"]
            font_dict.setdefault(fs, []).append(item["text"])

    # 3) Individua quale font-size ha tra 7 e 15 occorrenze (si assume sia quello dei piatti)
    dish_font_sizes = [fs for fs, texts in font_dict.items() if 7 <= len(texts) <= 15]
    if not dish_font_sizes:
        print("Nessun font_size con numero di occorrenze compreso tra 7 e 15 è stato trovato.")
        return
    elif len(dish_font_sizes) > 1:
        dish_font_size = max(dish_font_sizes, key=lambda fs: len(font_dict[fs]))
    else:
        dish_font_size = dish_font_sizes[0]

    print(f"Font size individuato per i piatti: {dish_font_size}px (con {len(font_dict[dish_font_size])} occorrenze)")

    # 4) Individua gli indici in cui compaiono le etichette dei piatti e gestisce la fusione.
    # Ignora i nodi di tipo "br" e i nodi di tipo "text" composti solo da spazi.
    dish_entries = []  # lista di tuple: (indice_in_elements, dish_title, merge_count)
    i = 0
    while i < len(elements):
        item = elements[i]
        if item["type"] == "span" and item.get("font_size") == dish_font_size:
            candidate_indices = [i]
            j = i + 1
            while j < len(elements):
                # Salta nodi di tipo "br" o nodi di testo che, dopo strip, risultano vuoti
                if elements[j]["type"] == "br" or (elements[j]["type"] == "text" and elements[j]["text"].strip() == ""):
                    j += 1
                elif elements[j]["type"] == "span" and elements[j].get("font_size") == dish_font_size:
                    candidate_indices.append(j)
                    j += 1
                else:
                    break
            if len(candidate_indices) == 2:
                # Se sono esattamente due, li uniamo (inserendo uno spazio tra i testi)
                merged_text = " ".join(elements[k]["text"] for k in candidate_indices)
                # Imposta la seconda occorrenza come None per evitare duplicati
                elements[candidate_indices[1]]["text"] = None
                dish_entries.append((candidate_indices[0], merged_text, len(candidate_indices)))
            else:
                for k in candidate_indices:
                    dish_entries.append((k, elements[k]["text"], 1))
            i = j
        else:
            i += 1

    if not dish_entries:
        print("Nessun piatto individuato nella struttura degli elementi.")
        return

    # Ordina i dish_entries in base all'indice di apparizione
    dish_entries.sort(key=lambda x: x[0])

    # 5) Per ogni piatto, crea un file txt con il testo che va dal titolo del piatto fino al titolo del piatto successivo
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, (start_index, dish_title, merge_count) in enumerate(dish_entries):
        end_index = dish_entries[idx + 1][0] if idx + 1 < len(dish_entries) else len(elements)
        segment_parts = [dish_title]
        for item in elements[start_index + merge_count:end_index]:
            if item["text"] is None:
                continue
            segment_parts.append(item["text"])
        # Utilizziamo join senza aggiungere spazi artificiali, così si preservano gli spazi già presenti
        dish_content = "".join(segment_parts)

        # Elimina br multipli
        dish_content = re.sub(r'\n{3,}', '\n\n\n', dish_content)

        safe_restaurant = re.sub(r'[\\/*?:"<>|]', "", restaurant_name).strip()
        safe_dish = re.sub(r'[\\/*?:"<>|]', "", dish_title).strip()
        file_name = f"{safe_restaurant}_{safe_dish}.txt"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as outf:
            outf.write(dish_content)
        print(f"Creato file: {file_name}")

    print("Elaborazione completata.")

def find_txt_files(path: str):
    # Verifica se il percorso è valido
    if not os.path.isdir(path):
        raise ValueError(f"{path} non è una directory valida.")

    # Lista per raccogliere i file .txt trovati
    txt_files = []

    # Itera su tutti i file e le cartelle nella directory
    for root, dirs, files in os.walk(path):
        for file in files:
            # Controlla se il file ha estensione .txt
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))

    return txt_files

def get_text_after_menu(text):
    match = re.search(r'(?i)menu\s*\n', text)
    return text[match.end():] if match else ""

def extract_menu(menu_path, prompt_func, suffix):
    # Ottieni solo i file .txt nella cartella specificata (senza esplorare sottocartelle)
    menu_paths = [os.path.join(menu_path, file) for file in os.listdir(menu_path) if file.endswith('.txt')]

    for i, menu in enumerate(menu_paths):
        with open(menu, "r", encoding="utf-8") as file:
            text = file.read()  # Legge tutto il contenuto in una variabile
            print(f"Sto processando il menu {i + 1}/{len(menu_paths)}")
            extract_info(transform_path3(menu, "json"), prompt_func(text), suffix)
            #extract_info(transform_path3(menu, "json"), prompt_func(pf.clean_text(text)), suffix)


def merge_json_files(input_dir: str, outputname: str):
    # Verifica se il percorso è valido
    if not os.path.isdir(input_dir):
        raise ValueError(f"{input_dir} non è una directory valida.")

    # Lista per raccogliere i dati da tutti i file JSON
    merged_data = []

    # Itera su tutti i file nella directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".json"):
            json_path = os.path.join(input_dir, file_name)
            # Leggi il contenuto di ogni file JSON
            with open(json_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                    merged_data.append(data)  # Aggiungi il contenuto del file al risultato
                except json.JSONDecodeError:
                    print(f"Errore nel file {json_path}: non è un JSON valido.")

    # Crea il percorso completo per il file di output
    output_path = os.path.join(input_dir, outputname)
    print(output_path)
    # Scrivi tutti i dati uniti nel file di output
    with open(output_path, 'w', encoding='utf-8') as output_json:
        json.dump(merged_data, output_json, ensure_ascii=False, indent=4)

    print(f"Unione completata. I dati sono stati salvati in {output_path}")







def remove_emoji(text):
    """
    Rimuove i caratteri emoji da una stringa.
    Utilizza la categoria Unicode "So" (Symbol, other).
    """
    return ''.join(c for c in text if not unicodedata.category(c).startswith('So'))


def normalize_piatto(nome):
    """
    Restituisce una versione normalizzata del nome del piatto,
    rimuovendo eventuali emoji e spazi in eccesso, per facilitare il confronto.
    """
    return remove_emoji(nome).strip().lower()


def merge_restaurant_files(info_file, ingredienti_file, tecniche_file):
    """
    Data la tripla di file JSON di un ristorante, restituisce il JSON unito.
    """
    # Carica il JSON delle informazioni di base
    with open(info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)

    # Carica i JSON del menu
    with open(ingredienti_file, 'r', encoding='utf-8') as f:
        lista_ingredienti = json.load(f)

    with open(tecniche_file, 'r', encoding='utf-8') as f:
        lista_tecniche = json.load(f)

    # Crea un dizionario per i piatti, usando come chiave il nome normalizzato
    menu_dict = {}

    # Processa il JSON degli ingredienti
    for piatto in lista_ingredienti:
        print(piatto)
        nome_orig = piatto.get("nome piatto", "").strip()
        key = normalize_piatto(nome_orig)
        menu_dict[key] = {
            "piatto": nome_orig,  # conserva il nome originale (con emoji se presente)
            "ingredienti": piatto.get("nomi ingredienti", []),
            "tecniche": [],  # da integrare
            "ordine": []  # campo vuoto come richiesto
        }

    # Processa il JSON delle tecniche
    for piatto in lista_tecniche:
        nome_tecnica = piatto.get("nome piatto", "").strip()
        key = normalize_piatto(nome_tecnica)
        # Se il piatto è già presente (cioè lo trovata nei ingredienti) lo aggiorniamo
        if key in menu_dict:
            menu_dict[key]["tecniche"] = piatto.get("nomi tecniche", [])
        else:
            # Se il piatto non è presente negli ingredienti, lo aggiungiamo con ingredienti vuoti
            menu_dict[key] = {
                "piatto": nome_tecnica,  # in questo caso il nome non ha emoji
                "ingredienti": [],
                "tecniche": piatto.get("nomi tecniche", []),
                "ordine": []
            }

    # Costruisci la struttura finale per il ristorante
    merged_restaurant = {
        "ristorante": info.get("nome ristorante", ""),
        "chef": info.get("nome chef", ""),
        "pianeta": info.get("nome pianeta", ""),
        "licenze": info.get("licenze", []),
        "menu": list(menu_dict.values())
    }

    return merged_restaurant


def merge_all_restaurants(path):
    """
    Scansiona la directory 'path' e raggruppa i file per ristorante.
    Restituisce una lista contenente il JSON unito per ogni ristorante.
    """
    # Dizionario per raggruppare i file in base al nome del ristorante
    gruppi = {}

    # Filtri per i tipi di file che ci interessano
    tipi_file = ["pianeti_chef_e_licenze", "piatti_e_ingredienti_totali_per_ristorante_updated", "piatti_e_tecniche_totali_per_ristorante_updated"]

    # Scansiona tutti i file nella directory
    for file in os.listdir(path):
        if not file.endswith(".json"):
            continue
        # Il nome del ristorante è la parte iniziale fino al primo "_"
        parts = file.split("_")
        if len(parts) < 2:
            continue  # non rispetta il pattern atteso
        ristorante = parts[0].strip()
        # Determina il tipo di file controllando se contiene uno dei tipi
        for tipo in tipi_file:
            if tipo in file:
                gruppi.setdefault(ristorante, {})[tipo] = os.path.join(path, file)
                break

    # Ora unisci i file per ciascun ristorante
    merged_list = []
    for ristorante, files in gruppi.items():
        # Verifica che i tre file necessari siano presenti
        if all(tipo in files for tipo in tipi_file):
            merged = merge_restaurant_files(
                info_file=files["pianeti_chef_e_licenze"],
                ingredienti_file=files["piatti_e_ingredienti_totali_per_ristorante_updated"],
                tecniche_file=files["piatti_e_tecniche_totali_per_ristorante_updated"]
            )
            merged_list.append(merged)
        else:
            print(f"Attenzione: file mancanti per il ristorante {ristorante}.")

    return merged_list

def extract_emojis(text):
    """
    Estrae le emoji da una stringa e restituisce una tupla (testo senza emoji, lista di emoji).
    """
    emojis = []
    text_without = ""
    for char in text:
        if unicodedata.category(char).startswith('So'):  # Categoria Unicode per simboli (emoticon)
            emojis.append(char)
        else:
            text_without += char
    return text_without.strip(), emojis


def process_emoji_in_menu(merged_results_file):
    """
    Legge il file JSON 'merged_results' (contenente una lista di ristoranti) e applica la regola per separare le emoji.
    """
    # Carica il file JSON
    with open(merged_results_file, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    # Verifica che merged_data sia una lista di ristoranti
    if not isinstance(merged_data, list):
        raise ValueError("Il file JSON deve contenere una lista di ristoranti.")

    # Processa ogni ristorante nella lista
    for ristorante in merged_data:
        menu = ristorante.get("menu", [])

        # Processa ogni piatto nel menu del ristorante
        for piatto in menu:
            nome_piatto = piatto.get("piatto", "")

            # Estrai il nome senza emoji e le emoji
            nome_senza_emoji, emoji_list = extract_emojis(nome_piatto)

            # Se ci sono emoji, metti la lista nel campo 'ordine'
            if emoji_list:
                piatto["piatto"] = nome_senza_emoji  # Rimuovi le emoji dal nome del piatto
                piatto["ordine"] = emoji_list  # Aggiungi le emoji al campo 'ordine'
            else:
                piatto["ordine"] = []  # Se non ci sono emoji, metti un elenco vuoto in 'ordine'

    # Salva il risultato modificato nel file
    with open(merged_results_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

def extract_techniques_recursively(d):
    """
    Naviga ricorsivamente nel JSON delle tecniche e restituisce un set con i nomi delle tecniche (in UPPER CASE).
    Evita di includere chiavi come "requisiti".
    """
    techniques = set()

    for key, value in d.items():
        if isinstance(value, dict):
            if "requisiti" in value:  # Se il dizionario ha "requisiti", allora è una tecnica
                techniques.add(key.upper())
            else:  # Altrimenti, continua a cercare più in profondità
                techniques.update(extract_techniques_recursively(value))

    return techniques


def correct_techniques_in_merged(merged_results_file, techniques_def_file):

    # Carica il JSON delle tecniche
    with open(techniques_def_file, 'r', encoding='utf-8') as f:
        techniques_def = json.load(f)

    # Estrai il set di tecniche valide in UPPER CASE
    try:
        valid_techniques = extract_techniques_recursively(techniques_def["tecniche"])
    except:
        valid_techniques = extract_techniques_recursively(techniques_def)

    print(valid_techniques)
    # Carica il JSON merged (che contiene una lista di ristoranti)
    with open(merged_results_file, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    if not isinstance(merged_data, list):
        raise ValueError("Il file merged_results deve contenere una lista di ristoranti.")

    # Processa ogni ristorante e ogni piatto
    for restaurant in merged_data:
        restaurant_name = restaurant.get("ristorante", "Unknown")
        menu = restaurant.get("menu", [])

        for dish in menu:
            dish_name = dish.get("piatto", "Unknown dish")
            ingredients = dish.get("ingredienti", [])
            techniques = dish.get("tecniche", [])

            # Se un ingrediente corrisponde a una tecnica valida, spostalo in tecniche (se non è già presente)
            for ingredient in ingredients[:]:
                ingredient_upper = ingredient.upper()
                if ingredient_upper in valid_techniques:
                    print(f"[{restaurant_name} - {dish_name}] Ingredient '{ingredient}' is a valid technique. Moving to techniques.")
                    ingredients.remove(ingredient)
                    if not any(t.upper() == ingredient_upper for t in techniques):
                        techniques.append(ingredient)

            # Se una voce in tecniche non è valida, stampa il ristorante, il piatto e la tecnica non trovata
            for tech in techniques[:]:
                tech_upper = tech.upper()
                if tech_upper not in valid_techniques:
                    #print(f"[{restaurant_name} - {dish_name}] WARNING: Technique '{tech}' NOT FOUND in valid techniques!")
                    pass

            # Aggiorna il piatto
            dish["ingredienti"] = ingredients
            dish["tecniche"] = techniques

    merged_results_file2 = increment_version(merged_results_file)

    # Salva il JSON merged aggiornato
    with open(merged_results_file2, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

    return merged_results_file2

# Trova l'ultima versione e incrementa il numero
def increment_version(file_path):
    match = re.search(r"(v\d+)", file_path, re.IGNORECASE)
    if match:
        current_version = int(match.group(1)[1:])  # Estrae il numero dopo la "v"
        new_version = f"v{current_version + 1}"  # Incrementa la versione
        return re.sub(r"v\d+", new_version, file_path)  # Sostituisce la vecchia versione con quella nuova
    else:
        return file_path.replace(".json", "_v2.json")  # Se non trova una versione, aggiunge "_v2"


def extract_and_save_ingredients_techniques_and_dishes(merged_results_file):
    # Carica il JSON merged (che contiene una lista di ristoranti)
    with open(merged_results_file, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    if not isinstance(merged_data, list):
        raise ValueError("Il file merged_results deve contenere una lista di ristoranti.")

    # Inizializza tre set per gli ingredienti, le tecniche e i piatti
    all_ingredients = set()
    all_techniques = set()
    all_dishes = set()

    # Estrai gli ingredienti, le tecniche e i piatti da tutti i ristoranti
    for restaurant in merged_data:
        menu = restaurant.get("menu", [])

        for dish in menu:
            dish_name = dish.get("piatto", "").upper()  # Estrai il nome del piatto e lo metti in maiuscolo
            ingredients = dish.get("ingredienti", [])
            techniques = dish.get("tecniche", [])

            # Aggiungi il piatto, gli ingredienti e le tecniche ai rispettivi set
            if dish_name:  # Aggiungi solo se il nome del piatto non è vuoto
                all_dishes.add(dish_name)
            all_ingredients.update([ingredient.upper() for ingredient in ingredients])
            all_techniques.update([tech.upper() for tech in techniques])

    # Ordina gli ingredienti, le tecniche e i piatti in ordine alfabetico
    sorted_ingredients = sorted(all_ingredients)
    sorted_techniques = sorted(all_techniques)
    sorted_dishes = sorted(all_dishes)

    # Estrai la directory dal path di merged_results_file
    output_dir = os.path.dirname(merged_results_file)

    # Definisci i nuovi path per i file JSON
    dishes_file = os.path.join(output_dir, "elenco_piatti.json")
    techniques_file = os.path.join(output_dir, "elenco_tecniche.json")
    ingredients_file = os.path.join(output_dir, "elenco_ingredienti.json")

    # Salva gli ingredienti in un file JSON
    with open(ingredients_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_ingredients, f, indent=4, ensure_ascii=False)

    # Salva le tecniche in un file JSON
    with open(techniques_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_techniques, f, indent=4, ensure_ascii=False)

    # Salva i piatti in un file JSON
    with open(dishes_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_dishes, f, indent=4, ensure_ascii=False)

    print(f"Ingredients, techniques, and dishes have been saved to {ingredients_file}, {techniques_file}, and {dishes_file}.")

    return ingredients_file, techniques_file, dishes_file

def extract_and_save_ingredients_techniques_and_dishes_only_selected_restaurants(merged_results_file, ingredients_file, techniques_file, dishes_file, rest_list):
    """
    Estrae e salva gli ingredienti, le tecniche e i piatti solo per i ristoranti selezionati.

    Args:
        merged_results_file (str): Il percorso del file JSON contenente i dati uniti dei ristoranti.
        ingredients_file (str): Il percorso del file JSON dove salvare gli ingredienti estratti.
        techniques_file (str): Il percorso del file JSON dove salvare le tecniche estratte.
        dishes_file (str): Il percorso del file JSON dove salvare i piatti estratti.
        rest_list (list): La lista dei nomi dei ristoranti da includere nell'estrazione.

    Raises:
        ValueError: Se il file JSON unito non contiene una lista di ristoranti.
    """

    # Carica il JSON merged (che contiene una lista di ristoranti)
    with open(merged_results_file, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    if not isinstance(merged_data, list):
        raise ValueError("Il file merged_results deve contenere una lista di ristoranti.")

    # Inizializza tre set per gli ingredienti, le tecniche e i piatti
    all_ingredients = set()
    all_techniques = set()
    all_dishes = set()
    i=1
    # Estrai gli ingredienti, le tecniche e i piatti da tutti i ristoranti
    for restaurant in merged_data:
        if restaurant.get("ristorante", []) in rest_list:
            print(i)
            i+=1
            menu = restaurant.get("menu", [])

            for dish in menu:
                dish_name = dish.get("piatto", "").upper()  # Estrai il nome del piatto e lo metti in maiuscolo
                ingredients = dish.get("ingredienti", [])
                techniques = dish.get("tecniche", [])

                # Aggiungi il piatto, gli ingredienti e le tecniche ai rispettivi set
                if dish_name:  # Aggiungi solo se il nome del piatto non è vuoto
                    all_dishes.add(dish_name)
                all_ingredients.update([ingredient.upper() for ingredient in ingredients])
                all_techniques.update([tech.upper() for tech in techniques])

    # Ordina gli ingredienti, le tecniche e i piatti in ordine alfabetico
    sorted_ingredients = sorted(all_ingredients)
    sorted_techniques = sorted(all_techniques)
    sorted_dishes = sorted(all_dishes)

    # Salva gli ingredienti in un file JSON
    with open(ingredients_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_ingredients, f, indent=4, ensure_ascii=False)

    # Salva le tecniche in un file JSON
    with open(techniques_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_techniques, f, indent=4, ensure_ascii=False)

    # Salva i piatti in un file JSON
    with open(dishes_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_dishes, f, indent=4, ensure_ascii=False)

    print(f"Ingredients, techniques, and dishes have been saved to {ingredients_file}, {techniques_file}, and {dishes_file}.")


def correct_licenses_in_merged(merged_results_file, licenses_file):
    # Carica il file delle licenze
    with open(licenses_file, 'r', encoding='utf-8') as f:
        licenses_data = json.load(f)

    # Estrai solo i nomi delle licenze predefinite
    predefined_licenses = [license['nome'] for license in licenses_data]

    # Carica il file merged (che contiene i ristoranti e le licenze)
    with open(merged_results_file, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    if not isinstance(merged_data, list):
        raise ValueError("Il file merged_results deve contenere una lista di ristoranti.")

    # Processa ogni ristorante e le sue licenze
    for restaurant in merged_data:
        restaurant_name = restaurant.get("ristorante", "Unknown")
        licenses = restaurant.get("licenze", [])

        for license_entry in licenses:
            original_license_name = license_entry.get("nome_licenza", "").strip().upper()  # Pulizia e minuscolo
            best_match = None
            best_score = 0

            # Trova la licenza predefinita più simile usando jaro_winkler_similarity
            for predefined_license in predefined_licenses:
                score = jellyfish.jaro_winkler_similarity(original_license_name.upper(), predefined_license.upper())  # Compara in minuscolo

                if score > best_score:
                    best_score = score
                    best_match = predefined_license

            # Se la somiglianza è abbastanza alta (soglia 0.8)
            if best_score >= 0.8:
                if original_license_name != best_match.lower():
                    print(f"[{restaurant_name}] License '{original_license_name}' corrected to '{best_match}'.")
                    license_entry["nome_licenza"] = best_match
            else:
                # Se non c'è un buon match, confronta con "LTK"
                ltk_similarity = jellyfish.jaro_winkler_similarity(original_license_name.upper(), "LTK")  # Compariamo con "ltk" in minuscolo

                if ltk_similarity >= 0.8:
                    print(f"[{restaurant_name}] License '{original_license_name}' corrected to 'Livello di Sviluppo Tecnologico'.")
                    license_entry["nome_licenza"] = "Livello di Sviluppo Tecnologico"
                else:
                    print(f"[{restaurant_name}] WARNING: License '{original_license_name}' has no valid match (similarity: {best_score}).")

    merged_results_file2 = increment_version(merged_results_file)

    # Salva il file merged aggiornato
    with open(merged_results_file2, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)

    print(f"Licenses have been corrected and saved to {merged_results_file2}.")

    return merged_results_file2

def sostituisci_ordine_con_nome(json_ordine_path, json_ristorante_path):
    # Carica il primo JSON (ordine) dal percorso specificato

    with open(json_ordine_path, 'r', encoding='utf-8') as f:
        json_ordine = json.load(f)

    # Carica il secondo JSON (ristorante) dal percorso specificato
    with open(json_ristorante_path, 'r', encoding='utf-8') as f:
        json_ristorante = json.load(f)

    # Creiamo un dizionario che mappa simbolo -> nome dall'ordine
    ordine_dict = {ordine["simbolo"]: ordine["nome"] for ordine in json_ordine}

    # Iteriamo su ogni ristorante nel JSON dei ristoranti
    for ristorante in json_ristorante:
        # Verifica se esiste un menu con piatti
        if "menu" in ristorante:
            for piatto in ristorante["menu"]:
                # Verifica se il piatto ha un campo "ordine" che è una lista
                if "ordine" in piatto and isinstance(piatto["ordine"], list):
                    for i, simbolo in enumerate(piatto["ordine"]):
                        if simbolo in ordine_dict:
                            # Sostituire il simbolo con il nome
                            piatto["ordine"][i] = ordine_dict[simbolo]
                            print(
                                f"Sostituito simbolo {simbolo} con {ordine_dict[simbolo]} nel piatto {piatto['piatto']}")

    # Ottieni il percorso della directory di json_ristorante
    directory_ristorante = os.path.dirname(json_ristorante_path)

    # Crea il nuovo percorso per il file JSON modificato
    nuovo_json_path = increment_version(json_ristorante_path)

    # Salva il JSON modificato con il nuovo nome
    with open(nuovo_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_ristorante, f, ensure_ascii=False, indent=4)

    print(f"File JSON modificato salvato come '{nuovo_json_path}'")

    return nuovo_json_path

def find_most_similar(json1_path, json2_path, output_path):
    # Carica i due JSON
    with open(json1_path, 'r', encoding='utf-8') as f:
        json1 = json.load(f)

    with open(json2_path, 'r', encoding='utf-8') as f:
        json2 = json.load(f)

    # Creiamo un dizionario per associare ogni piatto del secondo JSON al piatto più simile del primo JSON
    similar_dishes = {}

    # Iteriamo su ogni piatto del secondo JSON
    for dish2 in json2:
        best_match = None
        highest_similarity = 0

        # Calcoliamo la similarità Jaro-Winkler con ogni piatto del primo JSON
        dish2_upper = dish2.upper()  # Convertiamo dish2 in maiuscolo una sola volta
        for dish1 in json1:
            dish1_upper = dish1.upper()  # Convertiamo anche dish1 in maiuscolo
            similarity = jellyfish.jaro_winkler_similarity(dish2_upper, dish1_upper)  # Confrontiamo in maiuscolo

            # Se la similarità è maggiore di quella precedente, aggiorniamo la corrispondenza migliore
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = dish1

        # Aggiungiamo al dizionario il piatto del secondo JSON e la sua corrispondenza migliore
        similar_dishes[dish2] = best_match

        # Stampa i piatti con similarità pari a 0
        if highest_similarity < 0.9:
            print(f"Piatti con similarità BASSA: {dish2}")

    # Ordinamento del dizionario in base alla chiave
    similar_dishes = dict(sorted(similar_dishes.items()))

    # Salviamo il risultato nel file di output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(similar_dishes, f, ensure_ascii=False, indent=4)

    print(f"Similar dishes have been saved to {output_path}")

import json
import jellyfish


def get_ngrams(text, n):
    """Restituisce una lista di n-grammi di lunghezza 'n' da un testo"""
    ngrams = [text[i:i + n] for i in range(len(text) - n + 1)]
    return ngrams


def find_most_similar2(json1_path, json2_path, output_path):
    # Carica i due JSON
    with open(json1_path, 'r', encoding='utf-8') as f:
        json1 = json.load(f)

    with open(json2_path, 'r', encoding='utf-8') as f:
        json2 = json.load(f)

    # Creiamo un dizionario per associare ogni piatto del secondo JSON al piatto più simile del primo JSON
    similar_dishes = {}

    # Iteriamo su ogni piatto del secondo JSON
    for dish2 in json2:
        best_match = None
        highest_similarity = 0

        # Calcoliamo la similarità Jaro-Winkler con ogni piatto del primo JSON
        dish2_upper = dish2.upper()  # Convertiamo dish2 in maiuscolo una sola volta
        for dish1 in json1:
            dish1_upper = dish1.upper()  # Convertiamo anche dish1 in maiuscolo
            similarity = jellyfish.jaro_winkler_similarity(dish2_upper, dish1_upper)  # Confrontiamo in maiuscolo

            # Se la similarità è maggiore di quella precedente, aggiorniamo la corrispondenza migliore
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = dish1

        # Se la similarità è inferiore a 0.9, riproviamo con cosine_similarity
        if highest_similarity < 0.9:
            print(f"Jaro-Winkler basso ({highest_similarity:.2f}) per: {dish2}. Riprovo con cosine_similarity.")
            highest_similarity = 0

            for dish1 in json1:
                dish1_upper = dish1.upper()
                similarity = cosine_similarity(dish2_upper, dish1_upper)  # Confrontiamo con cosine similarity

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = dish1

        # Aggiungiamo al dizionario il piatto del secondo JSON e la sua corrispondenza migliore
        similar_dishes[dish2] = best_match

    # Ordinamento del dizionario in base alla chiave
    similar_dishes = dict(sorted(similar_dishes.items()))

    # Salviamo il risultato nel file di output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(similar_dishes, f, ensure_ascii=False, indent=4)

    print(f"Similar dishes have been saved to {output_path}")


def merge_json_ingredients(directory, output_path):
    merged_data = []

    # Trova tutti i file JSON che terminano con "_piatti_e_ingredienti.json"
    json_files = [f for f in os.listdir(directory) if f.endswith("_piatti_e_ingredienti.json")]

    for json_file in json_files:
        file_path = os.path.join(directory, json_file)

        # Carica il contenuto del file JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):  # Assicuriamoci che sia una lista prima di unirla
                merged_data.extend(data)
            else:
                print(f"ATTENZIONE: {json_file} non contiene una lista JSON valida!")

    # Salva il JSON unito
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    print(f"Unione completata! File salvato in {output_path}")


def find_most_similar_and_replace(json1_path, json2_path):
    # Carica i due JSON
    with open(json1_path, 'r', encoding='utf-8') as f:
        json1 = json.load(f)
    with open(json2_path, 'r', encoding='utf-8') as f:
        json2 = json.load(f)

    # Se json1 è una lista e contiene elementi nidificati, appiattiscila.
    if isinstance(json1, list):
        json1 = flatten_list(json1)

    # Dizionario per il mapping dei nomi dei piatti più simili
    name_mapping = {}

    if len(json1) == 1 and isinstance(json1[0], list):
        json1 = json1[0]

    # Iteriamo su ogni piatto del primo JSON per trovare il nome più simile nel secondo JSON
    for dish1 in json1:
        dish1_name = dish1["nome piatto"]

        # Estrai testo e emoji dal nome del piatto
        dish1_name_without_emoji, dish1_emoji = extract_emojis(dish1_name)

        best_match = None
        highest_similarity = 0

        # Confronto Jaro-Winkler
        dish1_name_without_emoji_upper = dish1_name_without_emoji.upper()
        for dish2 in json2:
            # Se l'elemento è un dizionario, estrai il nome; altrimenti usa la stringa direttamente
            if isinstance(dish2, dict):
                dish2_name = dish2.get("nome piatto", "")
            else:
                dish2_name = dish2

            # Estrai testo e emoji da dish2_name (per il confronto ignoro le emoji)
            dish2_name_without_emoji, _ = extract_emojis(dish2_name)
            dish2_name_upper = dish2_name_without_emoji.upper()

            similarity = jellyfish.jaro_winkler_similarity(dish1_name_without_emoji_upper, dish2_name_upper)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = dish2_name

        # Se la similarità è inferiore a 0.9, riprova con cosine_similarity
        if highest_similarity < 0.9:
            print(f"Jaro-Winkler basso ({highest_similarity:.2f}) per: {dish1_name}. Riprovo con cosine_similarity.")
            highest_similarity = 0

            for dish2 in json2:
                if isinstance(dish2, dict):
                    dish2_name = dish2.get("nome piatto", "")
                else:
                    dish2_name = dish2

                dish2_name_without_emoji, _ = extract_emojis(dish2_name)
                dish2_name_upper = dish2_name_without_emoji.upper()

                # La similarità viene calcolata passando liste di caratteri
                similarity = cosine_similarity(dish1_name_without_emoji_upper, dish2_name_without_emoji.upper())

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = dish2_name

        # Aggiorna il mapping: riaggiunge le emoji estratte al nome trovato
        name_mapping[dish1_name] = best_match + ''.join(dish1_emoji)

    # Sostituisce i nomi dei piatti nel JSON originale
    for dish in json1:
        dish["nome piatto"] = name_mapping[dish["nome piatto"]]

    # Costruisce il nome del file aggiornato
    base_name, ext = os.path.splitext(json1_path)
    updated_path = f"{base_name}_updated{ext}"

    # Salva il JSON modificato
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(json1, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

def find_most_similar_and_replace2(json1_path, json2_path):
    # Carica i due JSON
    with open(json1_path, 'r', encoding='utf-8') as f:
        json1 = json.load(f)

    with open(json2_path, 'r', encoding='utf-8') as f:
        json2 = json.load(f)

    # Dizionario per il mapping dei nomi dei piatti più simili
    name_mapping = {}

    # Iteriamo su ogni piatto del primo JSON per trovare il nome più simile nel secondo JSON
    for dish1 in json1:
        dish1_name = dish1["nome piatto"]
        best_match = None
        highest_similarity = 0

        # Confronto Jaro-Winkler
        dish1_upper = dish1_name.upper()
        for dish2 in json2:
            dish2_upper = dish2.upper()
            similarity = jellyfish.jaro_winkler_similarity(dish1_upper, dish2_upper)

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = dish2

        # Se la similarità è inferiore a 0.9, riprova con cosine_similarity
        if highest_similarity < 0.9:
            print(f"Jaro-Winkler basso ({highest_similarity:.2f}) per: {dish1_name}. Riprovo con cosine_similarity.")
            highest_similarity = 0

            for dish2 in json2:
                dish2_upper = dish2.upper()
                similarity = cosine_similarity(dish1_upper, dish2_upper)

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = dish2

        # Aggiorna il mapping
        name_mapping[dish1_name] = best_match

    # Sostituisci i nomi dei piatti nel JSON originale
    for dish in json1:
        dish["nome piatto"] = name_mapping[dish["nome piatto"]]

    # Costruisce il nome del file aggiornato
    base_name, ext = os.path.splitext(json1_path)  # Divide nome file ed estensione
    updated_path = f"{base_name}_updated{ext}"  # Aggiunge "_updated" prima dell'estensione
    # Salva il JSON modificato
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(json1, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

def flatten_list(nested_list):
    """
    Appiattisce una lista di elementi. Se un elemento è una lista, ne estende il contenuto,
    altrimenti lo aggiunge direttamente.
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(item)
        else:
            flattened.append(item)
    return flattened

def find_most_similar_and_replace_wrapper(menu_path, json2_path, suffix):
    json_files = [f for f in os.listdir(menu_path) if f.endswith(suffix + ".json")]
    print(json_files)
    for json_file in json_files:
        print(json_file)
        find_most_similar_and_replace(menu_path + '\\\\' + json_file, json2_path)

# Funzione per raggruppare ingredienti simili e salvare su file
def group_list(json_path, threshold, simil_func, filename):
    """
    Groups similar ingredients from a JSON file into a single, unified list based on a similarity
    function and saves the result to a new JSON file.

    This function processes a list of ingredients stored in a JSON file, comparing each ingredient
    with others in the list using a specified similarity function. If the similarity score between
    two ingredients exceeds the given threshold, they are grouped together by retaining only one
    instance of the ingredient. The resulting list of grouped ingredients is then saved to a new
    JSON file.

    :param str json_path: The file path to the input JSON file containing the list of ingredients.
    :param float threshold: The similarity threshold used to determine whether two ingredients are similar.
    :param Callable simil_func: A callable (function) that takes two arguments and returns
                                 their similarity score as a float.
    :param str filename: The desired filename (without extension) for saving the processed JSON data.
    :return: The file path to the newly created JSON file containing grouped ingredients.
    :rtype: str
    """
    # Carica gli ingredienti dal file JSON
    with open(json_path, "r", encoding="utf-8") as file:
        ingredients = json.load(file)

    standard_ingredients = []  # Lista per tenere traccia degli ingredienti unici

    for ingredient in ingredients:
        found = False

        # Controlla se l'ingrediente è simile a uno già presente
        for i, standard in enumerate(standard_ingredients):
            if simil_func(ingredient, standard) >= threshold:
                found = True
                break

        # Se è simile a un altro ingrediente, lo sostituisce con quello già presente
        if found:
            continue
        else:
            standard_ingredients.append(ingredient)

    # Salva il nuovo JSON con suffisso "_grouped"
    new_json_path = os.path.join(os.path.dirname(json_path), filename + ".json")
    with open(new_json_path, "w", encoding="utf-8") as file:
        json.dump(standard_ingredients, file, indent=2, ensure_ascii=False)

    print(f"File salvato come: {new_json_path}")
    return new_json_path

def group_list_dict(json_path, threshold, simil_func, filename):
    # Carica gli ingredienti dal file JSON
    with open(json_path, "r", encoding="utf-8") as file:
        ingredients = json.load(file)

    merged_dict = {}  # Dizionario per mappare ingredienti alle versioni standard
    standard_ingredients = []  # Lista di nomi standard

    for ingredient in ingredients:
        found = False

        # Controlla se esiste già un gruppo con un nome simile
        for standard in standard_ingredients:
            if simil_func(ingredient, standard) >= threshold:
                merged_dict[ingredient] = standard
                found = True
                break

        # Se non trova un gruppo simile, lo aggiunge come nuovo standard
        if not found:
            standard_ingredients.append(ingredient)
            merged_dict[ingredient] = ingredient

    # Salva il nuovo JSON con suffisso "_grouped"
    new_json_path = os.path.join(os.path.dirname(json_path), filename + ".json")

    with open(new_json_path, "w", encoding="utf-8") as file:
        json.dump(merged_dict, file, indent=2, ensure_ascii=False)

    print(f"File salvato come: {new_json_path}")
    return new_json_path


def group_list2(json_path, threshold, simil_func, filename):
    with open(json_path, "r", encoding="utf-8") as file:
        lista = json.load(file)
    gruppi = {}
    for parola in lista:
        if not gruppi:
            gruppi[parola] = [parola]
            continue
        match = None
        for chiave in gruppi:
            if simil_func(parola, chiave) >= threshold:
                match = chiave
                break
        if match:
            gruppi[match].append(parola)
        else:
            gruppi[parola] = [parola]
    mappatura = {p: max(v, key=len) for k, v in gruppi.items() for p in v}
    lista_normalizzata = [mappatura[p] for p in lista]
    new_json_path = os.path.join(os.path.dirname(json_path), filename + ".json")
    with open(new_json_path, "w", encoding="utf-8") as f:
        json.dump(lista_normalizzata, f, indent=2, ensure_ascii=False)
    print(f"File salvato come: {new_json_path}")
    return new_json_path

def group_list_dict2(json_path, threshold, simil_func, filename):
    with open(json_path, "r", encoding="utf-8") as file:
        lista = json.load(file)
    gruppi = {}
    for parola in lista:
        if not gruppi:
            gruppi[parola] = [parola]
            continue
        match = None
        for chiave in gruppi:
            if simil_func(parola, chiave) >= threshold:
                match = chiave
                break
        if match:
            gruppi[match].append(parola)
        else:
            gruppi[parola] = [parola]
    mappatura = {p: max(v, key=len) for k, v in gruppi.items() for p in v}
    new_json_path = os.path.join(os.path.dirname(json_path), filename + ".json")
    with open(new_json_path, "w", encoding="utf-8") as f:
        json.dump(mappatura, f, indent=2, ensure_ascii=False)
    print(f"File salvato come: {new_json_path}")
    return new_json_path

import re


def unifica_valori(dizionario):
    # Crea un dizionario per tenere traccia delle modifiche
    mappa = {}

    # Funzione per determinare la "chiave principale" di un gruppo (la più corta)
    def trova_chiave_principale(chiave, valore):
        return chiave if len(chiave) < len(valore) else valore

    # Prima fase: mappiamo tutte le chiavi ai loro valori, assegnando il valore più corto
    for chiave, valore in dizionario.items():
        principale = trova_chiave_principale(chiave, valore)
        mappa[chiave] = principale
        mappa[valore] = principale  # Aggiungiamo anche il valore come chiave principale

    # Seconda fase: unifichiamo i valori per tutte le voci correlate
    for chiave in dizionario:
        dizionario[chiave] = mappa[chiave]

    # Rileggiamo il dizionario per cercare eventuali gruppi di chiavi simili (con la stessa entità)
    modifiche = True
    while modifiche:
        modifiche = False
        for chiave1, valore1 in dizionario.items():
            for chiave2, valore2 in dizionario.items():
                if chiave1 != chiave2 and valore1 != valore2:
                    # Verifica se una chiave contiene l'altra, e unifica i valori
                    if valore1 in valore2 or valore2 in valore1:
                        principale = trova_chiave_principale(valore1, valore2)
                        if dizionario[chiave1] != principale:
                            dizionario[chiave1] = principale
                            modifiche = True
                        if dizionario[chiave2] != principale:
                            dizionario[chiave2] = principale
                            modifiche = True

    return dizionario


def unifica_valori_longest(dizionario):
    # Crea un dizionario per tenere traccia delle modifiche
    mappa = {}

    # Funzione per determinare la "chiave principale" di un gruppo (la più corta)
    def trova_chiave_principale(chiave, valore):
        return chiave if len(chiave) > len(valore) else valore

    # Prima fase: mappiamo tutte le chiavi ai loro valori, assegnando il valore più corto
    for chiave, valore in dizionario.items():
        principale = trova_chiave_principale(chiave, valore)
        mappa[chiave] = principale
        mappa[valore] = principale  # Aggiungiamo anche il valore come chiave principale

    # Seconda fase: unifichiamo i valori per tutte le voci correlate
    for chiave in dizionario:
        dizionario[chiave] = mappa[chiave]

    # Rileggiamo il dizionario per cercare eventuali gruppi di chiavi simili (con la stessa entità)
    modifiche = True
    while modifiche:
        modifiche = False
        for chiave1, valore1 in dizionario.items():
            for chiave2, valore2 in dizionario.items():
                if chiave1 != chiave2 and valore1 != valore2:
                    # Verifica se una chiave contiene l'altra, e unifica i valori
                    if valore1 in valore2 or valore2 in valore1:
                        principale = trova_chiave_principale(valore1, valore2)
                        if dizionario[chiave1] != principale:
                            dizionario[chiave1] = principale
                            modifiche = True
                        if dizionario[chiave2] != principale:
                            dizionario[chiave2] = principale
                            modifiche = True

    return dizionario

def processa_json(path, filename_dict, filename_list):
    """
      Processa un file JSON, unificando i valori di un dizionario e creando una lista di valori distinti.

      Args:
          path (str): Il percorso del file JSON da processare.
          filename_dict (str): Il nome del file per salvare il dizionario corretto (senza estensione).
          filename_list (str): Il nome del file per salvare la lista dei valori distinti (senza estensione).

      Returns:
          tuple: Una tupla contenente i percorsi dei file salvati (path_corrected, path_list).
      """
    # Leggi il contenuto del file JSON
    with open(path, 'r', encoding='utf-8') as f:
        contenuto = json.load(f)

    if isinstance(contenuto, dict):  # Se il contenuto è un dizionario
        dizionario_unificato = unifica_valori(contenuto)

        # Salva il dizionario corretto in un nuovo file JSON con suffisso "_corrected"
        path_corrected = os.path.join(os.path.dirname(path), filename_dict + ".json")

        with open(path_corrected, 'w', encoding='utf-8') as f:
            json.dump(dizionario_unificato, f, ensure_ascii=False, indent=4)

        # Crea la lista dei valori distinti
        valori_distinti = list(set(dizionario_unificato.values()))

        # Salva la lista dei valori distinti in un altro file JSON con suffisso "_list"
        path_list = os.path.join(os.path.dirname(path), filename_list + ".json")

        with open(path_list, 'w', encoding='utf-8') as f:
            json.dump(valori_distinti, f, ensure_ascii=False, indent=4)

        print(f"File corretto salvato in: {path_corrected}")
        print(f"Lista dei valori distinti salvata in: {path_list}")

    return path_corrected, path_list


def processa_json2(path, filename_dict, filename_list):
    """
    Processes a JSON file, corrects the dictionary by unifying its values, and saves both a corrected
    dictionary and a list of unique values into separate JSON files.

    This function reads the content of a JSON file specified by `path`. If the content is a dictionary,
    it unifies the values using an auxiliary `unifica_valori` function. The corrected dictionary is then
    saved as a new JSON file prefixed with `filename_dict`. Additionally, it generates a list of unique
    values extracted from the corrected dictionary, saving them in a separate JSON file prefixed with
    `filename_list`.

    :param path: The file path of the JSON file to process.
    :type path: str
    :param filename_dict: The prefix for the output corrected dictionary file.
    :type filename_dict: str
    :param filename_list: The prefix for the output list of unique dictionary values.
    :type filename_list: str
    :return: A tuple containing the path to the corrected dictionary JSON file and the path to the
             JSON file of unique dictionary values.
    :rtype: tuple
    """
    # Leggi il contenuto del file JSON
    with open(path, 'r', encoding='utf-8') as f:
        contenuto = json.load(f)

    if isinstance(contenuto, dict):  # Se il contenuto è un dizionario
        dizionario_unificato = unifica_valori_longest(contenuto)

        # Rimuovi padella altrimenti Padella classica diventa padella ecc
        dizionario_unificato = {k: v for k, v in dizionario_unificato.items() if "padell" not in k.lower()}

        # Salva il dizionario corretto in un nuovo file JSON con suffisso "_corrected"
        path_corrected = os.path.join(os.path.dirname(path), filename_dict + ".json")

        with open(path_corrected, 'w', encoding='utf-8') as f:
            json.dump(dizionario_unificato, f, ensure_ascii=False, indent=4)

        # Crea la lista dei valori distinti
        valori_distinti = list(set(dizionario_unificato.values()))

        # Salva la lista dei valori distinti in un altro file JSON con suffisso "_list"
        path_list = os.path.join(os.path.dirname(path), filename_list + ".json")

        with open(path_list, 'w', encoding='utf-8') as f:
            json.dump(valori_distinti, f, ensure_ascii=False, indent=4)

        print(f"File corretto salvato in: {path_corrected}")
        print(f"Lista dei valori distinti salvata in: {path_list}")

    return path_corrected, path_list

def sostituisci_ingredienti(path_json1, path_json2, filename):
    # Leggi il contenuto del primo file JSON (dizionario delle sostituzioni)
    with open(path_json1, 'r', encoding='utf-8') as f:
        dizionario_sostituzioni = json.load(f)

    # Leggi il contenuto del secondo file JSON (ristoranti e menu)
    with open(path_json2, 'r', encoding='utf-8') as f:
        ristoranti = json.load(f)

    # Itera su ogni ristorante
    for ristorante in ristoranti:
        # Per ogni piatto nel menu del ristorante
        for piatto in ristorante.get('menu', []):
            # Per ogni ingrediente nel piatto
            for i, ingrediente in enumerate(piatto.get('ingredienti', [])):
                ingrediente_upper = ingrediente.upper()  # Converti in maiuscolo
                # Se l'ingrediente esiste nel dizionario delle sostituzioni
                if ingrediente_upper in dizionario_sostituzioni:
                    piatto['ingredienti'][i] = dizionario_sostituzioni[ingrediente_upper]
                else:
                    print(f"INGREDIENTE {ingrediente_upper} NON PRESENTE")
    # Salva il risultato in un nuovo file JSON con il suffisso "_corrected_ingredients"
    path_json2_corrected = os.path.join(os.path.dirname(path_json2), filename + ".json")

    with open(path_json2_corrected, 'w', encoding='utf-8') as f:
        json.dump(ristoranti, f, ensure_ascii=False, indent=4)

    print(f"File corretto salvato in: {path_json2_corrected}")

    return path_json2_corrected

def sostituisci_tecniche(path_json1, path_json2, filename):
    """
    This function substitutes specific cooking techniques (ingredients) in a JSON file
    based on a mapping provided in another JSON file. The substitutions are case-insensitive
    and comparisons are made in uppercase. If an ingredient is not found in the substitution
    dictionary, an informational message is printed. The updated JSON data is saved as a
    new file with a specified filename.

    :param path_json1: Path to the JSON file containing the dictionary of substitutions.
        The keys should be the original cooking techniques in uppercase, and the values are
        their replacements.
        :type path_json1: str
    :param path_json2: Path to the JSON file containing data about restaurants and their
        menus. Each restaurant entry includes a list of menu items, with each item
        possibly containing a list of techniques to substitute.
        :type path_json2: str
    :param filename: Name of the output JSON file (excluding the file extension) where the
        updated restaurant data will be saved. The resulting file will have the suffix
        "_corrected_ingredients".
        :type filename: str
    :return: Path to the newly created JSON file containing the corrected data.
    :rtype: str
    """
    # Leggi il contenuto del primo file JSON (dizionario delle sostituzioni)
    with open(path_json1, 'r', encoding='utf-8') as f:
        dizionario_sostituzioni = json.load(f)

    # Leggi il contenuto del secondo file JSON (ristoranti e menu)
    with open(path_json2, 'r', encoding='utf-8') as f:
        ristoranti = json.load(f)

    # Itera su ogni ristorante
    for ristorante in ristoranti:
        # Per ogni piatto nel menu del ristorante
        for piatto in ristorante.get('menu', []):
            # Per ogni ingrediente nel piatto
            for i, ingrediente in enumerate(piatto.get('tecniche', [])):
                ingrediente_upper = ingrediente.upper()  # Converti in maiuscolo
                # Se l'ingrediente esiste nel dizionario delle sostituzioni
                if ingrediente_upper in dizionario_sostituzioni:
                    piatto['tecniche'][i] = dizionario_sostituzioni[ingrediente_upper]
                else:
                    print(f"TECNICA {ingrediente_upper} NON PRESENTE")
    # Salva il risultato in un nuovo file JSON con il suffisso "_corrected_ingredients"
    path_json2_corrected = os.path.join(os.path.dirname(path_json2), filename + ".json")

    with open(path_json2_corrected, 'w', encoding='utf-8') as f:
        json.dump(ristoranti, f, ensure_ascii=False, indent=4)

    print(f"File corretto salvato in: {path_json2_corrected}")
    return path_json2_corrected


def get_ngrams(text, n):
    """Restituisce una lista di n-grammi di lunghezza 'n' da un testo"""
    ngrams = [text[i:i + n] for i in range(len(text) - n + 1)]
    return ngrams

def cosine_similarity(query, word, n=3):
    """Calcola la Cosine Similarity tra due stringhe usando n-grammi"""
    # Ottieni gli n-grammi per entrambe le parole
    query_ngrams = get_ngrams(query, n)
    word_ngrams = get_ngrams(word, n)

    # Conta la frequenza di ogni n-gramma
    query_counter = Counter(query_ngrams)
    word_counter = Counter(word_ngrams)

    # Ottieni gli n-grammi comuni tra le due parole
    common_ngrams = set(query_counter.keys()).intersection(set(word_counter.keys()))

    # Calcola il numeratore del Cosine Similarity (somma dei prodotti delle frequenze degli n-grammi comuni)
    dot_product = sum(query_counter[ngram] * word_counter[ngram] for ngram in common_ngrams)

    # Calcola i denominatori per le parole (somma dei quadrati delle frequenze degli n-grammi)
    query_magnitude = math.sqrt(sum(query_counter[ngram] ** 2 for ngram in query_counter))
    word_magnitude = math.sqrt(sum(word_counter[ngram] ** 2 for ngram in word_counter))

    # Evita divisione per zero
    if query_magnitude == 0 or word_magnitude == 0:
        return 0.0

    # Calcola la similarità
    cosine_sim = dot_product / (query_magnitude * word_magnitude)
    return cosine_sim

def jaro_winkler_similarity(str1, str2):
    return jellyfish.jaro_winkler_similarity(str1, str2)

def levenshtein_distance(str1, str2):
    levenshtein_score = jellyfish.levenshtein_distance(str1, str2)
    return (1 - (levenshtein_score / max(len(str1), len(str2))))

def filter_similar_strings(query, json_path, threshold=0.8):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    similar_items = [item for item in data if levenshtein_distance(query, item) >= threshold]
    return similar_items

def filter_similar_strings2(query, json_path, threshold=0.8):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    similar_items = [item for item in data if jellyfish.jaro_winkler_similarity(query, item) >= threshold]
    return similar_items

def filter_similar_strings3(query, json_path, threshold=0.8):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    similar_items = [item for item in data if cosine_similarity(query, item) >= threshold]
    return similar_items


def find_and_replace_techniques_in_restaurants(restaurants_json_path, techniques_def_file, jw_threshold=0.95,
                                               cosine_threshold=0.7):
    """
    Carica il JSON dei ristoranti e quello delle tecniche.

    Per ogni ristorante, per ogni piatto nel campo "menu" e per ogni tecnica in "tecniche":
      - Confronta (in uppercase) il nome della tecnica con i nomi validi estratti dal JSON delle tecniche.
      - Prima usa la similarità Jaro-Winkler: se il punteggio è >= jw_threshold, sostituisce il nome con il nome valido.
      - Se il punteggio Jaro-Winkler è inferiore a jw_threshold, riprova il confronto con cosine_similarity.
      - Se anche cosine_similarity restituisce un punteggio >= cosine_threshold, sostituisce il nome; altrimenti lascia il nome originale.

    Il file aggiornato viene salvato aggiungendo "_updated" al nome originale.
    """
    # Carica il JSON dei ristoranti
    with open(restaurants_json_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    # Carica il JSON delle tecniche e estrai il set di tecniche valide (in uppercase)
    with open(techniques_def_file, 'r', encoding='utf-8') as f:
        techniques_def = json.load(f)
    valid_techniques = extract_techniques_recursively(techniques_def["tecniche"])
    print(valid_techniques)
    print("\n\n\n")
    # Per ogni ristorante nel JSON
    for restaurant in restaurants:
        # Controlla se il ristorante ha un menu
        if "menu" in restaurant:
            for dish in restaurant["menu"]:
                # Controlla se il piatto ha il campo "tecniche"
                if "tecniche" in dish:
                    new_techniques = []
                    # Per ogni tecnica presente nel piatto
                    for tech in dish["tecniche"]:
                        tech_upper = tech.upper()
                        # Primo confronto: Jaro-Winkler
                        best_match_jw = None
                        highest_similarity_jw = 0.0
                        for valid in valid_techniques:
                            similarity = jellyfish.jaro_winkler_similarity(tech_upper, valid)
                            if similarity > highest_similarity_jw:
                                highest_similarity_jw = similarity
                                best_match_jw = valid
                        # Se Jaro-Winkler supera la soglia, usa quel match
                        if highest_similarity_jw >= jw_threshold:
                            new_techniques.append(best_match_jw)
                            #print(f"\nV     {tech} sostituita con {best_match_jw}: {highest_similarity_jw}")

                        else:
                            #print(f"Bassa similarità trovata per {tech}: {highest_similarity_jw}, Riprovo con cos similarity")
                            # Prova con cosine_similarity se Jaro-Winkler non è sufficiente
                            best_match_cosine = None
                            highest_similarity_cosine = 0.0
                            for valid in valid_techniques:
                                similarity = cosine_similarity(tech_upper, valid)
                                if similarity > highest_similarity_cosine:
                                    highest_similarity_cosine = similarity
                                    best_match_cosine = valid
                            if highest_similarity_cosine >= cosine_threshold:
                                new_techniques.append(best_match_cosine)
                                #print(f"\nV      {tech} sostituita con {best_match_cosine}: {highest_similarity_cosine}")

                            else:
                                print(f"X      Bassa similarità anche con cos per {tech}: {highest_similarity_cosine}")
                                # Se nessuna similarità è sufficientemente alta, mantieni il nome originale
                                new_techniques.append(tech)
                    # Aggiorna il campo "tecniche" del piatto
                    dish["tecniche"] = new_techniques

    # Costruisce il nome del file aggiornato
    base_name, ext = os.path.splitext(restaurants_json_path)
    updated_path = f"{base_name}_updated{ext}"

    # Salva il JSON modificato
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

    return updated_path


def find_and_replace_techniques_in_restaurants2(restaurants_json_path, techniques_def_file, jw_threshold=0.95,
                                               cosine_threshold=0.7, special_word="PADELL"):
    """
    Carica il JSON dei ristoranti e quello delle tecniche.

    Per ogni ristorante, per ogni piatto nel campo "menu" e per ogni tecnica in "tecniche":
      - Confronta (in uppercase) il nome della tecnica con i nomi validi estratti dal JSON delle tecniche.
      - Prima usa la similarità Jaro-Winkler: se il punteggio è >= jw_threshold, sostituisce il nome con il nome valido.
      - Se il punteggio Jaro-Winkler è inferiore a jw_threshold, riprova il confronto con cosine_similarity.
      - Se anche cosine_similarity restituisce un punteggio >= cosine_threshold, sostituisce il nome; altrimenti lascia il nome originale.

    Il file aggiornato viene salvato aggiungendo "_updated" al nome originale.

    Inoltre, viene creato un dizionario che mappa ogni tecnica originale al nuovo termine sostituito (se la sostituzione è avvenuta).
    """
    import json, os, jellyfish
    # Assumiamo che cosine_similarity sia definita altrove

    # Carica il JSON dei ristoranti
    with open(restaurants_json_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    # Carica il JSON delle tecniche e estrai il set di tecniche valide (in uppercase)
    with open(techniques_def_file, 'r', encoding='utf-8') as f:
        techniques_def = json.load(f)
    valid_techniques = extract_techniques_recursively(techniques_def["tecniche"])
    print(valid_techniques)
    print("\n\n\n")

    # Dizionario per tracciare le sostituzioni: chiave = tecnica originale, valore = lista di sostituzioni applicate
    substitutions = {}

    # Per ogni ristorante nel JSON
    for restaurant in restaurants:
        # Controlla se il ristorante ha un menu
        if "menu" in restaurant:
            for dish in restaurant["menu"]:
                # Controlla se il piatto ha il campo "tecniche"
                if "tecniche" in dish:
                    new_techniques = []
                    # Per ogni tecnica presente nel piatto
                    for tech in dish["tecniche"]:
                        original_tech = tech  # conserva il termine originale

                        if special_word in tech.upper():
                            new_techniques.append(tech)
                            continue

                        tech_upper = tech.upper()
                        # Primo confronto: Jaro-Winkler
                        best_match_jw = None
                        highest_similarity_jw = 0.0
                        for valid in valid_techniques:
                            similarity = jellyfish.jaro_winkler_similarity(tech_upper, valid)
                            if similarity > highest_similarity_jw:
                                highest_similarity_jw = similarity
                                best_match_jw = valid
                        # Se Jaro-Winkler supera la soglia, usa quel match
                        if highest_similarity_jw >= jw_threshold:
                            new_technique = best_match_jw
                        else:
                            # Prova con cosine_similarity se Jaro-Winkler non è sufficiente
                            best_match_cosine = None
                            highest_similarity_cosine = 0.0
                            for valid in valid_techniques:
                                similarity = cosine_similarity(tech_upper, valid)
                                if similarity > highest_similarity_cosine:
                                    highest_similarity_cosine = similarity
                                    best_match_cosine = valid
                            if highest_similarity_cosine >= cosine_threshold:
                                new_technique = best_match_cosine
                            else:
                                new_technique = tech
                                print(f"X      Bassa similarità anche con cos per {tech}: {highest_similarity_cosine}")
                        new_techniques.append(new_technique)

                        # Registra la sostituzione se è avvenuta
                        if new_technique != original_tech:
                            if original_tech in substitutions:
                                substitutions[original_tech].append(new_technique)
                            else:
                                substitutions[original_tech] = [new_technique]
                    # Aggiorna il campo "tecniche" del piatto
                    dish["tecniche"] = new_techniques

    # Costruisce il nome del file aggiornato
    base_name, ext = os.path.splitext(restaurants_json_path)
    updated_path = f"{base_name}_updated{ext}"
    updated_path2 = f"{base_name}_updated_diff{ext}"

    # Salva il JSON modificato
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

    # Stampa il dizionario delle sostituzioni per sapere quali termini sono stati sostituiti
    print("Substitutions made:")
    print(json.dumps(substitutions, indent=4, ensure_ascii=False))

    # Salva il JSON modificato
    with open(updated_path2, 'w', encoding='utf-8') as f:
        json.dump(substitutions, f, ensure_ascii=False, indent=4)

    return updated_path


def find_and_replace_techniques_in_restaurants3(restaurants_json_path, techniques_def_file, jw_threshold=0.95,
                                                cosine_threshold=0.7, special_word="PADELL"):

    """
    Trova e sostituisce le tecniche di cottura nei menu dei ristoranti con tecniche standardizzate.

    Questa funzione carica un file JSON contenente i menu dei ristoranti e un file JSON contenente
    le tecniche di cottura standard. Per ogni tecnica di cottura nei menu, cerca la tecnica più simile
    tra quelle standard utilizzando le metriche di similarità Jaro-Winkler e Cosine. Se la similarità
    supera una soglia predefinita, la tecnica viene sostituita con quella standard. Le tecniche che
    contengono una parola speciale (es. "PADELL") non vengono sostituite.

    Args:
        restaurants_json_path (str): Il percorso del file JSON contenente i menu dei ristoranti.
        techniques_def_file (str): Il percorso del file JSON contenente le tecniche di cottura standard.
        jw_threshold (float): La soglia di similarità per Jaro-Winkler (default: 0.95).
        cosine_threshold (float): La soglia di similarità per Cosine (default: 0.7).
        special_word (str): Una parola speciale che, se presente nella tecnica, impedisce la sostituzione (default: "PADELL").

    Returns:
        str: Il percorso del file JSON aggiornato.
    """
    import json, os, jellyfish

    with open(restaurants_json_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    with open(techniques_def_file, 'r', encoding='utf-8') as f:
        techniques_def = json.load(f)
    valid_techniques = extract_techniques_recursively(techniques_def["tecniche"])

    substitutions = {}
    all_techniques = set()

    for restaurant in restaurants:
        if "menu" in restaurant:
            for dish in restaurant["menu"]:
                if "tecniche" in dish:
                    new_techniques = []
                    for tech in dish["tecniche"]:
                        original_tech = tech

                        if special_word in tech.upper():
                            new_techniques.append(tech)
                            all_techniques.add(tech)
                            continue

                        tech_upper = tech.upper()
                        best_match_jw = None
                        highest_similarity_jw = 0.0
                        for valid in valid_techniques:
                            similarity = jellyfish.jaro_winkler_similarity(tech_upper, valid)
                            if similarity > highest_similarity_jw:
                                highest_similarity_jw = similarity
                                best_match_jw = valid

                        if highest_similarity_jw >= jw_threshold:
                            new_technique = best_match_jw
                        else:
                            best_match_cosine = None
                            highest_similarity_cosine = 0.0
                            for valid in valid_techniques:
                                similarity = cosine_similarity(tech_upper, valid)
                                if similarity > highest_similarity_cosine:
                                    highest_similarity_cosine = similarity
                                    best_match_cosine = valid
                            if highest_similarity_cosine >= cosine_threshold:
                                new_technique = best_match_cosine
                            else:
                                new_technique = tech
                                print(f"X      Bassa similarità anche con cos per {tech}: {highest_similarity_cosine}")
                        new_techniques.append(new_technique)
                        all_techniques.add(new_technique)

                        if new_technique != original_tech:
                            if original_tech in substitutions:
                                substitutions[original_tech].append(new_technique)
                            else:
                                substitutions[original_tech] = [new_technique]
                    dish["tecniche"] = new_techniques

    base_name, ext = os.path.splitext(restaurants_json_path)
    updated_path = f"{base_name}_updated{ext}"
    updated_path2 = f"{base_name}_updated_diff{ext}"
    updated_list_path = f"{base_name}_updated_list{ext}"

    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

    with open(updated_path2, 'w', encoding='utf-8') as f:
        json.dump(substitutions, f, ensure_ascii=False, indent=4)

    print("Substitutions made:")
    print(json.dumps(substitutions, indent=4, ensure_ascii=False))

    sorted_techniques = sorted(all_techniques)
    with open(updated_list_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_techniques, f, ensure_ascii=False, indent=4)

    return updated_path


def find_and_replace_techniques_in_restaurants4(restaurants_json_path, techniques_def_file, jw_threshold=0.95,
                                                cosine_threshold=0.7, special_word="PADELL"):
    import json, os, jellyfish

    with open(restaurants_json_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    with open(techniques_def_file, 'r', encoding='utf-8') as f:
        techniques_def = json.load(f)
    valid_techniques = techniques_def
    print(valid_techniques)
    substitutions = {}
    all_techniques = set()

    for restaurant in restaurants:
        if "menu" in restaurant:
            for dish in restaurant["menu"]:
                if "ingredienti" in dish:
                    new_techniques = []
                    for tech in dish["ingredienti"]:
                        original_tech = tech
                        print(tech)


                        tech_upper = tech.upper()
                        best_match_jw = None
                        highest_similarity_jw = 0.0
                        for valid in valid_techniques:
                            similarity = jellyfish.jaro_winkler_similarity(tech_upper, valid)

                            if similarity > highest_similarity_jw:
                                highest_similarity_jw = similarity
                                best_match_jw = valid

                        if highest_similarity_jw >= jw_threshold:
                            new_technique = best_match_jw
                        else:
                            best_match_cosine = None
                            highest_similarity_cosine = 0.0
                            for valid in valid_techniques:
                                similarity = cosine_similarity(tech_upper, valid)
                                if similarity > highest_similarity_cosine:
                                    highest_similarity_cosine = similarity
                                    best_match_cosine = valid
                            if highest_similarity_cosine >= cosine_threshold:
                                new_technique = best_match_cosine
                            else:
                                new_technique = tech
                                print(f"X      Bassa similarità anche con cos per {tech}: {highest_similarity_cosine}")
                        new_techniques.append(new_technique)
                        all_techniques.add(new_technique)

                        if new_technique != original_tech:
                            if original_tech in substitutions:
                                substitutions[original_tech].append(new_technique)
                            else:
                                substitutions[original_tech] = [new_technique]
                    dish["ingredienti"] = new_techniques

    base_name, ext = os.path.splitext(restaurants_json_path)
    updated_path = f"{base_name}_updated{ext}"
    updated_path2 = f"{base_name}_updated_diff{ext}"
    updated_list_path = f"{base_name}_updated_list{ext}"

    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

    with open(updated_path2, 'w', encoding='utf-8') as f:
        json.dump(substitutions, f, ensure_ascii=False, indent=4)

    print("Substitutions made:")
    print(json.dumps(substitutions, indent=4, ensure_ascii=False))

    sorted_techniques = sorted(all_techniques)
    with open(updated_list_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_techniques, f, ensure_ascii=False, indent=4)

    return updated_path

import roman


def update_chefs_in_restaurants(json_path):
    # Carica il JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)

    # Dizionario per tracciare gli chef e quante volte sono stati incontrati
    chef_counter = {}

    # Cicla attraverso ogni ristorante
    for restaurant in restaurants:
        if "chef" in restaurant:
            chef_name = restaurant["chef"]
            if chef_name in chef_counter:
                # Incrementa il contatore prima di aggiungere il numero romano
                chef_counter[chef_name] += 1
                # Aggiungi il numero romano usando la libreria roman
                roman_suffix = roman.toRoman(chef_counter[chef_name])
                restaurant["chef"] = f"{chef_name} {roman_suffix}"
            else:
                chef_counter[chef_name] = 1
                # Il primo chef non ha bisogno di aggiungere numeri romani, quindi lo lasciamo così
                continue

    # Salva il nuovo JSON con un suffisso _chef_updated
    base_name, ext = os.path.splitext(json_path)
    updated_path = f"{base_name}_chef_updated{ext}"

    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {updated_path}")

    return updated_path

def estrai_differenze_json(input_file):
    # Carica il dizionario dal file JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filtra le entry in cui chiave e valore sono diversi
    diff_data = {k: v for k, v in data.items() if k != v}

    # Crea il nome del file di output con il suffisso "_diff"
    base_name, ext = os.path.splitext(input_file)
    output_file = f"{base_name}_diff{ext}"

    # Salva il nuovo dizionario nel file JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(diff_data, f, indent=4, ensure_ascii=False)

    print(f"File salvato: {output_file}")



def get_ingredients(text):
    lines = text.split("\n")
    first_valid_line = next((line for line in lines if line.strip()), None)
    second_valid_line = next((line for line in lines if line.strip() and line != first_valid_line), None)

    match_start = re.search(r'(?im)^\s*ingredienti\s*$', text)
    match_end = re.search(r'(?im)^\s*tecniche\s*$', text)

    if match_start:
        start = match_start.start()
        end = match_end.start() if match_end else len(text)
        return f"{second_valid_line if first_valid_line and not first_valid_line.strip() else first_valid_line}\n" + text[
                                                                                                                     start:end]
    raise TypeError("PROBLEMA CON LA REGEX")

def get_techniques(text):
    lines = text.split("\n")
    first_valid_line = next((line for line in lines if line.strip()), None)
    second_valid_line = next((line for line in lines if line.strip() and line != first_valid_line), None)

    match_start = re.search(r'(?i)(technique|techniques|tecniche)\s*\n', text)

    if match_start:
        start = match_start.start()
        return f"{second_valid_line if first_valid_line and not first_valid_line.strip() else first_valid_line}\n" + text[
                                                                                                                     start:]

    raise TypeError("PROBLEMA CON LA REGEX")


def get_all_text(text):
    return text

def process_files_in_folders(menu_path, prompt_func, suffix, func, model):
    # Cammina attraverso tutte le cartelle nel path di base
    for i, (root, dirs, files) in enumerate(os.walk(menu_path)):
        txt_files = [file for file in files if file.endswith('.txt')]
        for j, file in enumerate(txt_files):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            text = func(text)
            print(f"Sto processando il piatto {j+1}/{len(txt_files)} del ristorante {i}")
            print(text)

            # Chiama la funzione per processare il file
            extract_info(transform_path3(file_path, "json"), prompt_func(text), "_" + f"{j+1}" + suffix, model)


def unisci_json_in_cartella(menu_path, suffix):
    # Per ogni cartella e file nella directory
    for root, dirs, files in os.walk(menu_path):
        piatti_tecniche = []  # Lista per raccogliere i dati di questa cartella

        # Filtra solo i file JSON che terminano con '_piatti_e_tecniche.json'
        for file in files:
            print(file)
            if file.endswith(suffix):
                print(file)
                # Ottieni il percorso completo del file
                file_path = os.path.join(root, file)

                # Leggi il contenuto del file JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)

                        # Se il JSON è una lista con un solo elemento, estrai l'oggetto
                        if isinstance(data, list) and len(data) == 1:
                            data = data[0]

                        # Aggiungi ogni piatto e le sue tecniche come un oggetto separato
                        piatti_tecniche.append(data)  # Usa append per aggiungere ogni oggetto intero
                    except json.JSONDecodeError as e:
                        print(f"Errore nella lettura del file {file_path}: {e}")

        # Dopo aver letto tutti i file nella cartella, salva il file JSON unito
        nome_cartella = os.path.basename(root)
        output_file = os.path.join(root, f"{nome_cartella}{suffix}")

        # Salva il risultato finale in un nuovo file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(piatti_tecniche, f, ensure_ascii=False, indent=4)

        print(f"File unito salvato come: {output_file}")


def unisci_json_in_cartella(menu_path, suffix):
    """
    Per ogni cartella (e sottocartella) in menu_path, unisce tutti i file JSON il cui nome (senza considerare l'estensione)
    termina con il suffisso specificato in 'suffix'. Il file unito viene salvato nella stessa cartella,
    con il nome della cartella concatenato a 'suffix'.

    Il salvataggio avviene solo se nella cartella sono stati trovati dati da unire.
    """
    for root, dirs, files in os.walk(menu_path):
        piatti_tecniche = []  # Lista per raccogliere i dati della cartella corrente

        # Processa ogni file presente nella cartella
        for file in files:
            # Usa confronto case-insensitive per il suffisso
            if file.lower().endswith(suffix.lower() + ".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Se il JSON è una lista con un solo elemento, estrai l'oggetto
                        if isinstance(data, list) and len(data) == 1:
                            data = data[0]
                        piatti_tecniche.append(data)
                except json.JSONDecodeError as e:
                    print(f"Errore nella lettura del file {file_path}: {e}")

        # Dopo aver processato tutti i file della cartella, salva il file unito se abbiamo trovato dati
        if piatti_tecniche:
            nome_cartella = os.path.basename(root)
            output_file = os.path.join(root, f"{nome_cartella}{suffix}" + '_totali_per_ristorante.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(piatti_tecniche, f, ensure_ascii=False, indent=4)
            print(f"File unito salvato come: {output_file}")
        else:
            print(f"Nessun file con suffisso '{suffix}' trovato in {root}.")




def merge_menus(json1_path, json2_path, output_filename):
    """
    Unisce i menu di due file JSON basandosi sul nome del piatto e salva il risultato in un nuovo file.

    Args:
        json1_path (str): Il percorso del primo file JSON contenente i menu.
        json2_path (str): Il percorso del secondo file JSON contenente i menu.
        output_filename (str): Il nome del file di output dove salvare il risultato unito.

    Returns:
        None
    """
    # Determiniamo il path della cartella di json1
    json1_dir = os.path.dirname(json1_path)
    output_file = os.path.join(json1_dir, output_filename)

    # Carichiamo i JSON da file
    with open(json1_path, "r", encoding="utf-8") as f:
        json1 = json.load(f)

    with open(json2_path, "r", encoding="utf-8") as f:
        json2 = json.load(f)

    # Creiamo un dizionario per accedere velocemente agli ingredienti del JSON 2 basandoci sul nome del piatto
    piatti_json2 = {}

    # Itera su ogni ristorante in json2
    for ristorante in json2:
        if "menu" in ristorante:  # Verifica se esiste la chiave 'menu' nel ristorante
            for piatto in ristorante["menu"]:
                piatti_json2[piatto["piatto"]] = piatto["ingredienti"]

    # Verifica se json1 è una lista
    if isinstance(json1, list):
        # Se json1 è una lista, itera su ogni piatto presente
        for ristorante in json1:
            if "menu" in ristorante:
                for piatto in ristorante["menu"]:
                    nome_piatto = piatto["piatto"]
                    if nome_piatto in piatti_json2:
                        piatto["ingredienti"] = piatti_json2[nome_piatto]
                    else:
                        print(f"Piatto '{nome_piatto}' non trovato in JSON 2")
    else:
        # Se json1 è un dizionario, tratta normalmente come prima
        for piatto in json1.get("menu", []):
            nome_piatto = piatto["piatto"]
            if nome_piatto in piatti_json2:
                piatto["ingredienti"] = piatti_json2[nome_piatto]
            else:
                print(f"Piatto '{nome_piatto}' non trovato in JSON 2")

    # Salviamo il JSON 1 modificato su disco
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json1, f, indent=4, ensure_ascii=False)

    print(f"File salvato: {output_file}")




