# Team 8 project

## Setup
1. Clone the repository
```bash
git clone https://github.com/eece-4081-fall-2025/team8-status-monitor.git
cd team8-status-monitor
```

2. Create the virtual enviorment
Windows:
```bash -m venv .venv
.venv\Scripts\Activate.ps1
```
Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Dependencies
Make sure the virtual environment is active, then run
```bash
pip install -r requirements.txt
```

## Database Setup (PostgreSQL)

### macOS
Install PostgreSQL using Homebrew:
```bash
brew install postgresql
brew services start postgresql
```

### Windows
Download and install PostgreSQL from the official installer:  
https://www.postgresql.org/download/windows/

### Create PostgreSQL User and Database
After installing PostgreSQL, create the user and database required by the Django project:
```bash
psql -U postgres
CREATE USER team8_user WITH PASSWORD 'your_password';
CREATE DATABASE team8_db OWNER team8_user;
GRANT ALL PRIVILEGES ON DATABASE team8_db TO team8_user;
\q
```
Make sure to update your Django `settings.py` with the correct database credentials.

### Reset Database
You can use the provided script `reset_db.sh` to reset the database configuration.  
**Note:** This script will drop and recreate the database and user, so use it with caution.
```bash
./reset_db.sh
```

4. Start the development server (not set up!)
From the project root:
```bash
python manage.py runserver
```
