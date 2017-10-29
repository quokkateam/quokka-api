web: python app.py
release: python release.py && python manage.py db init && python manage.py db migrate && python manage.py db upgrade && python -m src.tasks.remove_duke_challenges