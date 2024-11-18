import os
import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# from django.core.management import execute_from_command_line
# from django.core.wsgi import get_wsgi_application

# application = get_wsgi_application()


# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '8000'])