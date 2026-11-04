# Rental Management

An offline Windows desktop rental management application built with Flask,
SQLite and Tailwind CSS.

## Requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.12 or newer
- Tailwind CSS v4 standalone CLI

## Development

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python run.py
```

Open:

http://127.0.0.1:5000

## Tailwind CSS

Compile the stylesheet:

```powershell
.\tools\tailwindcss.exe -i .\app\static\css\input.css -o .\app\static\css\app.css --watch
```

For a production build, use `--minify` instead of `--watch`.

## Database

The development SQLite database is stored in Flask's instance directory.

The final packaged application will use a persistent data directory
outside the installation folder so that application updates do not
overwrite business data.

## Default currency

KES (Kenyan Shilling).