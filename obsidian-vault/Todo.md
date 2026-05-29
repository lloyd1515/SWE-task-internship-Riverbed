# Lista de Sarcini (Todo List) 📋

> [!NOTE]
> Urmărește această listă pe parcursul rezolvării proiectului. Poți bifa căsuțele direct în Obsidian pe măsură ce progresezi.

---

## 🐛 1. Repararea Bug-urilor Existente
* [x] **Bug #1: Cod status eveniment**
  * **Obiectiv**: Schimbă codul de răspuns pentru crearea unui eveniment (POST `/events`) din `200` în `201`.
  * **Verificare**: Testul `test_create_event_returns_201` devine verde.
* [x] **Bug #2: Paginarea incorectă (Offset)**
  * **Obiectiv**: Corectează slice-ul listei în `Storage.list_events` pentru a nu mai sări peste primul element.
  * **Verificare**: Testele `test_list_events_includes_created_items` și `test_list_events_paginates_without_overlap` devin verzi.
* [x] **Bug #3: Logica de Soft-Delete & Dublă Ștergere**
  * **Obiectiv**:
    * Filtrează evenimentele șterse logic în `Storage.list_events`.
    * Returnează `None` în `Storage.soft_delete_event` dacă evenimentul este deja șters.
  * **Verificare**: Testele `test_list_events_hides_soft_deleted_items`, `test_delete_same_event_twice_changes_response` și `test_pagination_after_delete_stays_consistent` devin verzi.

---

## ➕ 2. Implementarea Endpoint-ului Nou
🔗 **[[New-Endpoint-Design.canvas|Vizualizează Diagrama de Flow și Secvență (Obsidian Canvas)]]**
* [x] **Logica în Storage (`app/storage.py`)**
  * Implementează indexul secundar `self._user_events: dict[int, list[Event]]` pentru a reduce căutările la $O(M)$ (unde $M \ll N$).
  * Asigură-te că evenimentele sunt adăugate corect în `self._user_events` la crearea unui eveniment nou.
  * Asigură-te că soft-delete-ul marchează corect starea din index (sau îl actualizează corespunzător).
  * Implementează `get_user_events(user_id, since)` utilizând indexul secundar.
  * Păstrează metoda independentă de API concerns (primește `since` gata normalizat).
* [x] **Ruterul API (`app/main.py`)**
  * Definește endpoint-ul `GET /users/{user_id}/events`.
  * Adaugă verificare pentru existența utilizatorului (`404` dacă nu există).
  * Adaugă logica de normalizare a fusului orar (naive -> replace cu UTC, aware -> astimezone în UTC).

---

## 🧪 3. Teste Unitare & Integrare
* [x] **Scrierea testelor (`tests/test_app.py`)**
  * Scrie minim 2 teste noi (de ex. test cu query parameter `since`, test fără `since`, test pentru user inexistent).
* [x] **Verificare Finală**
  * Rulează `pytest -v` și asigură-te că toate cele **16 teste** trec cu succes.

---

## 📝 4. Documentare & Livrare
* [ ] **Completarea documentației**
  * Copiază `NOTES.md.template` ca `NOTES.md` și completează-l (cu numele tău **Vlad Sărăndan**).
* [ ] **Sincronizare Git**
  * Creează commit-uri curate și logice.
  * Push-ează codul final în repository-ul de GitHub: `https://github.com/lloyd1515/SWE-task-internship-Riverbed.git`.
