"""Settings configuration - Configuration for environment variables can go
in here."""

import os
from decouple import config

ENV = config('FLASK_ENV', default='production')
DEBUG = ENV == 'development'
SQLALCHEMY_DATABASE_URI = config('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
