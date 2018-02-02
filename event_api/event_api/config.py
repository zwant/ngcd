# Enable Flask's debugging features. Should be False in production
DEBUG = True
PORT = 5001
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5432/event_api'
SQLALCHEMY_TRACK_MODIFICATIONS = 'false'
