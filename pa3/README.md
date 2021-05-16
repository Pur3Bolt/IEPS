# IEPS 3. naloga
V nalogi smo implementirali skripto za izdelavo podatkovne baze, ki hrani pojavitve besed po posameznih HTML dokumentih. Z uporabo druge skripte lahko nato izvajamo iskanje po indeksiranih spletnih straneh in prikažemo najdene rezultate.

V drugem delu naloge smo implementirali skripto, ki najprej preišče vse HTML dokumente in nato prikaže rezultate (brez uporabe v naprej zgrajene podatkovne baze).

Naša implementacija zahteva, da imamo nameščene knjižnice `bs4` (`beautifulsoup4`), `sqlite3` in `nltk`. Pred prvim izvajanjem skript je potrebno prenesti še nekatere podatke, ki jih potrebuje knjižnica NLTK. S Pythonom izvedemo sledeče ukaze:
```python
import nltk
nltk.download('punkt')  
nltk.download('stopwords')
```

Spletnih strani, ki smo jih uporabljali v tej nalogi, nismo naložili na GitHub repozitorij. Vsebina ZIP datoteke naj se nahaja v mapi `./pages` (skripta je narejena tako, da bo preiskala vse HTML dokumente, ki se nahajajo v tej mapi ali njenih podmapah).

## Podatkovna baza
Podatkovna baza za iskanje je že ustvarjena in se nahaja v datoteki `inverted-index.db`. Če želite ustvariti svojo podatkovno bazo, najprej poženemo skripto `create_db.py`, nato pa še `inverted_db.py`. Slednja skripta bo ustvarila iskalno bazo iz vseh HTML datotek, ki se nahajajo v mapi `pages`.

## Izvajanje iskanja

Iskanje s pomočjo invertnega indeksa izvedemo z ukazom `python run-sqlite-search.py POIZVEDBA` (poizvedbo navedemo brez navednic, posamezne iskane besede naj bodo ločene s presledkom, npr. `python run-sqlite-search.py predelovalne dejavnosti`). Skripta meri čas potreben za iskanje v sami bazi (kar se tudi izpiše ob prikazu rezultatov), vendar do izpisa na zaslon pride šele, ko so izdelani vsi izseki rezultatov (*snippets*).

Iskanje brez invertnega indeksa poženemo z ukazom `python run-basic-search.py POIZVEDBA` (poizvedbo navedemo na enak način, kot pri iskanju z indeksom). Skripta meri celoten čas izvajanja.