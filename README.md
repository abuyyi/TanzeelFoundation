TanzeelFoundation — Local development setup

Prerequisites
- Python 3.10+ (3.14 used in CI/dev here).

Quick start (Windows PowerShell)

```powershell
cd 'c:\Users\PC\tanzeel\TanzeelFoundation'
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
# edit .env to set SECRET_KEY and other vars

```

Run tests

```powershell
.venv\Scripts\python.exe manage.py test
```


Notes
- `requirements.txt` now contains pinned packages used by the project; pin further if needed.
- If you rely on a different DB (Postgres/MySQL), set `DATABASE_URL` in `.env` and update `tanzeel/settings.py` accordingly.

git status
git add .
git commit -m "message"
git pull
git push