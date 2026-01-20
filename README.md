# Office Tasks & Personnel Management (Intranet)

A lightweight intranet-only web application for managing users (employees), projects, and tasks, built with Flask + PostgreSQL and server-rendered templates.

Designed for:

- internal office networks (no internet dependency)
- minimal, auditable dependencies
- simple deployment on Windows Server / IIS or standalone
- public read-only dashboards + admin-only management

---

## Features

### Public (no login)

- Dashboard with KPIs (users / projects / tasks / overdue)
- List & detail views:
  - Users (including phone numbers)
  - Projects (tasks + attachment links)
  - Tasks (filters by project, status, assignee, overdue)
- Task comments visible to everyone

### Admin (login required)

- Manage users (employees)
  - rank (ENUM)
  - phones
  - active / admin flags
- Manage projects
- Manage tasks
  - multiple assignees
  - status, priority, deadlines
- Add task comments
- Add project attachment links (internal folders / URLs)
- Logout support

---

### Tech Stack

- **Backend:** Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** Flask-Login
- **Forms / CSRF:** Flask-WTF
- **WSGI (Windows):** Waitress
- **Frontend:** Server-rendered HTML (Jinja)
- **UI:** Bootstrap + Font Awesome (loaded from internal CDN)

No React, no npm, no external APIs.

---

### Requirements

- Python **3.12+**
- PostgreSQL **17+**
- pip / virtualenv

---

## Local Development Setup (macOS / Linux)

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. PostgreSQL setup

```sql
CREATE DATABASE office_tasks;
CREATE USER office_app WITH PASSWORD 'StrongPassword';
ALTER DATABASE office_tasks OWNER TO office_app;
GRANT ALL PRIVILEGES ON DATABASE office_tasks TO office_app;
```

### 3. Environment variables

```bash
export DATABASE_URL="postgresql://office_app:StrongPassword@127.0.0.1:5432/office_tasks"
export SECRET_KEY="change-me"
```

### 4. Initialize database schema

```bash
alembic upgrade head
```

### 5. Create first admin user

```bash
python bootstrap_admin.py
```

### 6. Run development server

```bash
python run.py
```

### Open:

http://127.0.0.1:5000

---

### PostgreSQL Backups

Backup (custom format)

```bash
pg_dump -h 127.0.0.1 -U office_app -d office_tasks -Fc -f office_tasks.dump
```

Restore (clean)

```bash
createdb office_tasks_restored
pg_restore -U office_app -d office_tasks_restored --no-owner --no-privileges office_tasks.dump
```

---

## License

- Internal / private use.
- Adapt freely for organizational needs.
