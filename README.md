# Time Capsule
A web application that allows users to save memories, messages, or notes to be opened at a future date. A digital version of a traditional time capsule.

---

## Features
- Create personal time capsules  
- Set a future unlock date  
- Store text-based memories  
- Capsules become accessible once the date arrives  
- Simple and clean user interface  

---

## Tech Stack
- Frontend: HTML, CSS  
- Backend: Django  
- Database: SQLite / PostgreSQL  
- Version Control: Git & GitHub  

## Run locally

1. Install Django (`pip install django`).
2. Run `python manage.py migrate`.
3. Run `python manage.py runserver` and open `http://127.0.0.1:8000/`.

Each new capsule requires a secret key of at least 10 characters. Only its
password hash is stored. The key cannot be recovered, so keep it somewhere
safe. After unlocking, the browser session stays authorized for that capsule
for 10 minutes. Attachments are delivered through an access-checked Django
view; do not configure a web server or CDN to publish `MEDIA_ROOT` directly.

Capsules already in the database from before secret keys were added have no
key hash. An administrator must open that capsule in `/admin/` and set a key
before it can be opened. This avoids letting an arbitrary first visitor claim
an old capsule.

For deployment, set `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and set
`DJANGO_ALLOWED_HOSTS` to a comma-separated list of the site's hostnames. The
development key is randomly generated at startup and is not suitable for
deployment.
            
