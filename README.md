# ASA-Database
Database for ASA's Lepidoptera Research
to run: `python manage.py runserver`

This project supports both a networked (multi-user) mode and a simple client (user) mode.

## For the Host (Server)
- See `host/README.md` for step-by-step instructions to set up and run the server on your network.

## For Users (Clients)
- See `client/README.md` for how to connect from any device with a browser.
- See `client/desktop_shortcut_instructions.txt` to create a desktop shortcut for easy access.

## Project Structure
- `host/` — Host/server setup guide
- `client/` — Client/user guide and shortcut instructions
- `docker-compose.yml`, `Dockerfile`, `run.sh` — Main server stack files
- `research_data_app/`, `butterflies/` — Django app code

## Data Migration & Backup
- To move the server, copy the whole project folder (including `postgres_data`)
- To add or remove fields in the database, modify their definitionsin `butterflies/views.py`
- Make migrations for the app, run: `python manage.py makemigrations butterflies`
- Apply migrations to the database, run: `python manage.py migrate`


- IF you want to erase all data, back up the data beforehand!!! and run: `python manage.py flush`

## Support
This project is designed to be as low-maintenance and user-friendly as possible. All instructions are included for both host and client roles.
# ASA-Database
Database for ASA's Lepidoptera Research
to run: `python manage.py runserver`