# 🏋️ Gym Platform

**Train · Track · Transform** — a complete gym management platform, available as a
**desktop app** and a matching **web app**.

Both share the same deep-red/black design, the same login, and the same features
(members, payments, alerts, birthdays, broadcast, check-in, leave, expenses,
maintenance, employees, activity tracker, products, finance, reports, settings,
audit logs).

---

## 🖥️ Desktop app

A full-featured CustomTkinter app backed by SQLAlchemy (SQLite by default, or
PostgreSQL if configured).

```bash
pip install -r requirements.txt
python desktop_app.py            # launch
python seed_fake_data.py --yes   # (re)fill with demo data
```

Login: **admin / admin123**

---

## 🌐 Web app

`index.html` is a **single-file web version** with the exact same look, login and
features. It is **100% client-side** — all data lives in the browser's
`localStorage`, so:

- **No PostgreSQL / no server database required.**
- The client can **add, edit and delete** members, payments, expenses, products,
  employees, etc. — everything is saved **locally in their browser**.
- On first open it seeds the same demo dataset as the desktop app.

### Run locally

Just open `index.html` in any browser, **or** serve it:

```bash
python -m http.server 8000     # then visit http://localhost:8000
```

Login: **admin / admin123** (staff: `sara / sara123`, `youssef / youssef123`, `khalid / khalid123`)

### Data controls (Settings page)

- **Export Data** — download everything as a JSON backup.
- **Import Data** — restore from a JSON backup.
- **Reset to Demo Data** — wipe local changes and reload the demo dataset.

---

## ☁️ Deploy to GitHub + Vercel

1. Push this repo to GitHub.
2. Import the repo on [vercel.com](https://vercel.com) → **Deploy** (no settings needed).

`vercel.json` serves the static web app (`index.html`) at the root and keeps the
optional read-only JSON API (`/api/*`) from `api/index.py`.

Because the web app stores data per-browser, every visitor gets their own
independent copy of the data — perfect for a shareable demo with no backend to
maintain.
