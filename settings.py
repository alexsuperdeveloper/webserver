import os

BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, 'database.sqlite')
SQL_PATH = os.path.join(BASE_DIR, 'sql/')
TEMPLATES = os.path.join(BASE_DIR, 'templates/')
STATIC = os.path.join(BASE_DIR, 'static/')
IMAGES = os.path.join(STATIC, 'images/')
