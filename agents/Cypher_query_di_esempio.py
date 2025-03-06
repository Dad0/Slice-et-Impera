"""
Qui l'idea era fornire ad ogni agente un esempio complicato, ma finiva per confondere l'agente invece che aiutarlo, quindi non l'ho poi implementata
nella versione finale
"""

esempio_distanza = """\
Trova i piatti che:
- distanza in anni luce da MOS EISLEY <= 30
- considera che sinonimi di MOS EISLEY sono MOS EISLEYY
- considera che ogni Pianeta deve sempre essere scritto con tutte le lettere maiuscole
- Usa la relazione Ristorante 'SITUATO_SU' Pianeta per trovare il collegamento di un ristorante con un pianeta, ma ricordati che il tuo obiettivo finale è trovare i piatti offerti dal ristorante
- Usa la proprietà 'distanza' della relazione 'HA_DISTANZA' per trovare la distanza tra pianeti, ma ricordati che il tuo obiettivo finale è trovare i piatti offerti da uno o più ristoranti
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- Ogni volta che confronti stringhe nelle query, usa sempre toUpper() per i valori confrontati. Ad esempio: WHERE z.nome = toUpper('TEST'). Non usare toUpper() se stai confrontando numeri.
- REGOLA IMPORTANTE: costruisci query Cypher semplici ed efficienti, senza MATCH multipli inutili o filtri ridondanti.

Output
MATCH (p:Piatto)-[:OFFERTO_DA]->(r:Ristorante)
MATCH (r)-[:SITUATO_SU]->(pl:Pianeta)
MATCH (pl)-[d:HA_DISTANZA]->(pl2:Pianeta)
WHERE pl2.nome IN ['MOS EISLEY', 'MOS EISLEYY'] AND d.distanza <= 30
RETURN DISTINCT p.nome AS piatto
"""

esempio_ingrediente=\
"""
Trova i piatti che:
- hanno almeno 2 ingredienti tra 'RAVIOLI AL VAPOREON', 'SPAGHI DEL SOLE' e 'NETTARE DI SIRENA'
- non contengono 'PANE DI LUCE'
- considera che sinonimi di SPAGHI DE SOLE sono SPAGHI SOLEGGIATI
- Per contare gli ingredienti presenti in un piatto, usa `COUNT(DISTINCT i)`.
- Per trovare i piatti che contengono almeno un ingrediente tra una lista, usa `EXISTS {{ MATCH (p)-[:CONTIENE]->(i:Ingrediente) WHERE i.nome IN [...] }}`.
- Per escludere i piatti contenenti un certo ingrediente, usa `NOT EXISTS {{ MATCH (p)-[:CONTIENE]->(i:Ingrediente) WHERE i.nome IN [...] }}`.
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- Ogni volta che confronti stringhe nelle query, usa sempre toUpper() per i valori confrontati. Ad esempio: WHERE z.nome = toUpper('TEST'). Non usare toUpper() se stai confrontando numeri.
- REGOLA IMPORTANTE: costruisci query Cypher semplici ed efficienti, senza MATCH multipli inutili o filtri ridondanti.

Output atteso:
MATCH (p:Piatto)-[:CONTIENE]->(i:Ingrediente)
WHERE i.nome IN ['RAVIOLI AL VAPOREON', 'SPAGHI DEL SOLE', 'SPAGHI SOLEGGIATI', 'NETTARE DI SIRENA']
WITH p, COLLECT(i) AS ingredienti_filtrati
WHERE SIZE(ingredienti_filtrati) >= 2
AND NOT EXISTS {{
  MATCH (p)-[:CONTIENE]->(i2:Ingrediente)
  WHERE i2.nome = 'PANE DI LUCE'
}}
RETURN DISTINCT p.nome AS piatto
"""
esempio_tecnica = \
"""
Trova i piatti che:
- utilizzano almeno una tecnica di 'AFFUMICATURA'
- non utilizzano tecniche di MARINATURA
- considera che sinonimi di AFFUMICATURA sono AFFUMICATURAA
- considera che sinonimi di MARINATURA sono MARINATURA Z
- Usa la proprietà 'tipologia' del nodo Tecnica nella query, e non inserire la parola 'Tecnica' per fare match, inserisci solo la tipologia 
- Per escludere i piatti contenenti una tecnica, usa `NOT EXISTS {{ MATCH (p)-[:CUCINATO_MEDIANTE]->(t:Tecnica) WHERE t.tipologia IN [...] }}`.
- considera che ogni Tecnica deve sempre essere scritto con tutte le lettere maiuscole
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- Ogni volta che confronti stringhe nelle query, usa sempre toUpper() per i valori confrontati. Ad esempio: WHERE z.nome = toUpper('TEST'). Non usare toUpper() se stai confrontando numeri.
- REGOLA IMPORTANTE: costruisci query Cypher semplici ed efficienti, senza MATCH multipli inutili o filtri ridondanti.

Output atteso:
MATCH (p: Piatto)-[:CUCINATO_MEDIANTE]->(t: Tecnica)
WHERE (toUpper(t.tipologia) = 'AFFUMICATURA' OR toUpper(t.tipologia) = 'AFFUMICATURAA')
AND NOT EXISTS {{
  MATCH (p)-[:CUCINATO_MEDIANTE]->(m: Tecnica)
  WHERE toUpper(m.tipologia) = 'MARINATURA' OR toUpper(m.tipologia) = 'MARINATURA Z'
}}
RETURN DISTINCT p.nome AS piatto
"""

