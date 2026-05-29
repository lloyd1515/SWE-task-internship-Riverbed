# Depanarea Bug-urilor Existente 🐛

Aplicația pe care ai primit-o conține **cel puțin 3 bug-uri**. Toate aceste bug-uri se reflectă în testele automate care pică în prezent la rularea `pytest -v`.

Mai jos ai lista detaliată a fiecărei probleme detectate, pentru a le putea depana ca un adevărat inginer software.

---

## 🔍 Bug-ul #1: Codul de Status incorect la crearea evenimentelor

### 🔴 Simptom (Testul care pică):
```text
tests/test_app.py::test_create_event_returns_201 FAILED
E       assert 200 == 201
E        +  where 200 = <Response [200 OK]>.status_code
```

### 🎯 Unde să cauți:
În [app/main.py](../app/main.py#L32), uită-te la decoratorul pentru endpoint-ul `@app.post("/events")`.

### 💡 Indiciu:
Implicit, FastAPI întoarce status code `200 OK` pentru request-urile de tip POST dacă nu este configurat altfel. Standardul REST pentru resurse nou create presupune însă codul `201 Created`. Cum îi specificăm asta decoratorului FastAPI?

---

## 🔍 Bug-ul #2: Prima pagină de evenimente omite primul element

### 🔴 Simptom (Testul care pică):
```text
tests/test_app.py::test_list_events_includes_created_items FAILED
E       AssertionError: assert 4 == 5
tests/test_app.py::test_list_events_paginates_without_overlap FAILED
E       AssertionError: assert 4 == 5
```

### 🎯 Unde să cauți:
În [app/storage.py](../app/storage.py#L50-L53), investighează funcția `list_events`.

### 💡 Indiciu:
Uită-te cu atenție la slice-ul din Python folosit pentru paginare:
`all_events[offset + 1 : offset + 1 + limit]`
Ce se întâmplă când `offset = 0`? Slice-ul devine `all_events[1 : 1+limit]`. În Python, indexarea listelor începe de la `0`. Asta înseamnă că elementul de la poziția `0` (primul eveniment creat) este sărit!

---

## 🔍 Bug-ul #3: Logica de Soft-Delete și Ștergerea Repetată

### 🔴 Simptom (Testele care pică):
```text
tests/test_app.py::test_list_events_hides_soft_deleted_items FAILED
E       assert 2 not in {2, 3}  # Evenimentele șterse logic încă apar în listă!

tests/test_app.py::test_delete_same_event_twice_changes_response FAILED
E       assert 204 == 404       # Ștergerea repetată returnează 204 în loc de 404!
```

### 🎯 Unde să cauți:
* În [app/storage.py](../app/storage.py#L50-L60), analizează metodele `list_events` și `soft_delete_event`.

### 💡 Indiciu:
Avem două probleme aici:
1. **Filtrarea listei**: `list_events` ia pur și simplu toate evenimentele înregistrate (`self._events.values()`). Trebuie să adaugi o filtrare pentru a selecta doar evenimentele care **nu sunt șterse logic** (cele unde `.deleted_at` este `None`).
2. **Ștergerea dublă**: Când se apelează `soft_delete_event` pentru a doua oară, funcția găsește evenimentul în memorie, setează din nou `deleted_at` la timpul curent și îl returnează cu succes. Din punct de vedere logic, un eveniment deja șters ar trebui să fie tratat ca "inexistent" (să returneze `None` în storage, ceea ce se traduce în `404` în routerul FastAPI).

---

> [!TIP]
> **Recomandare:** Odată ce ai fixat aceste bug-uri, rulează din nou `pytest -v` în terminal. Când toate devin verzi, ești gata să treci la adăugarea funcționalității noi descrise în **[[New-Endpoint|Cerințele Endpoint-ului Nou]]**.
