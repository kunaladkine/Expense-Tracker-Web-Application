# Django Expense Tracker (Full Version)

This is a ready-to-run Django Expense Tracker app.

How to run locally:

1. Create virtualenv and activate:
   python -m venv env
   # Windows:
   env\Scripts\activate

2. Install requirements:
   pip install -r requirements.txt

3. Run migrations and create superuser:
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser

4. Run server:
   python manage.py runserver

Visit http://127.0.0.1:8000/

