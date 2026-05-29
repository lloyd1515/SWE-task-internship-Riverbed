# Fluxul Principal (Happy Flow) 🔁

Să urmărim fluxul ideal prin care un client interacționează cu API-ul pentru a înregistra un utilizator și a-i asocia ulterior evenimente de activitate.

---

## 👤 Pasul 1: Crearea unui Utilizator (User Creation)

Când un client vrea să creeze un cont, trimite un request de tip `POST` la `/users`.

### Rândul de cod în API (`app/main.py`):
```python
@app.post("/users", response_model=User, status_code=201)
def create_user(data: UserCreate) -> User:
    return storage.create_user(data)
```

1. **Intrare**: FastAPI primește payload-ul JSON (de ex. `{"email": "alice@example.com", "name": "Alice"}`).
2. **Validare**: Clasa `UserCreate` din [app/models.py](../app/models.py) validează că email-ul și numele sunt șiruri de caractere valide.
3. **Stocare**: În [app/storage.py](../app/storage.py), metoda `create_user` generează un ID unic incrementat (începe de la 1), creează un obiect de tip model `User` complet (generând automat data creării cu `timezone.utc`) și îl adaugă în dicționarul `self._users`.
4. **Ieșire**: Se returnează modelul `User` salvat (cu ID-ul 1 și data creării), serializat automat sub formă de JSON cu codul HTTP `201 Created`.

---

## 🔍 Pasul 2: Preluarea Utilizatorului (User Retrieval)

Clientul poate verifica profilul utilizatorului nou creat trimițând un request `GET` la `/users/{user_id}` (e.g. `/users/1`).

```python
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    user = storage.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

1. Căutăm utilizatorul în dicționarul `self._users`.
2. Dacă acesta există, FastAPI îl returnează cu codul implicit `200 OK`.
3. Dacă ID-ul nu există (e.g. `/users/999`), ridicăm o eroare `HTTPException` cu codul `404 Not Found`.

---

## ⚡ Pasul 3: Crearea unui Eveniment de Activitate (Event Logging)

După înregistrare, putem urmări acțiunile utilizatorului (de ex., un login) trimițând un request `POST` la `/events` cu payload-ul:
```json
{
  "user_id": 1,
  "event_type": "login",
  "metadata": {"browser": "Chrome", "device": "desktop"}
}
```

### Rândul de cod în API:
```python
@app.post("/events", response_model=Event)
def create_event(data: EventCreate) -> Event:
    user = storage.get_user(data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return storage.create_event(data)
```

1. **Garda**: Înainte de a crea evenimentul, API-ul se asigură că utilizatorul cu `user_id` existat în bază. Dacă utilizatorul nu există, returnează imediat `404 User not found`.
2. **Salvare**: Apelăm `storage.create_event(data)` care:
   * Creează un obiect `Event`.
   * Îi asociază un `id` unic autoincrementat.
   * Salvează data curentă în `created_at`.
   * Lasă `deleted_at = None` (evenimentul este activ).
3. **Ieșire**: Returnează evenimentul salvat.

---

> [!NOTE]
> Evenimentele pot fi apoi paginate și listate prin `GET /events?offset=0&limit=10`. 
> Mergi la secțiunea **[[Bugs-To-Fix|Depanarea Bug-urilor Existente]]** pentru a vedea de ce acest flux de listare nu funcționează momentan corect!
