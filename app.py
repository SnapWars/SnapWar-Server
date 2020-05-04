from flask import Flask
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)
