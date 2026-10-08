# Sentinel Console

Sentinel Console is a Flask-based web application that helps security and system administrators review Linux system snapshots and turn them into a compliance-style assessment. The app accepts raw command output, parses the important sections, and uses the Gemini API to identify compliance issues, recommendations, and summary findings.

This project is designed to take a pasted system snapshot such as `uname -a`, `ip addr`, `lscpu`, `free -h`, `df -h`, and `uptime` output and convert it into a readable report.

---

## What the app does

- Accepts pasted Linux system output from a user
- Extracts the key sections automatically
- Summarizes operating system, CPU, memory, disk, network, and uptime details
- Sends the data to Gemini for compliance analysis
- Stores the latest scan and historical scan results in SQLite
- Displays the analysis in a browser UI

---

## Project structure

```text
NewCapstone2026/
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── api/
│   │   ├── ai_integration.py
│   │   └── routes.py
│   ├── collector/
│   │   └── log_parser.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   └── __pycache__/
└── frontend/
    ├── app.js
    ├── index.html
    ├── report.html
    └── style.css
```

### Main components

- `backend/app.py` - starts the Flask app and serves frontend files
- `backend/config.py` - loads environment variables and project config
- `backend/api/routes.py` - exposes the API endpoints
- `backend/api/ai_integration.py` - communicates with the Gemini API
- `backend/collector/log_parser.py` - parses raw Linux output into sections
- `backend/database/db.py` - manages SQLite access and scan storage
- `frontend/index.html` - dashboard page for submitting system snapshots
- `frontend/app.js` - frontend logic for submitting and rendering results

---

## Features

### 1. Raw system output input
Users can paste text that looks like Linux diagnostic output or even a simple section-based format such as:

```text
OS:
Linux ubuntu 5.15.0-107-generic ...

CPU:
Architecture: x86_64
Model name: Intel(R) Xeon(R) CPU @ 2.20GHz

MEMORY:
MemTotal: 16384256 kB

DISK:
Filesystem     Size  Used Avail Use% Mounted on
/dev/sda1      20G   9G   10G  47% /

NETWORK:
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 192.168.1.25/24

UPTIME:
18:00:01 up 2 days, 4:32, 1 user, load average: 0.18, 0.27, 0.30
```

The parser accepts both raw Linux output and section label styles.

### 2. AI-based compliance review
The app sends the parsed snapshot to Gemini and asks for a compliance-oriented assessment. It looks for:

- missing security controls
- risky server configuration issues
- weak operational posture
- recommendations for compliance improvement
- summary findings with a pass/fail style interpretation

### 3. SQLite storage
Every submitted scan is saved to a local SQLite database for:

- latest result lookup
- scan history view
- detailed record inspection

### 4. Web dashboard
The UI includes:

- a text area for pasting system output
- a summary panel for current posture
- a results table with control observations and recommendations
- a history/report page

---

## Requirements

Before running the project, make sure you have:

- Python 3.10+ (tested with Python 3.12)
- pip
- A valid Gemini API key
- Internet access for the Gemini API call

---

## Environment setup

Create a `.env` file in the project root with your configuration:

```env
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
GEMINI_API_KEY=your_api_key_here
AI_MODEL=gemini-3.1-flash-lite
AI_MAX_TOKENS=1024
```

Notes:

- `GEMINI_API_KEY` is required for AI analysis.
- `AI_MODEL` should be a valid Gemini model name that is available in your account.
- The project already includes a `.gitignore` entry for `.env` so secrets are not committed.

---

## Installation

From the project root:

```bash
cd C:\Users\nguye\NewCapstone2026
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

On macOS/Linux:

```bash
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

## Running the app

Start the Flask app from the backend directory:

```bash
cd backend
python app.py
```

Then open in your browser:

```text
http://localhost:5000
```

The app serves:

- home page: `http://localhost:5000/`
- report/history page: `http://localhost:5000/report`

---

## API endpoints

The backend exposes these endpoints:

### Submit a new scan

```http
POST /api/submit
```

Request body:

```json
{
  "raw_output": "Linux ubuntu ..."
}
```

Response includes:

- `scan_id`
- AI-generated `summary`
- compliance `items`
- parsed `specs`

### Get latest scan

```http
GET /api/latest
```

### Get full scan history

```http
GET /api/history
```

### Get a single scan by ID

```http
GET /api/scan/<scan_id>
```

### Health check

```http
GET /api/health
```

---

## How the parsing works

The parser in `backend/collector/log_parser.py` does not execute commands on your machine. It simply reads the pasted text and finds sections such as:

- OS / kernel info
- CPU info
- memory usage
- disk usage
- IP/interface details
- uptime / load averages

It then turns that into a summary dictionary for the AI model. This lets the app work with raw pasted output from Linux commands without needing to directly access the server environment.

---

## Example usage

### Example 1: Paste raw Linux output

```text
Linux ubuntu 5.15.0-107-generic #117-Ubuntu SMP Tue Apr 30 17:03:15 UTC 2024 x86_64 GNU/Linux

Architecture: x86_64
CPU op-mode(s): 32-bit, 64-bit
Model name: Intel(R) Xeon(R) CPU @ 2.20GHz

MemTotal: 16384256 kB

Filesystem     Size  Used Avail Use% Mounted on
/dev/sda1      20G   9G   10G  47% /

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 192.168.1.25/24

18:00:01 up 2 days, 4:32, 1 user, load average: 0.18, 0.27, 0.30
```

### Example 2: Paste cleaner labeled sections

```text
OS:
Linux ubuntu 5.15.0-107-generic #117-Ubuntu SMP Tue Apr 30 17:03:15 UTC 2024 x86_64 GNU/Linux

CPU:
Architecture: x86_64
Model name: Intel(R) Xeon(R) CPU @ 2.20GHz

MEMORY:
MemTotal: 16384256 kB

DISK:
Filesystem     Size  Used Avail Use% Mounted on
/dev/sda1      20G   9G   10G  47% /

NETWORK:
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 192.168.1.25/24

UPTIME:
18:00:01 up 2 days, 4:32, 1 user, load average: 0.18, 0.27, 0.30
```

Both variants are accepted.

---

## Troubleshooting

### ModuleNotFoundError: No module named 'google'
Run:

```bash
pip install -r backend/requirements.txt
```

### App starts but AI is unavailable
Check:

- your `.env` file exists in the project root
- `GEMINI_API_KEY` is set correctly
- your model name is valid in Gemini
- the Flask app was restarted after changing environment variables

### Blank or failed analysis
Check whether the pasted output is too short or missing standard Linux sections.

### Port already in use
If port `5000` is already occupied, change the value in `.env`:

```env
FLASK_PORT=5001
```

Then restart the app.

---

## Docker support

A `Dockerfile` is included in the project root. You can build and run it with:

```bash
docker build -t sentinel-console .
docker run -p 5000:5000 --env-file .env sentinel-console
```

---

## Security notes

- Do not commit your `.env` file to version control.
- Keep your Gemini API key private.
- Only paste environment data you are authorized to review.

---

## Future ideas

- Add user authentication
- Add more detailed compliance checks
- Support CSV/JSON export of scan results
- Add scheduled scanning and alerts
- Improve AI output formatting and scoring

---

## License

This project is intended for internal use and educational or operational evaluation. Add your preferred license if you plan to publish or distribute it publicly.

---

## Quick start summary

```bash
cd C:\Users\nguye\NewCapstone2026
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy .env.example .env
# then edit .env with your API key
cd backend
python app.py
```

Then open `http://localhost:5000` in your browser.
