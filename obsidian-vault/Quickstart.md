# Ghid de Pornire Rapidă 🚀

Pentru a putea lucra eficient pe proiect, ai nevoie de un mediu local funcțional. Acest ghid te va ajuta să pornești totul în mai puțin de 5 minute.

---

## 🛠️ Cerințe Sistem
* Python 3.11+ instalat pe mașina ta.
* Pip (managerul de pachete implicit al Python).

---

## 📦 Setarea Mediului Virtual

Este o bună practică ca inginer software să lucrezi într-un mediu virtual izolat (`venv`) pentru a preveni conflictele între biblioteci. 

Deschide PowerShell sau linia de comandă în folderul proiectului și rulează:

```powershell
# 1. Crearea mediului virtual în folderul '.venv'
python -m venv .venv

# 2. Activarea mediului virtual pe Windows
.venv\Scripts\activate

# 3. Instalarea proiectului în mod editabil împreună cu dependințele de testare
pip install -e ".[dev]"
```

> [!IMPORTANT]
> Flag-ul `-e` (editable mode) indică faptul că orice modificare pe care o faci în fișierele din folderul `app/` se va reflecta instantaneu în aplicația rulată, fără a fi nevoie să o reinstalezi.

---

## 🚦 Rularea Serverului API

Aplicația folosește **Uvicorn** drept server web. Pentru a porni serverul local cu reîncărcare automată la fiecare salvare de fișier (`--reload`):

```bash
uvicorn app.main:app --reload
```

După pornire, poți accesa:
* 🌐 **API-ul de bază**: `http://localhost:8000`
* 📖 **Swagger UI (Docs)**: `http://localhost:8000/docs` – *Un instrument extrem de util unde poți testa manual fiecare endpoint!*

---

## 🧪 Rularea Testelor Automate

Proiectul folosește framework-ul **pytest** pentru testele sale unitare și de integrare. Înainte de a scrie orice cod nou, rulează:

```bash
pytest -v
```

> [!WARNING]
> La prima rulare, vei vedea o serie de eșecuri roșii în consolă. Nu te îngrijora! Acesta este punctul de pornire. Mergi la ghidul **[[Bugs-To-Fix]]** pentru a înțelege cum le vom analiza și repara.
