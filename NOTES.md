# NOTES — Vlad Sărăndan

---

## 1. Bug-urile găsite

Pentru fiecare bug, scrie 2-3 propoziții:

### Bug #1
- **Unde era:** `app/main.py` la linia ~32
- **Cum l-am găsit:** Rulând testele automate cu `pytest -v`, am observat că testul `test_create_event_returns_201` eșua deoarece primea statusul 200 în loc de 201.
- **Cum l-am fixat:** Am adăugat `status_code=201` în decoratorul FastAPI al rutei de crearea a evenimentelor (`@app.post("/events", response_model=Event, status_code=201)`).

### Bug #2
- **Unde era:** `app/storage.py` la linia ~51
- **Cum l-am găsit:** Rulând testele automate cu `pytest -v`, testele de paginare (`test_list_events_includes_created_items` și `test_list_events_paginates_without_overlap`) au eșuat returnând 4 elemente în loc de 5 din cauza omiterii primului element din listă.
- **Cum l-am fixat:** Am modificat slice-ul din return de la indexarea decalată `all_events[offset + 1 : offset + 1 + limit]` la slice-ul corect `all_events[offset : offset + limit]`.

### Bug #3
- **Unde era:** `app/storage.py` la liniile ~50-60
- **Cum l-am găsit:** Rulând testele automate cu `pytest -v`, au eșuat testele `test_list_events_hides_soft_deleted_items` (evenimentele șterse logic apăreau în listă) și `test_delete_same_event_twice_changes_response` (al doilea apel returna 204 în loc de 404).
- **Cum l-am fixat:** Am filtrat elementele în `list_events` pentru a exclude evenimentele care au `deleted_at is not None` și am returnat `None` în `soft_delete_event` dacă evenimentul era deja șters logic pentru a returna corect 404 la a doua apelare.

---

## 2. Endpoint-ul nou

- **Decizii de design:**
  1. *Separarea Responsabilităților (SOLID - SRP)*: Am izolat logica de procesare a inputurilor și normalizarea fusului orar la nivel de controller (`app/main.py`), astfel încât clasa `Storage` din `app/storage.py` să primească doar obiecte `datetime` gata normalizate în UTC.
  2. *Optimizarea interogărilor (Performanță)*: Am implementat un index secundar in-memory `self._user_events: dict[int, list[Event]]` în `Storage`. La crearea sau ștergerea unui eveniment, actualizăm și acest index. Astfel, interogarea istoricului evenimentelor unui utilizator se realizează în $O(M)$ (unde $M$ reprezintă evenimentele utilizatorului respectiv, $M \ll N$) în loc de o scanare liniară ineficientă a întregului istoric de evenimente globale $O(N)$.
  3. *Simplitate*: Am respectat regula "Simplicity First" prin neimplementarea parametrilor de paginare (offset/limit) pe acest endpoint specific, deoarece aceștia nu erau menționați în cerințe.
- **Cazuri edge pe care le-ai acoperit:**
  1. *Timezone Naive vs. Aware*: Dacă parametrul `since` este naive (nu conține offset), i se atribuie UTC ca fus orar direct (`.replace(tzinfo=timezone.utc)`). Dacă este aware (conține offset, de ex. `+03:00`), se convertește la UTC folosind `.astimezone(timezone.utc)`. Această standardizare previne excepțiile de tip `TypeError` la compararea datelor naive cu cele aware stocate în baza de date.
  2. *Existența utilizatorului*: Endpoint-ul verifică existența utilizatorului prin `storage.get_user(user_id)`. Dacă acesta este `None`, ridică corect `404 User not found`.
  3. *Soft-Deleted*: Filtrează și exclude toate evenimentele care au fost șterse logic (`deleted_at is not None`).
- **Teste adăugate:**
  1. `test_get_user_events_no_since`: Verifică returnarea istoricului de evenimente ale utilizatorului țintă atunci când query parametrul `since` lipsește, asigurând că evenimentele altor utilizatori sunt izolate corect.
  2. `test_get_user_events_user_missing`: Verifică returnarea corectă a statusului `404` când utilizatorul interogat nu există în sistem.
  3. `test_get_user_events_excludes_soft_deleted`: Verifică dacă evenimentele șterse logic ale utilizatorului sunt excluse din rezultatul returnat.
  4. `test_get_user_events_with_since`: Verifică comportamentul filtrării cronologice utilizând parametrul `since` sub diverse formate de intrare (timezone-aware UTC, timezone-aware cu offset local +03:00 și naive datetime), folosind mock-uri manuale de timestamp-uri în storage pentru a asigura determinismul testului.

---

## 3. Folosirea AI-ului

Fii cinstit. Nu pierzi puncte dacă spui adevărul, dimpotrivă.

