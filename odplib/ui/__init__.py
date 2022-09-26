from pathlib import Path

from flask import Flask

STATIC_DIR = Path(__file__).parent / 'static'
TEMPLATE_DIR = Path(__file__).parent / 'templates'


def init_app(app: Flask):
    from . import auth, db, forms, templates
    auth.init_app(app)
    db.init_app(app)
    forms.init_app(app)
    templates.init_app(app)