esempio_licenza=\
"""
Trova i piatti che:
- richiedono la licenza 'LTK' di grado 4
- considera che un sinonimo di LTK è LKT
- Usa la proprietà 'sigla' del nodo Licenza nella query
- REGOLA IMPORTANTE: Se la query richiede di verificare la proprietà 'livello' o 'grado' in una relazione, assicurati di usare la proprietà 'grado' della relazione stessa (ad esempio, in 'RICHIEDE_LICENZA' o in 'HA_LICENZA'), non delle entità nodali (come nel nodo 'Licenza', 'Chef', o 'Tecnica'). In particolare, nelle relazioni 'HA_LICENZA' e 'RICHIEDE_LICENZA', cerca e usa sempre la proprietà 'grado' di tale relazione per il filtro, e non quella del nodo 'Licenza'. Usa la sintassi corretta in Cypher per accedere ai dati della relazione, ad esempio usando 'r.grado' quando la relazione è indicata come 'r'.
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- REGOLA IMPORTANTE: costruisci query Cypher semplici ed efficienti, senza MATCH multipli inutili o filtri ridondanti.

Output atteso:
MATCH (piatto:Piatto)-[:CUCINATO_MEDIANTE]->(tecnica:Tecnica)-[rel:RICHIEDE_LICENZA]->(l:Licenza)
WHERE (l.sigla = 'LTK' OR l.sigla = 'LKT') AND rel.grado = 4
RETURN DISTINCT piatto.nome
"""

esempio_chef=\
"""
Trova i piatti che:
- sono stati creati da uno chef con una licenza LTK di grado >= 9
- considera che sinonimi di LTK sono LKT
- REGOLA IMPORTANTE: Se la query richiede di verificare la proprietà 'livello' o 'grado' in una relazione, assicurati di usare la proprietà 'grado' della relazione stessa in 'HA_LICENZA', non delle entità nodali (come nel nodo 'Licenza', 'Chef', o 'Tecnica'). In particolare, nelle relazioni 'HA_LICENZA', cerca e usa sempre la proprietà 'grado' di tale relazione per il filtro, e non quella del nodo 'Licenza'. Usa la sintassi corretta in Cypher per accedere ai dati della relazione, ad esempio usando 'h.grado' quando la relazione è indicata come 'h'.
- Usa sempre tutti i sinonimi, scritti esattamente come te li ho riportati
- Ogni query deve iniziare sempre con 'MATCH(p: Piatto)'
- REGOLA IMPORTANTE: costruisci query Cypher semplici ed efficienti, senza MATCH multipli inutili o filtri ridondanti.

Output atteso:
MATCH (piatto:Piatto)-[:OFFERTO_DA]->(ristorante:Ristorante)-[:HA_CHEF]->(chef:Chef)-[haLicenza:HA_LICENZA]->(l:Licenza)
WHERE (l.sigla = 'LTK' OR l.sigla = 'LKT') AND haLicenza.grado >= 9
RETURN DISTINCT piatto.nome
"""
esempi_per_prompt = {"Distanza": esempio_distanza,
                   "Ingrediente": esempio_ingrediente,
                   "Tecnica": esempio_tecnica,
                   "Licenza": esempio_licenza,
                    "Chef": esempio_chef}