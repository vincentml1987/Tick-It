# Tick-It

A simple IT ticketing and inventory system built with Flask and SQLite.

## Setup

Create a Python virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Initialize the database:

```bash
flask db init
flask db migrate -m "init"
flask db upgrade
```

Run the application:

```bash
python run.py
```

The API will be available at `http://localhost:5000/api/`.
