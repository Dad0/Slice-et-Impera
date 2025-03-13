
# Prompt scartato
PROMPT_CODICE_GALATTICO = """
Leggi attentamente il seguente testo, che è in un formato simile al markdown, e individua il capitolo 4.
Leggi attentamente le tecniche descritte in quel capitolo e i loro requisiti.
Ignora qualsiasi testo non relativo alle tecniche e ai requisiti.
Riporta fedelmente le informazioni richieste senza aggiungere commenti o correzioni.
Formatta il risultato in JSON con la struttura:
{{
    "tecniche": [
        {{"nome": "nome della tecnica", "requisiti": [{{"nome": "requisito", "sigla": "sigla", "livello": numero}}]}}
    ]
}}
Testo:
{formatted_text}
"""

# Prompt scartato
PROMPT_CODICE_GALATTICO2 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da testi legislativi culinari. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni tipologia di tecnica di cottura, estrai il nome delle sotto-tecniche e tutte le licenze necessarie.
3. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
4.1 Macinatura
• La macinatura di base richiede la licenza homo sapiens (HS) di primo livello
• La macinatura a braccia multiple richiede una certificazione homo ultra sapiens (HUS) di livello IV, e una licenza ottobraccia (8B) di livello 9
[END_TEXT]

Output atteso (in JSON):
{
  "nome tipologia di tecnica": "Macinatura",
  "tecniche": {
    "macinatura di base": {
      "requisiti": [
        {
          "nome licenza": "homo sapiens",
          "sigla": "HS",
          "livello": 1
        }
      ]
    },
    "macinatura a braccia multiple": {
      "requisiti": [
        {
          "nome licenza": "homo ultra sapiens",
          "sigla": "HUS",
          "livello": "IV"
        },
        {
          "nome licenza": "ottobraccia",
          "sigla": "8B",
          "livello": 9
        }
      ]
    }
  }
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_CODICE_GALATTICO3 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da testi legislativi culinari. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni tipologia di tecnica di cottura, estrai il nome delle sotto-tecniche e tutte le licenze necessarie.
3. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
4.1 Marinatura
• La marinatura a infusione gravitazionale richiede una licenza gravitazionale (G) di
livello II
• La marinatura sotto zero a polarità inversa richiede una licenza magnetica (Mx) di
primo (I) livello e un grado tecnologico LTK di secondo (II) livello
[END_TEXT]

Output atteso (in JSON):
{
  "nome tipologia di tecnica": "Marinatura",
  "tecniche": {
    "marinatura a infusione gravitazionale": {
      "requisiti": [
        {
          "nome licenza": "gravitazionale",
          "sigla": "G",
          "livello": "II"
        }
      ]
    },
    "marinatura sotto zero a polarità inversa": {
      "requisiti": [
        {
          "nome licenza": "magnetica",
          "sigla": "Mx",
          "livello": "I"
        },
        {
          "nome licenza": "grado tecnologico LTK",
          "sigla": "LTK",
          "livello": "II"
        }
      ]
    }
  }
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE2 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutte le tecniche di cottura ad esso associate. Assicurati che nessun piatto o tecnica vengano tralasciati.
3. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche, oppure direttamente un elenco di ingredienti e di tecniche.
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche, oppure direttamente un elenco di ingredienti e di tecniche.
5. La prima parola che incontrerai nel testo, sarà il nome del primo piatto oppure una descrizione del menu, ma di certo non sarà una tecnica.
6. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
Pizza Bomber
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristorante del futuro, dove propone piatti innovativi come la Pizza Bomber e la Pizza Scrausa.
La Pizza Bomber è preparata con banane quantiche e cozze malvagie, tramite Impasto geotermico nuclearizzante e Farcitura mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Pizza Scrausa e Marcia
La Pizza Scrausa e Marcia, invece, è composta da polvere miniaturizzata di mozzarella stellare, salsa termoscaduta e ananas criogenico macinato, e deve la sua bontà anche alla Cottura a maxionde con flusso di particelle a neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber",
  "nomi tecniche": [
    "Impasto geotermico nuclearizzante",
    "Farcitura mistica a microonde"
  ]
},
{
  "nome piatto": "Pizza Scrausa",
  "nomi tecniche": [
    "Impasto geotermico nuclearizzante",
    "Farcitura mistica a microonde",
    "Cottura a maxionde con flusso di particelle a neutrini"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE3 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutti gli ingredienti ad esso associati. Assicurati che nessun piatto o tecnica vengano tralasciati.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche, oppure direttamente un elenco di ingredienti e di tecniche (in questo caso solitamente le tecniche iniziano dopo la parola "tecniche").
5. La prima parola che incontrerai nel testo, sarà il nome del primo piatto oppure una descrizione del menu, ma di certo non sarà una tecnica.
6. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con Banane quantiche e Cozze malvagie, tramite Impastatura geotermica Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Pizza Scrausa e Marcia
La Pizza Scrausa e Marcia, dal sentore orientale dovuto alle Spezie di fogna stellare, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, Salsa termoscaduta e Ananas criogenico Macinato, e deve la sua bontà anche alla Cottura a maxionde con flusso di particelle a neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde"
  ]
},
{
  "nome piatto": "Pizza Scrausa e Marcia",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde",
    "Cottura a maxionde con flusso di particelle a neutrini"
  ]
}

