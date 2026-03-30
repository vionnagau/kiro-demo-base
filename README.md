# KiroEvents

A full-stack Flask application for managing events, contacts, and invitations.

## Features

- Create, edit, and manage events
- Manage contacts
- Send invitations and track responses
- SQLite database with proper relationships
- Error handling and form validation
- Responsive Bootstrap UI

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The database will be created automatically in the `instance/` directory when you first run the app.

4. Run tests:
```bash
pytest
```

## Usage

- Visit http://localhost:5000 to access the application
- Create events and contacts through the web interface
- Manage invitations from the event detail page

## Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `test_app.py` - Test suite
- `instance/events.db` - SQLite database (created automatically)
