import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
from flask import current_app
import os

# Firebase Admin SDK (để truy cập Firestore, Auth, Storage, v.v.)
firebase_app = None
firestore_db = None

# Pyrebase (dễ sử dụng hơn cho Firebase Auth)
firebase = None
auth = None


def init_firebase():
    global firebase_app, firestore_db, firebase, auth

    # Khởi tạo Firebase Admin SDK
    cred = credentials.Certificate("swap.json")

    firebase_app = firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()

    # Khởi tạo Pyrebase
    firebase_config = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID'),
        'measurementId': os.environ.get('FIREBASE_MEASUREMENT_ID')
    }

    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()


def get_firestore_db():
    return firestore_db


def get_firebase_auth():
    return auth