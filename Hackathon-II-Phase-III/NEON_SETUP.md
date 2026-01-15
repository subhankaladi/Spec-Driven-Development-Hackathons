# 🚀 Neon PostgreSQL Setup Guide

This guide will help you migrate from SQLite to Neon PostgreSQL for production deployment.

## 📋 Prerequisites

- [ ] Neon account (https://neon.tech)
- [ ] Python 3.12+
- [ ] Existing project with SQLite

---

## Step 1: Create Neon Database

### 1.1 Sign Up for Neon

1. Go to: **https://neon.tech/**
2. Click **"Sign Up"** (use GitHub/Google/Email)
3. Verify your email (if using email signup)

### 1.2 Create Your First Project

1. Click **"Create a project"**
2. Configure:
   - **Project name**: `todo-app-production` (or your choice)
   - **PostgreSQL version**: `15` (recommended)
   - **Region**: Choose closest to your users:
     - `US East (Ohio)` - for US East Coast
     - `US West (Oregon)` - for US West Coast
     - `Europe (Frankfurt)` - for Europe
     - `Asia Pacific (Singapore)` - for Asia
3. Click **"Create Project"**

### 1.3 Get Your Connection String

After creating the project, you'll see the **Connection Details** page:

```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**📝 Copy this entire string** - you'll need it in the next step.

**Connection String Breakdown**:
- `username`: Your database user (auto-generated)
- `password`: Your database password (auto-generated)
- `ep-cool-name-123456.us-east-2.aws.neon.tech`: Your endpoint hostname
- `neondb`: Default database name
- `?sslmode=require`: SSL is required for security

---

## Step 2: Configure Your Application

### 2.1 Update `.env` File

Open `backend/.env` and replace line 8 with your Neon connection string:

```bash
# Before:
DATABASE_URL=postgresql://user:password@your-endpoint.neon.tech/neondb?sslmode=require

# After (use YOUR actual connection string):
DATABASE_URL=postgresql://your-username:your-password@ep-your-endpoint.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**⚠️ IMPORTANT**:
- Replace the entire string with the one from Neon
- Keep `?sslmode=require` at the end
- **DO NOT commit this file to Git** (it's already in `.gitignore`)

### 2.2 For Local Development (Optional)

If you want to use SQLite locally but PostgreSQL in production:

```bash
# .env.local (for local development)
DATABASE_URL=sqlite:///./todo_app.db
ENVIRONMENT=development

# .env.production (for deployment)
DATABASE_URL=postgresql://your-neon-connection-string
ENVIRONMENT=production
```

---

## Step 3: Test the Connection

Run the test script to verify your connection:

```bash
cd backend
python test_db_connection.py
```

**Expected Output (Success)**:
```
============================================================
Testing Database Connection
============================================================

📊 Database Type: PostgreSQL (Neon)
🔗 Connection URL: postgresql://username:***@ep-cool-name-...
🌍 Environment: development

✅ Connection successful!
   Test query result: 1
   PostgreSQL version: PostgreSQL 15.3 on x86_64-pc-linux-gnu...

✅ Database is ready to use!
```

**If you see errors**, check:
1. ✅ Connection string is correct (copy-paste from Neon)
2. ✅ `psycopg2-binary` is installed: `pip install psycopg2-binary`
3. ✅ Your Neon project is **active** (check at https://console.neon.tech)
4. ✅ No firewall blocking port 5432

---

## Step 4: Set Up Database Migrations (Alembic)

Alembic tracks database schema changes and makes it safe to deploy updates.

### 4.1 Initialize Alembic

```bash
cd backend
alembic init migrations
```

This creates:
- `migrations/` folder (migration scripts)
- `alembic.ini` (configuration file)

### 4.2 Configure Alembic

**Edit `backend/alembic.ini`** - Update line ~58:

```ini
# Before:
sqlalchemy.url = driver://user:pass@localhost/dbname

# After:
# Leave this commented - we'll use env.py to read from .env
# sqlalchemy.url =
```

**Edit `backend/migrations/env.py`** - Replace the entire file:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models and settings
from src.config.settings import settings
from src.models.task import Task
from src.models.user import User
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4.3 Create Your First Migration

```bash
# Generate migration from your models
alembic revision --autogenerate -m "Initial migration with users and tasks"

# Review the generated migration file in migrations/versions/
# Then apply it:
alembic upgrade head
```

**What this does**:
- Creates `users` and `tasks` tables in Neon
- Sets up indexes and relationships
- Creates a version history for future changes

---

## Step 5: Migrate Existing Data (Optional)

If you have data in SQLite that you want to move to PostgreSQL:

### 5.1 Export from SQLite

```bash
cd backend

# Export users
sqlite3 todo_app.db "SELECT * FROM user;" > users_export.csv

# Export tasks
sqlite3 todo_app.db "SELECT * FROM task;" > tasks_export.csv
```

### 5.2 Import to PostgreSQL

Create `import_data.py`:

```python
from sqlmodel import Session
from src.database.session import engine
from src.models.user import User
from src.models.task import Task
import csv

with Session(engine) as session:
    # Import users from CSV
    with open('users_export.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(**row)
            session.add(user)

    # Import tasks from CSV
    with open('tasks_export.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = Task(**row)
            session.add(task)

    session.commit()
    print("✅ Data imported successfully!")
```

Run: `python import_data.py`

---

## Step 6: Update Your Application Startup

The application is already configured to create tables on startup, but with Alembic, you should remove auto-creation.

**Edit `backend/src/api/main.py`**:

```python
@app.on_event("startup")
def on_startup():
    # Comment out auto-creation - use Alembic instead
    # create_db_and_tables()

    # Optional: Log database info
    logger.info(f"🗄️  Database: {settings.database_url[:50]}...")
    logger.info(f"🌍 Environment: {settings.environment}")
```

---

## Step 7: Restart Your Backend

```bash
cd backend
uvicorn src.api.main:app --reload
```

Check the logs for:
```
🗄️  Database: postgresql://username:***@ep-...
🌍 Environment: development
✅ Application startup complete
```

---

## 🎉 You're Done!

Your app is now using Neon PostgreSQL!

### ✅ Verification Checklist

- [ ] Connection test passes (`python test_db_connection.py`)
- [ ] Backend starts without errors
- [ ] You can sign up and create a user
- [ ] You can create, read, update, and delete tasks
- [ ] Data persists after server restart

---

## 📊 Monitoring Your Database

### Neon Dashboard (https://console.neon.tech)

Monitor:
- **Usage**: Storage, connections, queries
- **Branches**: Create development/staging branches
- **Backups**: Automatic daily backups (retained 7 days on free tier)
- **Logs**: Query logs and errors

### Query Performance

Check slow queries in Neon Console > Monitoring > Query Stats

---

## 🔒 Security Best Practices

### 1. Generate a Secure JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Update `.env`:
```bash
JWT_SECRET=<generated-secret-here>
```

### 2. Use Environment Variables in Production

**Never hardcode secrets!**

On deployment platforms (Vercel, Railway, Render):
1. Go to Environment Variables settings
2. Add:
   - `DATABASE_URL`: Your Neon connection string
   - `JWT_SECRET`: Your generated secret
   - `ENVIRONMENT`: `production`

### 3. Enable Connection Pooling

Already configured in `src/database/session.py`:
- `pool_size=5`: Max 5 persistent connections
- `max_overflow=10`: Can create 10 more temporary connections
- `pool_recycle=300`: Recycle connections every 5 minutes

---

## 🐛 Troubleshooting

### Error: "Could not connect to server"

**Cause**: Network/firewall issue

**Fix**:
1. Check your connection string is correct
2. Ensure your Neon project is active (not suspended)
3. Check firewall allows outbound port 5432

### Error: "password authentication failed"

**Cause**: Incorrect credentials

**Fix**:
1. Re-copy connection string from Neon dashboard
2. Ensure you didn't modify username/password
3. Reset password in Neon Console > Settings > Reset Password

### Error: "SSL connection is required"

**Cause**: Missing `?sslmode=require`

**Fix**: Add to connection string:
```
postgresql://...neon.tech/neondb?sslmode=require
```

### Error: "No module named 'psycopg2'"

**Cause**: PostgreSQL driver not installed

**Fix**:
```bash
pip install psycopg2-binary
```

---

## 📚 Additional Resources

- **Neon Docs**: https://neon.tech/docs/introduction
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Alembic Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- **FastAPI Database Guide**: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

## 🎯 Next Steps

1. ✅ **Add more migrations** as your schema evolves
2. ✅ **Set up staging environment** with Neon branch
3. ✅ **Configure backups** (Neon does this automatically)
4. ✅ **Add monitoring** with error tracking (Sentry)
5. ✅ **Optimize queries** using Neon's query stats

Need help? Check the troubleshooting section or open an issue!
