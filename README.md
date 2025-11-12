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

4. Start the development server
From the project root:
```bash
python manage.py runserver
```
## Features and Usage
This is the development edition of the server. Currently there is no production equivilent for this application. To use the application, you must run it locally in a development enviorment, as detailed above. This existing MVP has the following features:
### Account Creation
Using an extension of Djangos buit-in authinticaiont stack, a new client must first create an user account. There is no 2FA or email confirmations. 

## Website Tracking
The user is prompted to enter details about tracked websites. The websites are attached to the user account, and will persist between sessions and are unique to accounts.

## Status display
The status monitor display is avalible, listing the details of the user-added tracked websites, such as their name, URL, status, immediate response time, and links to manage the tracked websites details. 