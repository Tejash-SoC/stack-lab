# Taskboard: React + Django REST full-stack app

```
taskboard/
  backend/    Django + Django REST Framework + JWT (simplejwt)
  frontend/   React 18 + Vite + axios
```

## How the pieces connect

1. The browser loads the React app (port 5173 in dev).
2. React calls `/api/...` with axios (`frontend/src/api.js`).
   In dev, Vite proxies `/api` to Django on port 8000, so there is no CORS problem.
3. Sign in: `POST /api/auth/login/` returns `access` (30 min) and `refresh` (7 days) tokens.
   The frontend stores them and sends `Authorization: Bearer <access>` on every request.
4. When the access token expires, axios gets a new one from `/api/auth/refresh/` and retries.
5. Django only returns the signed-in user's own tasks (`backend/tasks/views.py`).

## API

| Method | URL | What it does | Auth |
|---|---|---|---|
| POST | /api/auth/register/ | create account `{username, email?, password}` | no |
| POST | /api/auth/login/ | get `{access, refresh}` | no |
| POST | /api/auth/refresh/ | `{refresh}` -> new `{access}` | no |
| GET | /api/auth/me/ | current user | yes |
| GET | /api/tasks/ | list your tasks (`?status=todo\|doing\|done`) | yes |
| POST | /api/tasks/ | create `{title, notes?, status?, priority?, due_date?}` | yes |
| GET/PATCH/PUT/DELETE | /api/tasks/{id}/ | read / update / delete one task | yes |

## Run it locally

Backend (terminal 1):
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations accounts tasks
python manage.py migrate
python manage.py test           # optional: runs the API tests
python manage.py createsuperuser  # optional: for /admin/
python manage.py runserver      # http://127.0.0.1:8000
```

Frontend (terminal 2):
```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

Open http://localhost:5173, create an account, add tasks.

## Deploying

**Backend** (Render, Railway, Fly, a VPS, etc.)
- Set env vars: `SECRET_KEY` (long random), `DEBUG=0`, `ALLOWED_HOSTS=api.yourdomain.com`,
  `CORS_ALLOWED_ORIGINS=https://yourdomain.com`.
- Start command: `gunicorn config.wsgi`. Build step: `python manage.py collectstatic --noinput && python manage.py migrate`.
- Switch to PostgreSQL: `pip install psycopg[binary] dj-database-url`, then in `settings.py`
  replace `DATABASES` with `{"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR/'db.sqlite3'}")}`
  and set `DATABASE_URL`.

**Frontend** (Vercel, Netlify, Cloudflare Pages)
- Build: `npm run build`, publish `dist/`.
- Set `VITE_API_URL=https://api.yourdomain.com/api` before building.

## Ideas for next steps
Edit task titles and notes, drag-and-drop between columns, due-date sorting, password reset by email,
store the refresh token in an httpOnly cookie for stronger security.
