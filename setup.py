import os
import sys
import site
from cx_Freeze import setup, Executable

# Gather all Django-related dependencies
# PYTHON_PACKAGES = os.path.join(os.path.dirname(sys.__file__), 'site-packages')
PYTHON_PACKAGES = site.getsitepackages()[0]

includes = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'members',  # Your app name
]

# Include all required Django files and dependencies
include_files = [
    (os.path.join(PYTHON_PACKAGES, 'django'), 'django'),
    'config/',
    'manage.py',
    'members/',  # Your project directory
    'media/',
    'static/',      # Static files directory
    'templates/',   # Templates directory
    'db.sqlite3',   # Database file
]

# Basic cx_Freeze options
build_options = {
    'packages': includes,
    'include_files': include_files,
    'excludes': [],
    'include_msvcr': True,
}

# Create the executable
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Use this for Windows GUI applications

setup(
    name='ChashmaGYM',
    version='1.0',
    description='ChashmaGYM Desktop Application',
    options={'build_exe': build_options},
    executables=[
        Executable(
            'run_server.py',  # This is the entry point script we'll create next
            base=base,
            target_name='ChashmaGYM.exe',
            icon='./static/images/desktopIcon.png'  # Optional: Add your icon
        )
    ]
)