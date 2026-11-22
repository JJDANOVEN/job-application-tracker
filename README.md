# Job Application Tracker

A simple Flask web application with a MySQL database for tracking companies, job listings, applications, and contacts. It also includes a basic job-match percentage tool.


## Requirements
- Python 3.10 or newer
- MySQL Server
- pip

## Setup

### 1. Create the database and tables
Open MySQL Workbench, open `schema.sql`, and run the entire script. It creates the `job_tracker` database and four tables.

### 2. Install Python packages
Open a terminal in this project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Set your MySQL password
The app defaults to MySQL user `root` with a blank password. If your MySQL password is not blank, set environment variables before running the app.

macOS/Linux:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD='your_mysql_password'
export DB_NAME=job_tracker
```

Windows PowerShell:
```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_NAME="job_tracker"
```

### 4. Start the web app
```bash
python app.py
```

Open this address in your browser: http://127.0.0.1:5000

## Features
- Add, view, edit, and delete companies
- Add, view, edit, and delete jobs
- Add, view, edit, and delete applications
- Add, view, edit, and delete contacts
- Job Match page: enter your skills separated by commas to see each job's match percentage
- Dashboard counts and recent applications

## Database relationships
- Each job belongs to one company
- Each application refers to one job
- Contacts can be associated with a company

## Notes
Use the local development server for the project demonstration. Do not publish your database password or other secrets to GitHub.