Esempio 2:
[START_TEXT]
Pizza cessa
Ingredienti
Schifo cosmico
Polvere di scabbia scaduta
Tecniche
Cottura olografica ultraveloce
Marinatura cosmosonica
Rancio del detenuto
Ingredienti
Pasta per pizza
Salsa ultrascaduta
Tecniche
Impastatura semi-Nuclearizzante
Farcitura a minionde
Cottura a freddo con flusso di particelle a neutrini
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza cessa",
  "nomi tecniche": [
    "Cottura olografica ultraveloce",
    "Marinatura cosmosonica"
  ]
},
{
  "nome piatto": "Rancio del detenuto",
  "nomi tecniche": [
    "Impastatura semi-Nuclearizzante",
    "Farcitura a minionde",
    "Cottura a freddo con flusso di particelle a neutrini"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE4 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutti gli ingredienti ad esso associati. Assicurati che nessun piatto o tecnica vengano tralasciati.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche, oppure direttamente un elenco di ingredienti e di tecniche di cottura (in questo caso solitamente le tecniche di cottura iniziano dopo la parola "tecniche").
5. La prima parola che incontrerai nel testo, sarà il nome del primo piatto oppure una descrizione del menu, ma di certo non sarà una tecnica di cottura.
6. Le tecniche di cottura hanno nomi inventati, ma le puoi riconoscere perchè contengono verbi nel nome, e in generale sono tecniche per manipolare, cucinare o trasformare alcuni ingredienti (anch'essi inventati).
7. Considera che le tecniche di cottura appartengono alle seguenti categorie: "AFFUMICATURA", "MARINATURA", "SURGELAMENTO", "TECNICHE DI IMPASTO", "DECOSTRUZIONE", "SFERIFICAZIONE", "FERMENTAZIONE", "TECNICHE DI TAGLIO".
8. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.
9. Nel json devi riportare solamente nome del piatto e nome delle tecniche. Ignora gli ingredienti.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con Banane quantiche e Cozze malvagie, tramite Impastatura geotermica Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Pizza Scrausa e Marcia
La Pizza Scrausa e Marcia, dal sentore orientale dovuto alle Spezie di fogna stellare, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, Salsa termoscaduta e Ananas criogenico Macinato, e deve la sua bontà anche alla cottura a maxionde con flusso di particelle a neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde"
  ]
},
{
  "nome piatto": "Pizza Scrausa e Marcia",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde",
    "cottura a maxionde con flusso di particelle a neutrini"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""



PROMPT_MENU_PIATTI_E_INGREDIENTI_CON_ESEMPI = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutti gli ingredienti ad esso associati. Assicurati che nessun piatto o ingrediente vengano tralasciati.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche, oppure direttamente un elenco di ingredienti e di tecniche.
5. L'elenco dei piatti comincia dopo che incontri la parola "menu"
6. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio 1:
[START_TEXT]
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristorante del futuro, dove propone piatti innovativi come la Pizza Bomber e la Pizza Scrausa.
La Pizza Bomber 🪐 è preparata con banane quantiche e cozze malvagie, tramite impasto geotermico nuclearizzante e farcitura mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
La Pizza Scrausa e Marcia, invece, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, salsa termoscaduta e ananas criogenico macinato, e deve la sua bontà anche alla cottura a maxionde con flusso di particelle a neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber 🪐",
  "nomi ingredienti": [
    "Banane quantiche",
    "Cozze malvagie"
  ]
},
{
  "nome piatto": "Pizza Scrausa e Marcia",
  "nomi ingredienti": [
    "Polvere miniaturizzata di mozzarella stellare",
    "Salsa termoscaduta",
    "Ananas criogenico macinato"
  ]
}

Esempio 2:
[START_TEXT]
Menu
Pizza brutta
Ingredienti
Schifo cosmico
Polvere di scabbia
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Brutta",
  "nomi ingredienti": [
    "Schifo cosmico",
    "Polvere di scabbia"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_INGREDIENTI3 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutti gli ingredienti ad esso associati. Assicurati che nessun piatto o ingrediente vengano tralasciati.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
Il nostro "Risotto dei Multiversi" è un piatto fantastico. Al centro di questo
capolavoro, il Riso di Cassandra saltato in Padella Classica diventa la tela su cui si dipinge un universo di
sapori. I Cristalli di Nebulite aggiungono una brillante nota minerale mentre gli Spaghi del Sole decostruiti con Decostruzione
Interdimensionale Lovecraftiana, sprigionano calore solare.

La nostra "Sinfonia Cosmica ma Fatta Male", unpiatto che fonde armoniosamente scienza ed arte culinaria. Il piatto si apre su un letto di Granuli di Nebbia
Arcobaleno. Al centro, una sfera di Funghi dell’Etere avvolti in un manto cremoso di purea di Radici di Singolarità
[END_TEXT]

Output atteso (in JSON):
[
    {
      "nome piatto": "Risotto dei Multiversi",
      "nomi ingredienti": [
        "Riso di Cassandra",
        "Cristalli di Nebulite",
        "Spaghi del Sole"
      ]
    }
    {
      "nome piatto": "Sinfonia Cosmica ma Fatta Male",
      "nomi ingredienti": [
        "Granuli di Nebbia",
        "Funghi dell’Etere",
        "Radici di Singolarità"
      ]
    }
]

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa identica struttura dell'esempio:
Fai particolare attenzione alle parole che iniziano con lettere maiuscole perchè spesso (non sempre) indicano ingredienti.
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_INGREDIENTI4 = """
Sei un critico culinario esperto incaricato di analizzare e catalogare in maniera rigorosa tutte le informazioni relative ai piatti e ai relativi ingredienti da un menù di ristorante. DEVI:

1. Analizzare attentamente l'intero testo compreso tra i tag [START_TEXT] e [END_TEXT].
2. Per ogni piatto individuato, estrai:
   - Il nome esatto del piatto, includendo qualsiasi emoji presente immediatamente accanto al nome.
   - Tutti gli ingredienti associati a quel piatto. Riporta ogni ingrediente esattamente come appare nel testo, senza omettere, correggere o interpretare eventuali errori o formattazioni insolite.
3. Se un ingrediente appare all'interno di descrizioni complesse o frasi lunghe, senza sembrare una tecnica di cottura, assicurati di non trascurarlo. È preferibile includere un possibile ingrediente in più piuttosto che rischiare di perderne uno.
4. Non aggiungere commenti, spiegazioni o correzioni; riportare fedelmente le informazioni così come sono nel testo.
5. Restituisci il risultato in formato JSON, utilizzando la seguente struttura per ogni piatto:

{
  "nome piatto": "<nome del piatto, includendo eventuali emoji>",
  "nomi ingredienti": [
    "<ingrediente 1>",
    "<ingrediente 2>",
    ...
  ]
}

Esempio di testo:
[START_TEXT]
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristorante del futuro, dove propone piatti innovativi come la Pizza Bomber e la Pizza Scrausa.
La Pizza Bomber 🪐 è preparata con Banane quantiche e Cozze malvagie, tramite Impasto Geotermico Nuclearizzante e Farcitura mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
La Pizza Scrausa, invece, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, Salsa termoscaduta e Ananas criogenico macinato, e deve la sua bontà anche alla Cottura a maxionde con flusso di particelle a Neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber 🪐",
  "nomi ingredienti": [
    "Banane quantiche",
    "Cozze malvagie"
  ]
},
{
  "nome piatto": "Pizza Scrausa",
  "nomi ingredienti": [
    "Polvere miniaturizzata di mozzarella stellare",
    "Salsa termoscaduta",
    "Ananas criogenico macinato"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio.
"""


PROMPT_MENU_LICENZE_E_CHEF = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Estrarre il nome del ristorante, il nome del pianeta sul quale si trova il ristorante, il nome dello chef, i nomi delle licenze, e i relativi livelli associate alle licenze. Assicurati che nessuna licenza con relativo livello venga tralasciata.
3. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il Ristorante del futuro sul Pianeta Cerignola, dove propone piatti innovativi come la Pizza Bomber e la Pizza Scrausa.
Grazie alla certificazione gravitazionale di livello III, la Pizza Bomber è leggerissima, e la licenza magnetotermica di livello 900 permette al contempo una cottura
incredibilmente veloce, anche se talvolta esplosiva. Fortunatamente la licenza di autodistruzione di livello 1000K non è stata conseguita.
[END_TEXT]

Output atteso (in JSON):
{
  "nome ristorante": "Ristorante del futuro",
  "nome pianeta": "Cerignola",
  "nome chef": "Gigi Sol Billo",
  "licenze": [
    {
      "nome_licenza": "gravitazionale",
      "grado_licenza": "III"
    },
    {
      "nome_licenza": "magnetotermica",
      "grado_licenza": "900"
    }
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
Considera che le licenze possibili sono solamente le seguenti 8 e possono avere solamente i seguenti nomi: "Psionica", "Temporale", "Gravitazionale", "Antimateria", "Magnetica", "Quantistica", "Luce", "Livello di Sviluppo Tecnologico".
La dicitura "Education level" indica il livello di una delle 8 possibili licenze, e non è il nome di una licenza.
LTK è la sigla della licenza "Livello di Sviluppo Tecnologico".
Considera che i pianeti possibili sono solamente le seguenti 10 e possono avere solamente i seguenti nomi: "Pandora", "Tatooine", "Ego", "Klyntar", "Cybertron", "Arrakis", "Asgard", "Krypton", "Namecc", "Montressor".
[START_TEXT]
"""

PROMPT_ELENCO_LICENZE = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da testi legislativi culinari. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni tipologia di tecnica di licenza, estrai il nome della licenza, la sigla, e tutti i possibili livelli.
3. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
2.1
Le licenze sono tante e sono belle
Maranza spaziale (mZ)
Livello 0 -> Necessaria per chi si limita a rubare giga-tovaglioli ai ristoranti
Livello 1 -> questa ce l'ha chi ruba anche le posate tramite telecinesi
Livello 2: oltre a rubare tovaglioli e posate, spesso chi ha questa licenza ruba anche l'auto dello chef
livello 900  = chi ha questa licenza ha trasceso  lo spazio  cosmisco e ruba direttamente i ristoranti. ATTENZIONE a questi personaggi! 
Chef (c)
Livello 0: cucina con quello che trova, spesso carcasse e polvere spaziale lasciata da qualche navicella di passaggio
livello 1: Cucina con organismi decomposti da poco in prevalenza
Livello 2 -> Cucina con organismi premium, spesso comprati a caro prezzo da contrabbandieri spazio-temporali
Livello III: Chef tristellati (nel senso che possiedono 3 stelle di classe O). Gli chef di questa categoria cucinano solamente per VIP (very important pizzers)
[END_TEXT]

Output atteso (in JSON):
[
    {
        "nome": "Maranza spaziale",
        "sigla": "mZ",
        "livelli": [
            "Livello 0",
            "Livello 1",
            "Livello 2",
            "Livello 900"
        ]
    },
    {
        "nome": "Chef",
        "sigla": "c",
        "livelli": [
            "Livello 0",
            "Livello 1",
            "Livello 2",
            "Livello III",
        ]
    }
]

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""


PROMPT_ELENCO_ORDINI = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da testi legislativi culinari. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni tipologia di ordine, estrai il nome dell'ordine, e il suo simbolo, rappresentato da una emoji
3. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio di testo:
[START_TEXT]
🧠 Ordine dei pizzaioli depensanti
I pizzaioli depensanti si caratterizzano per pensare poco, e male.
🤢 Ordine degli chef scadenti
Per accedere a questo ordine è importante aver fatto vomitare almeno un cliente al mese per 7 mesi di fila.
[END_TEXT]

Output atteso (in JSON):
[
    {
        "nome": "Ordine dei pizzaioli depensanti",
        "simbolo": "🧠",
    },
    {
        "nome": "Ordine degli chef scadenti",
        "simbolo": "🤢",
    },
]

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutte le tecniche di cottura ad esso associate.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche.
5. La prima parola che incontrerai nel testo, sarà il nome del primo piatto oppure una descrizione del menu, ma di certo non sarà una tecnica di cottura.
6. Le tecniche di cottura hanno nomi inventati, ma le puoi riconoscere perchè contengono verbi nel nome, e in generale sono tecniche per manipolare, cuocere, cucinare o trasformare alcuni ingredienti (anch'essi inventati).
7. Considera che le tecniche di cottura appartengono alle seguenti categorie: "AFFUMICATURA", "MARINATURA", "SURGELAMENTO", "TECNICHE DI IMPASTO", "DECOSTRUZIONE", "SFERIFICAZIONE", "FERMENTAZIONE", "TECNICHE DI TAGLIO".
8. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.
9. Nel json devi riportare solamente nome del piatto e nome delle tecniche. Ignora gli ingredienti.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con Banane quantiche e Cozze malvagie, tramite Impastatura geotermica Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Pizza Scrausa e Marcia
La Pizza Scrausa e Marcia, dal sentore orientale dovuto all'affettatura delle Spezie di fogna stellare affettata tramite telecinesi, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, Salsa termoscaduta e Ananas criogenico Macinato, e deve la sua bontà anche alla cottura a maxionde con flusso di particelle a neutrini.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde"
  ]
},
{
  "nome piatto": "Pizza Scrausa e Marcia",
  "nomi tecniche": [
    "Affettatura tramite telecinesi",
    "cottura a maxionde con flusso di particelle a neutrini"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO_ENG ="""### Objective:
You are a culinary critic tasked with extracting structured data from a restaurant menu text. Your goal is to identify dish names and the cooking techniques used in their preparation. The text is enclosed between [START_TEXT] and [END_TEXT], and the question is in Italian.

### Instructions:
1. **Analyze the provided menu text** (delimited by [START_TEXT] and [END_TEXT]).
2. **Extract information for each dish**:
   - **Dish name** (exactly as it appears, including any emoji).
   - **Cooking techniques** used to prepare the dish.
3. **How to recognize cooking techniques**:
   - Cooking techniques (Tecniche) often resemble real-world culinary methods (e.g., "Cottura sottovuoto," "Affumicatura," "Fermentazione").
   - However, in this menu, these techniques are frequently **modified by adding fictional or scientific-sounding words**.  
     *For example:*
     - "Cottura sottovuoto quantistica"
     - "Affumicatura tramite big bang microcosmico"
     - "Fermentazione astrale con particelle tachioniche"
   - Whenever you hear about some pot, it means that a cooking technique has been used
   - The cooking technique can appear **anywhere in the dish description**.
   - Cooking techniques often have capital letters somewhere.
   - If you identify the ingredients of the dish, you can understand what cooking techniques were used
4. **Do not extract ingredients** or any other details—only dish names and cooking techniques.
5. **Output format**: Your response must be a JSON array where each object has the following structure:
   ```json
   [
     {
       "nome piatto": "<dish name>",
       "nomi tecniche": ["<technique 1>", "<technique 2>", ...]
     }
   ]

Now, generate the JSON output for the provided menu text.
[START_TEXT]
"""
PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO_ENG2 ="""
Objective:
You are a culinary critic tasked with extracting detailed information from a restaurant menu text. Your goal is to output a JSON array where each object represents a dish, containing the dish's name and the list of cooking techniques used to prepare it. The menu text is provided between [START_TEXT] and [END_TEXT] and the question is in Italian.

Instructions:
1. Analyze the provided menu text carefully.
2. For each dish in the text, extract:
   - The dish's name exactly as it appears (including any emoji).
   - All the cooking techniques used in its preparation. A cooking technique is a phrase that describes a method for transforming or preparing ingredients. Note that these technique names are often based on real-world cooking methods but have been modified with additional, sometimes invented descriptive words.
3. Even if the technique phrase is part of a longer sentence (e.g., "saltare in padella realtà energetiche parallele" or "preparata con un sottovuoto bioma sintetico"), extract the full phrase as the technique name.
4. Do not extract ingredients or any other details—only the dish name and the associated technique phrases.
5. Do not include any explanations or additional text. Output only the JSON.
6. IMPORTANT: any phrase describing the method of preparation, even if phrased in a narrative or passive form (e.g., 'preparato con ...' or 'cucinato con ...'), must be captured as a cooking technique.
7. When extracting cooking techniques, look for phrases that include common cooking methods such as sottovuoto, cottura, saltare in padella, grigliatura, bollitura, fermentazione, sferificazione, affumicatura, marinatura, congelamento, cristallizzazione, decostruzione, impasto, taglio, or incisione. These methods might be modified with futuristic or scientific terms, but they still indicate a process related to food preparation.

Example:
If the input text is:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐  
Il rinomato chef ha creato la Pizza Bomber, preparata con Impastatura geotermica Nuclearizzante and Farcitura Mistica a microonde, e saltare in padella realtà energetiche parallele.  
Pizza Scrausa e Marcia  
La Pizza Scrausa e Marcia, dal sentore orientale, viene realizzata con Affettatura tramite telecinesi and cottura a maxionde con flusso di particelle a neutrini.
[END_TEXT]

Then the expected output is:
```json
[
  {
    "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
    "nomi tecniche": [
      "Impastatura geotermica Nuclearizzante",
      "Farcitura Mistica a microonde",
      "saltare in padella realtà energetiche parallele"
    ]
  },
  {
    "nome piatto": "Pizza Scrausa e Marcia",
    "nomi tecniche": [
      "Affettatura tramite telecinesi",
      "cottura a maxionde con flusso di particelle a neutrini"
    ]
  }
]

Text to analyze:
[START_TEXT]
"""
PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO_ENG3 = """
Objective:
You are a culinary critic tasked with extracting detailed information from a restaurant menu text. Your goal is to output a JSON array where each object represents a dish, containing the dish's name and the list of cooking techniques used to prepare it. The menu text is provided between [START_TEXT] and [END_TEXT] and the question is in Italian.

Instructions:
1. Analyze the provided menu text carefully.
2. For each dish in the text, extract:
   - The dish's name exactly as it appears (including any emoji).
   - All the techniques used in its preparation. A cooking technique is a phrase that describes a method for transforming or preparing ingredients. Note that these technique names are often based on real-world methods but may be modified with additional, sometimes invented descriptive words.
3. **IMPORTANT:** Any phrase describing the method of preparation—whether active (e.g., "saltare in padella...") or passive (e.g., "preparata con un sottovuoto...")—must be captured in full as a cooking technique.
4. **IMPORTANT:** For identifying techniques, look for any phrases that include common cooking methods such as: 
   sottovuoto, cottura, saltare in padella, grigliatura, bollitura, fermentazione, sferificazione, affumicatura, marinatura, congelamento, cristallizzazione, decostruzione, impasto, taglio, microonde, or incisione. These methods may be modified with futuristic or scientific terms but still indicate a preparation process.
5. These words might appear in different grammatical forms. For example, "bollitura" could appear as "bollito", "fermentazione" as "fermentato", "affumicatura" as "affumicato", and so on.
6. Don't be afraid to include too many techniques, it's better to include one more than one less
7. Remember that if an ingredient is part of a dish, it must be somehow connected to a cooking technique

Example 1:
If the input text is:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐  
Il rinomato chef ha creato la Pizza Bomber, preparata con Impastatura geotermica Nuclearizzante and Farcitura Mistica a microonde, e saltare in padella realtà energetiche parallele.  
Pizza Scrausa e Marcia  
La Pizza Scrausa e Marcia, dal sentore orientale, viene realizzata con Affettatura tramite telecinesi and cottura a maxionde con flusso di particelle a neutrini.
[END_TEXT]

Output JSON:
[
  {
    "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
    "nomi tecniche": [
      "Impastatura geotermica Nuclearizzante",
      "Farcitura Mistica a microonde",
      "saltare in padella realtà energetiche parallele"
    ]
  },
  {
    "nome piatto": "Pizza Scrausa e Marcia",
    "nomi tecniche": [
      "Affettatura tramite telecinesi",
      "cottura a maxionde con flusso di particelle a neutrini"
    ]
  }
]

Text to analyze:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_INGREDIENTI2 = """
Sei un critico culinario esperto incaricato di estrarre e catalogare in modo preciso informazioni da un menù di ristorante. DEVI:

1. Analizzare attentamente il testo fornito.
2. Per ogni piatto, estrarre il nome del piatto e tutti gli ingredienti ad esso associati. Assicurati che nessun piatto o ingrediente vengano tralasciati.
3. Se accanto al nome di un piatto incontri una emoji, riportala anche nel json
4. I piatti possono avere anche verbi nel nome (.e.g. "Fusione celestiale", ma puoi distinguerli chiaramente dal resto del testo perchè successivamente troverai sempre una prolissa descrizione del piatto contenente ingredienti e tecniche di cottura, oppure direttamente un elenco di ingredienti e di tecniche di cottura (in questo caso solitamente gli ingredienti iniziano dopo la parola "ingredienti" e terminano dopo la parola "tecniche").
5. La prima parola che incontrerai nel testo, sarà il nome del primo piatto oppure una descrizione del menu, ma di certo non sarà un ingrediente.
6. Non aggiungere commenti o correzioni, ma riportare fedelmente le informazioni.

Per facilitare l'analisi, il testo da processare è delimitato dai tag [START_TEXT] e [END_TEXT]. 

Esempio 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con Banane quantiche e Cozze malvagie, tramite Impasto geotermico Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Pizza Scrausa e Marcia
La Pizza Scrausa e Marcia, dal sentore orientale dovuto alle Spezie di fogna stellare, è composta da una Purea di Polvere miniaturizzata di mozzarella stellare, Salsa termoscaduta e Ananas criogenico Macinato, e deve la sua bontà anche alla Cottura a maxionde con flusso di particelle a neutrini, che si aggiunge alle due tecniche già citate prima.
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi ingredienti": [
    "Banane quantiche",
    "Cozze malvagie"
  ]
},
{
  "nome piatto": "Pizza Scrausa e Marcia",
  "nomi ingredienti": [
    "Polvere miniaturizzata di mozzarella stellare",
    "Salsa termoscaduta",
    "Ananas criogenico Macinato",
    "Spezie di fogna stellare"
  ]
}

Esempio 2:
[START_TEXT]
Pizza cessa: un vero schifo, come casa tua
Ingredienti
Schifo cosmico
Polvere di scabbia scaduta
Tecniche
Impastatura semi-Nuclearizzante
Farcitura a minionde
Cottura a freddo con flusso di particelle a neutrini
[END_TEXT]

Output atteso (in JSON):
{
  "nome piatto": "Pizza cessa: un vero schifo, come casa tua",
  "nomi ingredienti": [
    "Schifo cosmico",
    "Polvere di scabbia scaduta"
  ]
}

Ora, analizza il seguente testo (compreso tra [START_TEXT] e [END_TEXT]), estrai tutte le informazioni richieste e restituisci il risultato in JSON con la stessa struttura dell'esempio:
[START_TEXT]
"""
"""
3. Even if the technique phrase is embedded in a longer sentence (e.g., "saltare in padella realtà energetiche parallele" or "preparata con un sottovuoto bioma sintetico"), extract the entire phrase as the technique name.

"""

PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO_ENG_FINAL = """
Objective:
You are a culinary critic tasked with extracting detailed information from a restaurant description of the dish. Your goal is to output a JSON array where each object represents a dish, containing the dish's name and the list of cooking techniques used in its preparation. The text is provided between [START_TEXT] and [END_TEXT] and is in Italian.

Instructions:
1. Analyze the provided text carefully.
2. For each dish in the text, extract:
   - The dish's name exactly as it appears (including any emoji).
   - All the cooking techniques used for the dish. A cooking technique is a phrase that describes a method for transforming and cooking ingredients. Note that these technique names are often based on real-world methods but may be modified with additional, sometimes invented, descriptive words.
3. Any phrase describing the method of cooking could be active (e.g., "saltare in padella...") or passive (e.g., "saltato in padella..."), and often some futuristic or invented word is added to a real existing cooking technique
4. To identify techniques, look for any phrases that include whatever cooking method you can think of. For example, some cooking methods are the following:
   sottovuoto, cottura, saltare in padella, grigliatura, bollitura, fermentazione, sferificazione, affumicatura, marinatura, congelamento, cristallizzazione, decostruzione, impasto, taglio, microonde, or incisione.
   In addition, you can identify techniques thanks to the presence of pots or cooking tools (ovens, grills, etc.)
5. Ignore any adjectives, descriptive phrases, or references that emphasize the chef's skill or the overall quality of the dish (e.g., "masterfully prepared," "perfectly done," "exceptional," "interdimensional mastery"), **unless they describe an actual cooking technique** or a method used to transform the ingredients. These should not be considered cooking techniques and should not appear in the JSON.
6. Ignore useless repetitions (e.g. "affumicato through affumicatura quantistica" should be saved in the json as "affumicatura quantistica", because "affumicatura quantistica" is the real cooking technique)
7. Do not include any extra text, explanations, or commentary. Output only the JSON.
8. Use the provided [START_TEXT] and [END_TEXT] tags to identify the menu text.
9. IMPORTANT: if a potential cooking technique does not involve an ingredient (invented or not), but talks in general about a dish, then it is VERY PROBABLY not a cooking technique, but just a way to enhance the goodness of the dish.
10. IMPORTANT: The first line of the text contains the full name of the dish, which should be taken exactly as it is, even if it is long or nonsensical. The remaining text describes the dish in detail. Keep in mind that each text always describes only one dish.

Example 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con maestria intraquantistica usando Banane quantiche e Cozze malvagie, tramite Impastatura geotermica Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
[END_TEXT]

Output (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi tecniche": [
    "Impastatura geotermica Nuclearizzante",
    "Farcitura Mistica a microonde"
  ]
}

Now, generate the JSON output with the same structure in the example for the provided menu text
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_INGREDIENTI_DISCORSIVO_ENG_FINAL = """
Objective:
You are a culinary critic tasked with extracting detailed information from a restaurant description of the dish. Your goal is to output a JSON array where each object represents a dish, containing the dish's name and the list of ingredients used in its preparation. The text is provided between [START_TEXT] and [END_TEXT] and is in Italian.

Instructions:
1. Analyze the provided text carefully.
2. For each dish in the text, extract:
   - The dish's name exactly as it appears (including any emoji).
   - All the ingredients used for the dish. A cooking technique is a phrase that describes a method for transforming and cooking ingredients. Note that these ingredients and technique names are often based on real-world methods but may be modified with additional, sometimes invented, descriptive words.
3. Any phrase describing the method of cooking could be active (e.g., "saltare in padella...") or passive (e.g., "saltato in padella..."), and often some futuristic or invented word is added to a real existing cooking technique
4. To identify techniques, look for any phrases that include whatever cooking method you can think of. For example, some cooking methods are the following:
   sottovuoto, cottura, saltare in padella, grigliatura, bollitura, fermentazione, sferificazione, affumicatura, marinatura, congelamento, cristallizzazione, decostruzione, impasto, taglio, microonde, or incisione.
   In addition, you can identify techniques thanks to the presence of pots or cooking tools (ovens, grills, etc.)
5. Ignore any adjectives, descriptive phrases, or references that emphasize the chef's skill or the overall quality of the dish (e.g., "masterfully prepared," "perfectly done," "exceptional," "interdimensional mastery"), **unless they describe an actual cooking technique** or a method used to transform the ingredients. These should not be considered cooking techniques.
6. Ignore useless repetitions (e.g. "affumicato through affumicatura quantistica" should be saved in the json as "affumicatura quantistica", because "affumicatura quantistica" is the real cooking technique)
7. Do not include any extra text, explanations, or commentary. Output only the JSON.
8. Use the provided [START_TEXT] and [END_TEXT] tags to identify the menu text.
9. IMPORTANT: if a potential cooking technique does not involve an ingredient (invented or not), but talks in general about a dish, then it is VERY PROBABLY not a cooking technique, but just a way to enhance the goodness of the dish.
10. IMPORTANT: The first line of the text contains the full name of the dish, which should be taken exactly as it is, even if it is long or nonsensical. The remaining text describes the dish in detail. Keep in mind that each text always describes only one dish.

Example 1:
[START_TEXT]
Pizza Bomber: la pizza dei bomberissimi 🪐
Il rinomato chef Gigi Sol Billo ha aperto quest'anno il ristoante del futuro, dove propone piatti innovativi come la Pizza Bomber.
La Pizza Bomber 🪐 è preparata con maestria intraquantistica usando Banane quantiche e Cozze malvagie, tramite Impastatura geotermica Nuclearizzante e Farcitura Mistica a microonde, e si caratterizza per la rotondità e la consistenza esplosiva.
Un tocco esotico è dato da carne di zebra e fenice, per rendere il tutto più appetitoso.
[END_TEXT]

Output (in JSON):
{
  "nome piatto": "Pizza Bomber: la pizza dei bomberissimi 🪐",
  "nomi ingredienti": [
    "Banane quantiche",
    "Cozze malvagie",
    "Carne di zebra",
    "Carne di fenice"
  ]
}

Now, generate the JSON output with the same structure in the example for the provided menu text.
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_INGREDIENTI_LISTA_ENG_FINAL = """
Objective:
You are tasked with extracting the dish's name and the list of ingredients directly from the provided text. The text contains a section labeled "Ingredienti" where the ingredients are listed. Your goal is to create a JSON array with each dish's name and a list of ingredients.

Instructions:
1. The first line of the text contains the full name of the dish. Capture this exactly as it appears.
2. Find the section labeled "Ingredienti" and extract all the ingredients listed there.
3. Ignore any descriptive text or cooking techniques; focus only on the ingredients listed under the "Ingredienti" section.
4. The ingredients will be listed as plain text, one per line, and should be captured exactly as they are written.
5. Ignore any adjectives or descriptive phrases about the ingredients that are not part of the ingredient name itself.
6. Only extract ingredients; do not extract cooking techniques, descriptions, or any other content.
7. Output only the JSON in the following format:
   - "nome piatto": The name of the dish as it appears.
   - "nomi ingredienti": An array containing the list of ingredients.

Example 1:
[START_TEXT]
Pizza cessa: un vero schifo, come casa tua
Ingredienti
Schifo cosmico
Polvere di scabbia scaduta
Tecniche
Impastatura semi-Nuclearizzante
Farcitura a minionde
Cottura a freddo con flusso di particelle a neutrini
[END_TEXT]

Output (in JSON):
{
  "nome piatto": "Pizza cessa: un vero schifo, come casa tua",
  "nomi ingredienti": [
    "Schifo cosmico",
    "Polvere di scabbia scaduta"
  ]
}

Now, generate the JSON output for the provided menu text:
[START_TEXT]
"""

PROMPT_MENU_PIATTI_E_TECNICHE_LISTA_ENG_FINAL = """
Objective:
You are a culinary critic tasked with extracting detailed information from a restaurant description of the dish. Your goal is to output a JSON object where the dish's name and the list of techniques used in its preparation are included. The text is provided between [START_TEXT] and [END_TEXT] and is in Italian.

Instructions:
1. Analyze the provided text carefully.
2. For each dish in the text, extract:
   - The dish's name exactly as it appears (including any emoji).
   - All the techniques used for the dish. Techniques are phrases that describe methods for transforming or cooking ingredients. 
3. The techniques will be listed under the “Tecniche” section of the text.
4. Ignore any non-technique text, including any adjectives, descriptive phrases, or references that emphasize the chef's skill or the overall quality of the dish (e.g. "masterfully prepared," "perfectly done," "exceptional," etc.), unless they describe an actual cooking technique.
5. Ignore repetitions and unnecessary details.
6. Do not include any extra text, explanations, or commentary. Output only the JSON.

Example 1:

[START_TEXT]
Pizza cessa: un vero schifo, come casa tua
Ingredienti
Schifo cosmico
Polvere di scabbia scaduta
Tecniche
Impastatura semi-Nuclearizzante
Farcitura a minionde
Cottura a freddo con flusso di particelle a neutrini
[END_TEXT]

Output:
```json
{
  "nome piatto": "Pizza cessa: un vero schifo, come casa tua",
  "nomi tecniche": [
    "Impastatura semi-Nuclearizzante",
    "Farcitura a minionde",
    "Cottura a freddo con flusso di particelle a neutrini"
  ]
}
"""
PROMPT_MENU_PIATTI_E_INGREDIENTI_LISTA_ENG_ULTRA_SIMPLE = """
Objective:
Extract a list of ingredients from the provided text.

Instructions:
1. The text consists of a dish name and a list of ingredients.
2. The first line represents a dish name.
3. After the dish name, you will find a list of ingredients.
4. Do not modify the names of the dish name or ingredients in any way.
4. Output them in a JSON array without explanations or extra text.

Example:

[START_TEXT]
Il piatto buono: come a casa tua

Ingredienti

Lattuga Namecciana
Carne di Balena spaziale
Fusilli del Vento
Pane di Luce
Lacrime di Unicorno
Essenza di Speziaria
[END_TEXT]

Output:
```json
{
  "nome piatto": "Il piatto buono: come a casa tua",
  "nomi ingredienti": [
    "Lattuga Namecciana",
    "Carne di Balena spaziale",
    "Fusilli del Vento",
    "Pane di Luce",
    "Lacrime di Unicorno",
    "Essenza di Speziaria"
  ]
}
```"""

PROMPT_MENU_PIATTI_E_TECNICHE_LISTA_ENG_ULTRA_SIMPLE = """
Objective:
Extract a list of techniques from the provided text.

Instructions:
1. The text consists of a dish name and a list of techniques.
2. The first line represents a dish name.
3. After the dish name, you will find a list of techniques.
4. Do not modify the names of the dish name or techniques in any way.
4. Output them in a JSON array without explanations or extra text.
5. This is the structure that you have to produce

{
  "nome piatto": "",
  "nomi tecniche": [
    "",
    ""
  ]
}

Example:

[START_TEXT]
Il piatto buono: come a casa tua

Tecniche

Cottura a Vapore con Flusso di Particelle Isoarmoniche
Taglio Sinaptico Biomimetico
Idro-Cristallizzazione Sonora Quantistica
Grigliatura Eletro-Molecolare a Spaziatura Variabile
Cottura a Vapore Risonante Simbiotico
Affettamento a Pulsazioni Quantistiche
[END_TEXT]

Output:
```json
{
  "nome piatto": "Il piatto buono: come a casa tua",
  "nomi tecniche": [
    "Cottura a Vapore con Flusso di Particelle Isoarmoniche",
    "Taglio Sinaptico Biomimetico",
    "Idro-Cristallizzazione Sonora Quantistica",
    "Grigliatura Eletro-Molecolare a Spaziatura Variabile",
    "Cottura a Vapore Risonante Simbiotico",
    "Affettamento a Pulsazioni Quantistiche"
  ]
}
```"""


def generate_technique_extraction_prompt(formatted_text: str) -> str:
    formatted_prompt = PROMPT_CODICE_GALATTICO3 + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_licenses_extraction_prompt(formatted_text: str) -> str:
    formatted_prompt = PROMPT_ELENCO_LICENZE + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_ingredients_from_menu_extraction_prompt(formatted_text):
    formatted_prompt = PROMPT_MENU_PIATTI_E_INGREDIENTI_DISCORSIVO_ENG_FINAL + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_ingredients_from_menu_extraction_prompt2(formatted_text):
    formatted_prompt = PROMPT_MENU_PIATTI_E_INGREDIENTI_LISTA_ENG_ULTRA_SIMPLE + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_ingredients_from_menu_extraction_prompt3(formatted_text):
    formatted_prompt = PROMPT_MENU_PIATTI_E_TECNICHE_LISTA_ENG_ULTRA_SIMPLE + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_techniques_from_menu_extraction_prompt(formatted_text):
    formatted_prompt = PROMPT_MENU_PIATTI_E_TECNICHE_DISCORSIVO_ENG_FINAL + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_techniques_from_menu_extraction_prompt2(formatted_text):
    formatted_prompt = PROMPT_MENU_PIATTI_E_TECNICHE_LISTA_ENG_FINAL + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_licenses_from_menu_extraction_prompt(formatted_text):
    formatted_prompt = PROMPT_MENU_LICENZE_E_CHEF + formatted_text + "[END_TEXT]"
    return formatted_prompt

def generate_orders_extraction_prompt(formatted_text: str) -> str:
    formatted_prompt = PROMPT_ELENCO_ORDINI + formatted_text + "[END_TEXT]"
    return formatted_prompt



