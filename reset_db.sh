#!/bin/bash
# ===========================================
# reset_db.sh
# Resets PostgreSQL DB and Django migrations safely
# for team8-status-monitor project
# ===========================================

# Stop on error
set -e

DB_NAME="status_monitor"
DB_USER="status_user"
DB_PASSWORD="status_password"
PYTHON_BIN="venv/bin/python"

echo "🚀 Resetting Django project and PostgreSQL database: $DB_NAME"
echo "============================================================"

# 1️⃣ Ensure PostgreSQL is running
echo "🔍 Checking PostgreSQL service..."
brew services start postgresql >/dev/null 2>&1 || true

# 2️⃣ Ensure PostgreSQL user exists
echo "👤 Ensuring PostgreSQL user '$DB_USER' exists..."
USER_EXISTS=$(psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
if [ "$USER_EXISTS" != "1" ]; then
  echo "🔑 Creating user '$DB_USER' with password..."
  psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
  echo "✅ User '$DB_USER' already exists."
fi

# 2️⃣ Drop and recreate database
echo "💣 Dropping and recreating database..."
psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# 2️⃣.1 Grant privileges to user
echo "🔏 Granting privileges on database '$DB_NAME' to user '$DB_USER'..."
psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 2.5️⃣ Detect and rename old table if it exists
echo "🔄 Checking for existing table 'status_monitor_site' to rename..."
psql -U postgres -d $DB_NAME -c "DO \$\$ BEGIN IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'status_monitor_site') THEN ALTER TABLE status_monitor_site RENAME TO status_monitor_monitoredsite; END IF; END \$\$;"
echo "✅ Table rename check complete."

# 3️⃣ Clean migrations (excluding __init__.py)
echo "🧹 Removing old migration files..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 4️⃣ Recreate migrations and apply them
echo "🧱 Rebuilding database schema..."
$PYTHON_BIN manage.py makemigrations
$PYTHON_BIN manage.py migrate --fake-initial

# 5️⃣ Fix django_apscheduler schema issue
echo "🩹 Applying fake migrations for django_apscheduler..."
$PYTHON_BIN manage.py migrate django_apscheduler zero || true
$PYTHON_BIN manage.py migrate django_apscheduler --fake

# 6️⃣ Apply all remaining migrations
$PYTHON_BIN manage.py migrate

echo "✅ Database and migrations successfully reset!"
echo "You can now run:  $PYTHON_BIN manage.py runserver"    