# Chat Django + DRF + Channels (WS)

## Installation
pip install -r requirements.txt
# or at minimum:
pip install django djangorestframework channels channels-redis daphne

## Important
- `daphne` must be in `INSTALLED_APPS` so that `python manage.py runserver` starts the ASGI/Daphne server.
- WebSocket URL: ws://127.0.0.1:8000/ws/chat/<room>/

## Run
python manage.py migrate
python manage.py runserver

If you prefer launching daphne directly:
daphne -b 127.0.0.1 -p 8000 monsite.asgi:application