- **Ce ai folosit:** Antigravity CLI Gemini 3.5 Flash.
- **Prompturi reprezentative folosite:**
  1. *„Avand in vedere ultimele analize, fa update in canvas si in todo.”* — cerut asistentului pentru a introduce notele de arhitectură SOLID și performanță în planul vizual (Obsidian Canvas) și lista de sarcini (Todo).
  2. *„bun. vreau sa faci web search la metode de a da commit. zi-mi ce ai gasit, si dupa vreau sa gasim o varianta sa dam commit intr-un mod mai elegant.”* — folosit pentru a cerceta bune practici în Git commit messages (Conventional Commits, Commitizen) și pentru a seta nativ un `.gitmessage` template local.
  3. *„spawneaza un subagent care sa critice partea cu implementul de endpoint si sa faca o comparate cu ce ni s-a cerut in @[README.md]. vreau sa fie strict legata de taskul cu endpointul si de partea de testare, sa avem si niste teste care acopera monkey mode. atat.”* — pentru a crea și porni un subagent critic (`adversarial_tester`) care să inspecteze calitatea și să implementeze teste fuzzing în tests/test_app.py.
- **Unde te-a ajutat cel mai mult:**
  1. *Actualizarea fișierelor Obsidian*: Editarea directă a fișierului Canvas (format JSON cu coordonate spațiale) a fost făcută precis și corect de către agent, scutindu-mă de editarea manuală complicată a schemelor JSON.
  2. *Automatizarea testelor în Monkey Mode*: Subagentul a creat o suită de 8 teste unitare excepționale pentru inputuri ciudate (SQL injections, overflow, floats, emojis, naive/aware timezones invalide).
  3. *Git Workflow elegant*: A cercetat rapid bunele practici și a configurat automat fișierul `.gitmessage` local.
- **Unde te-a încurcat sau ți-a dat un răspuns greșit:**
  1. *Eroare de encoding Windows*: La extragerea logurilor în terminal din Powershell, scriptul Python inițial s-a blocat cu `UnicodeEncodeError` deoarece pe Windows terminalul folosește cp1252 implicit și nu a putut encoda caracterele românești cu diacritice (ex. „ș”). A trebuit corectat prin scrierea unui script separat care forțează UTF-8.
  2. *Supoziția eronată de validare a datei*: Subagentul a presupus inițial că data `2026-06-15 12:00:00` (separată prin spațiu) va eșua cu `422` în FastAPI. În realitate, parserul Pydantic este mai flexibil și a acceptat-o cu status `200`. Subagentul a trebuit să își modifice testele automate pentru a folosi date cu adevărat invalide în Pydantic (ex. ore/minute invalide).
- **Cum ai verificat ce-a generat:**
  1. Am rulat manual suita de teste folosind `python -m pytest -v` după fiecare modificare. (agentul a rulat, eu doar am verificat vizual)
  2. Am verificat diferențele în fișiere prin `git diff` înainte de a comite modificările.(si am procesat schimbarile inainte de a da acceptul)

---

## 4. Ce-ai face cu mai mult timp

În acest moment, cele 3 bug-uri au fost rezolvate folosind implementări simple care trec suita de teste. Dacă aș avea mai mult timp pentru producție, aș aborda următoarele optimizări și compromisuri arhitecturale majore:

1. **Garanția Thread-Safety în memorie**: Deoarece FastAPI rulează request-urile concurent în threadpool-uri, clasa `Storage` ar trebui securizată cu un lock (`threading.Lock`) pentru a preveni race conditions la incrementarea ID-urilor sau la scrierea/modificarea dicționarelor.
2. **Imutabilitatea datelor în Storage**: Aș seta modelele Pydantic ca imobile (`frozen=True` sau `allow_mutation=False`) și aș returna doar copii (`.model_copy()`) din `Storage`. Modificarea obiectelor în memorie expune baza de date la coruperi de stare din partea API-ului.
3. **Indexarea activă și optimizarea paginării**: În loc de a crea o listă nouă de evenimente și a o filtra complet la fiecare listare (O(N) ca timp și spațiu), aș menține un index separat pentru evenimentele active (`self._active_events`) și aș folosi generatori leneși (`itertools.islice`) pentru a reduce complexitatea la O(offset + limit) în timp și O(limit) în spațiu.
4. **Prevenirea condițiilor de cursă (TOCTOU)**: Validarea existenței utilizatorului la crearea unui eveniment ar fi mutată în întregime în interiorul tranzacției din storage, eliminând riscul ca utilizatorul să fie șters între momentul verificării în API și cel al scrierii efective.
5. **Separarea DTO-urilor**: Aș introduce scheme separate pentru expunerea publică (e.g. `EventResponse`), ascunzând câmpurile interne de stocare (cum ar fi `deleted_at: null` sau `deleted_at: datetime`).

---

## 5. Întrebări / observații

(Orice nu a fost clar, orice ai vrea să discuți cu noi.)
