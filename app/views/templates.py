from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Templates directory - create if doesn't exist
TEMPLATES_DIR = BASE_DIR / "views" / "templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Static directory - create if doesn't exist
STATIC_DIR = BASE_DIR / "static"
os.makedirs(STATIC_DIR, exist_ok=True)

# Templates configuration
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Function to render template with common data
def render_template(request: Request, template_name: str, data: dict = None):
    """
    Render a template with common data
    """
    context = {"request": request}
    
    if data:
        context.update(data)
    
    return templates.TemplateResponse(template_name, context) 