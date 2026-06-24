web: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py ensure_superuser && gunicorn --bind 0.0.0.0:$PORT core.wsgi:application
