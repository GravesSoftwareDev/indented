web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT core.wsgi:application
