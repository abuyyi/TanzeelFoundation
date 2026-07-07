# Deploying Tanzeel Foundation to cPanel (SSH)

Tailored to this server:

| Thing | Value |
|---|---|
| cPanel user | `tanzcrwv` |
| Home | `/home/tanzcrwv` |
| App directory | `/home/tanzcrwv/tanzeelfoundation` |
| Virtualenv | `/home/tanzcrwv/virtualenv/tanzeelfoundation/<pyver>/bin/activate` |
| Domain docroot | `/home/tanzcrwv/public_html` |
| Passenger error log | `/home/tanzcrwv/tanzeelfoundation/stderr.log` |

> Get the exact `source .../activate` line from **cPanel → Setup Python App → "Enter to the virtual environment"**. Everything below assumes the venv is active and you are in the app dir.

```bash
source /home/tanzcrwv/virtualenv/tanzeelfoundation/3.9/bin/activate   # adjust 3.9 to your version
cd /home/tanzcrwv/tanzeelfoundation
```

---

## 0. Rotate leaked credentials (do this once, before go-live)

The old `settings.py` had real secrets committed in comments (now removed). Treat
them as compromised:

- **AzamPay** client secret / token / API key — regenerate in the AzamPay dashboard.
- The **Gmail** account `saumuissa27@gmail.com` password — change it.
- Generate a fresh Django `SECRET_KEY` (step 4).

---

## 1. Back up the current site first

```bash
cd /home/tanzcrwv
mysqldump -u tanzcrwv_<dbuser> -p tanzcrwv_<db> > ~/backup_$(date +%F).sql
tar czf ~/app_backup_$(date +%F).tar.gz tanzeelfoundation
```

Keep the current site running until the new one is verified.

---

## 2. Clean up dev/junk files in the app dir

Your `tanzeelfoundation/` folder currently has files that must NOT be in production.
Remove them:

```bash
cd /home/tanzcrwv/tanzeelfoundation
rm -f ngrok.exe                      # Windows dev tunneling binary, useless on Linux
rm -f Dockerfile docker-compose.yml  # not used on cPanel/Passenger
rm -f db.sqlite3                     # you're on MySQL now; sqlite file is stale/misleading
rm -f data.json data.json.bak        # dumpdata fixtures — may contain data, don't leave in webroot
rm -f 'SRS12-V2[1].pdf'              # internal spec doc, shouldn't sit on the server
# after extracting (step 7) also:  rm -f media.zip TanzeelFoundation.zip
```

`README.md`, `ISLAMIC_DESIGN_GUIDELINES.md`, `stderr.log`, `passenger_wsgi.py`,
`requirements.txt`, `manage.py`, and the `tanzeel/ core/ pages/ donations/ static/
templates/ scripts/` folders all stay.

---

## 3. Get the latest code onto the server

If you deployed by uploading `TanzeelFoundation.zip`, make sure it's the current
code (with the production hardening). Cleanest is Git:

```bash
cd /home/tanzcrwv/tanzeelfoundation
git pull        # or clone fresh and copy media/ + .env across
```

Do NOT commit or upload: `.env`, `db.sqlite3`, `staticfiles/`, `__pycache__/`.

---

## 4. Create and fill the environment file

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```

Set at minimum:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<the generated key>`  (must NOT start with `django-insecure-`)
- `DJANGO_ALLOWED_HOSTS=tanzeelfoundation.co.tz,www.tanzeelfoundation.co.tz`
- `MYSQL_DATABASE / MYSQL_USER / MYSQL_PASSWORD` — the cPanel MySQL DB from step 6
  (names are prefixed, e.g. `tanzcrwv_tanzeel_db`, `tanzcrwv_tanzeel`).
- Real AzamPay / Pesapal credentials.

> The app intentionally refuses to boot with `DEBUG=False` and a default/insecure key.

---

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

`mysqlclient` is intentionally excluded (needs a C toolchain); MySQL works via the
pure-Python `PyMySQL` + `cryptography`.

---

## 6. Create the database and load the data

In **cPanel → MySQL Databases**: create a database and user (they'll be prefixed
with `tanzcrwv_`), add the user to the database with **ALL PRIVILEGES**. Put those
names/password in `.env` (step 4). Then load the dump:

```bash
mysql -u tanzcrwv_<dbuser> -p tanzcrwv_<db> < dumps/dumps/Dump20260705.sql
python manage.py migrate      # applies any migrations newer than the dump
```

(If starting from an empty DB instead of the dump: just `migrate`, then
`python manage.py createsuperuser`.)

---

## 7. Media files (your images)

You have `media.zip` on the server. Extract it and **watch for double-nesting** —
the same trap we hit locally, where files land in `media/media/...` instead of
`media/...`.

```bash
cd /home/tanzcrwv/tanzeelfoundation
unzip -o media.zip
# If a nested media/media appeared, flatten it:
[ -d media/media ] && cp -r media/media/. media/ && rm -rf media/media

# Sanity check: this file MUST exist at exactly this path
ls -l media/homepage_images/0R2A0743.webp
rm -f media.zip
```

Media is served by the Django app in production (no web-server config needed), so
once the files are at the right paths, images work.

**Optional performance upgrade:** let Apache serve `/media/` directly by symlinking
it into the domain docroot, which bypasses Python for images:

```bash
ln -s /home/tanzcrwv/tanzeelfoundation/media /home/tanzcrwv/public_html/media
```

If the symlink 404s, your domain's docroot isn't `public_html` (e.g. it's a
subdomain) — remove the symlink; the app-served route already covers you.

---

## 8. Collect static files

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves everything from `staticfiles/` through the app — no Apache alias
needed for static.

---

## 9. Restart Passenger and verify

```bash
mkdir -p tmp && touch tmp/restart.txt      # tells Passenger to reload the app
python manage.py check --deploy            # should report no security issues
```

Then browse **https://tanzeelfoundation.co.tz** and confirm:

- Home page renders and **images load**.
- `/admin/` login works (CSRF uses `DJANGO_CSRF_TRUSTED_ORIGINS`).
- If something 500s, read the error: `tail -n 50 stderr.log`.

---

## 10. Future updates

```bash
source /home/tanzcrwv/virtualenv/tanzeelfoundation/3.9/bin/activate
cd /home/tanzcrwv/tanzeelfoundation
git pull
pip install -r requirements.txt        # only if requirements changed
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

---

## Rollback

Restore the DB dump and app backup from step 1, then `touch tmp/restart.txt`.

---

## Troubleshooting quick reference

| Symptom | Likely cause / fix |
|---|---|
| 500 on every page | `tail stderr.log`. Often a missing `.env` value or DB creds. |
| `DisallowedHost` | Add the domain to `DJANGO_ALLOWED_HOSTS` in `.env`, restart. |
| Admin login "CSRF verification failed" | Set `DJANGO_CSRF_TRUSTED_ORIGINS=https://tanzeelfoundation.co.tz,https://www.tanzeelfoundation.co.tz`. |
| Images 404 | Media file not at the path the DB expects — recheck `media/` structure (step 7). |
| CSS/JS missing | Re-run `collectstatic`; confirm `whitenoise` installed. |
| "SECRET_KEY must be set" on start | `DJANGO_SECRET_KEY` missing or still a `django-insecure-` value. |
