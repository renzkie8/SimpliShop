import sys
import os

# Add the 'src' directory to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import flet.fastapi as flet_fastapi

from main import main

# This 'app' object is what Azure App Service (Uvicorn/Gunicorn) will look for.
app = flet_fastapi.app(main)
