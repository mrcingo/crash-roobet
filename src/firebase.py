import firebase_admin
from firebase_admin import db

import config


# Authentication credentials for Firebase
CREDENTIALS = firebase_admin.credentials.Certificate(config.FIREBASE_CERTIFICATE)

# Setup Firebase app admin
firebase_admin.initialize_app(CREDENTIALS, 
                              { 'databaseURL': config.FIREBASE_DATABASE_URL })

# Realtime Firebase database
DATABASE = db.reference(config.FIREBASE_DATABASE_REF)
