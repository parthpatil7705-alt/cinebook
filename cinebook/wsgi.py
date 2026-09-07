"""
WSGI config for CineBook project.
"""
import os
import sys
from pathlib import Path

# Add the root directory to sys.path
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinebook.settings.development')
application = get_wsgi_application()
app = application
