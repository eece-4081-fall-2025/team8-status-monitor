# Team 8 project

## Setup
1. Clone the repository
```bash
git clone https://github.com/eece-4081-fall-2025/team8-status-monitor.git
cd team8-status-monitor
```

2. Create the virtual enviorment
Windows:
```bash 
python -m venv .venv
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
4. Run server
```bash
python manage.py runserver
```