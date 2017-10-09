web: python app.py
release: python release.py && python manage.py db init && python manage.py db migrate && python manage.py db upgrade
weekly_emails: python -m src.tasks.send_weekly_emails