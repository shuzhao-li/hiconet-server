web: gunicorn cruncher.wsgi:application --preload
worker: celery --without-gossip --without-mingle --without-heartbeat -A cruncher worker -l info
