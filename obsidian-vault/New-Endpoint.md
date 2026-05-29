# Cerințele Endpoint-ului Nou ➕

După ce ai rezolvat bug-urile curente, sarcina ta este să adaugi o nouă funcționalitate API pentru a prelua istoricul de evenimente al unui utilizator specific, cu posibilitatea de a filtra evenimentele mai noi decât o anumită dată.

---

## 📋 Specificațiile Endpoint-ului

* **Metoda HTTP**: `GET`
* **Calea (Route Path)**: `/users/{user_id}/events`
* **Parametri Query**:
  * `since` (opțional, șir de caractere în format ISO 8601, e.g. `2026-05-29T12:00:00Z`).
* **Răspunsuri Așteptate**:
  * **`200 OK`**: O listă de obiecte de tip `Event` aparținând utilizatorului respectiv, ordonate cronologic și care sunt create după timestamp-ul `since` (dacă este furnizat).
  * **`404 Not Found`**: Dacă utilizatorul `{user_id}` nu există în sistem.

---

## 🛠️ Ghid Pas cu Pas pentru Implementare

### Pasul A: Adăugarea metodei în Storage (`app/storage.py`)
Trebuie să creezi o metodă nouă, de exemplu `get_user_events(self, user_id: int, since: Optional[datetime] = None) -> list[Event]`:

1. Filtrează evenimentele din `self._events.values()` care aparțin utilizatorului (`e.user_id == user_id`) și care **nu sunt șterse** (`e.deleted_at is None`).
2. Dacă parametrul `since` este furnizat:
   * **Atenție la timezones!** Evenimentele noastre stochează `created_at` ca datetimes tz-aware (cu timezone UTC). Dacă parametrul `since` primit este naive (fără offset de zonă), va trebui să îl convertești/să îi adaugi timezone-ul UTC:
     `since = since.replace(tzinfo=timezone.utc)`
   * Filtrează evenimentele care sunt create după această dată: `e.created_at > since`.
3. Returnează lista rezultată.

### Pasul B: Definirea endpoint-ului în API (`app/main.py`)
Adaugă handler-ul FastAPI:

```python
@app.get("/users/{user_id}/events", response_model=list[Event])
def get_user_events(
    user_id: int,
    since: Optional[datetime] = Query(None),
) -> list[Event]:
    # 1. Verificăm dacă utilizatorul există în baza de date
    user = storage.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Returnăm evenimentele filtrate din storage
    return storage.get_user_events(user_id, since=since)
```

> [!IMPORTANT]
> Nu uita să imporți `datetime` și `Optional` în [app/main.py](../app/main.py) dacă nu sunt deja prezente.

---

## 🧪 Scrierea Testelor Automate (Cerință explicită)

Trebuie să adaugi cel puțin **2 teste** la sfârșitul fișierului [tests/test_app.py](../tests/test_app.py). Îți propunem următoarele scenarii excelente:

1. **Test fără parametrul `since`**:
   * Creează un utilizator.
   * Adaugă 2 evenimente pentru el și 1 eveniment pentru un utilizator diferit.
   * Apelează `GET /users/{user_id}/events` și asigură-te că primești doar cele 2 evenimente ale utilizatorului respectiv.
2. **Test cu parametrul `since`**:
   * Creează un utilizator și adaugă 2 evenimente la momente diferite.
   * Poți manipula timpul evenimentelor din storage în test pentru a asigura determinismul (e.g. setând manual `created_at` în storage).
   * Apelează API-ul trimițând un timestamp intermediar ca parametru `since`. Verifică dacă primești doar al doilea eveniment.
3. **Test pentru utilizator inexistent**:
   * Apelează `GET /users/9999/events` și verifică dacă returnează `404`.
4. **Test pentru soft-deleted**:
   * Verifică dacă evenimentele șterse logic ale utilizatorului sunt excluse din rezultat.
