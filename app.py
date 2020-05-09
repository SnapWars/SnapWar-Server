from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import firestore as google_firestore
from uuid import uuid4

app = Flask(__name__)

cred = credentials.Certificate('key.json')
initialize_app(cred)
db = firestore.client()

WARS_COLLECTION = 'wars'


@app.route('/v1/wars', methods=['POST'])
def create_war():
    war_uuid = str(uuid4())

    body = request.get_json()

    if not body:
        return jsonify({
            'request_status': 'ERROR',
            'reason': 'Empty request body'
        })

    display_name = body.get('display_name')
    timestamp = google_firestore.SERVER_TIMESTAMP

    war = {
        'uuid': war_uuid,
        'display_name': display_name,
        'images': [{body.get('external_id'): body.get('image_url')}],
        'created_at': timestamp,
        'updated_at': timestamp
    }

    db.collection(WARS_COLLECTION)\
        .document(war_uuid)\
        .set(war)

    return jsonify({
        'request_status': 'SUCCESS',
        'war': war
    })


@app.route('/v1/wars/<war_uuid>', methods=['GET'])
def get_war(war_uuid):
    doc_ref = db.collection(WARS_COLLECTION).document(war_uuid)

    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({
            'request_status': 'ERROR',
            'reason': 'War not found with uuid {}'.format(war_uuid)
        })

    return jsonify({
        'request_status': 'SUCCESS',
        'war': doc.to_dict()
    })


@app.route('/v1/wars', methods=['GET'])
def get_wars():
    wars = [doc.to_dict() for doc in db.collection(WARS_COLLECTION).stream()]

    return jsonify({
        'request_status': 'SUCCESS',
        'wars': wars
    })


@app.route('/v1/wars/<war_uuid>', methods=['PUT'])
def update_war(war_uuid):
    body = request.get_json()

    if not body:
        return jsonify({
            'request_status': 'ERROR',
            'reason': 'Empty request body'
        })

    doc = db.collection(WARS_COLLECTION).document(war_uuid).get()

    if not doc.exists:
        return jsonify({
            'request_status': 'ERROR',
            'reason': 'War not found with uuid {}'.format(war_uuid)
        })

    war = doc.to_dict()

    patch = {
        'updated_at': google_firestore.SERVER_TIMESTAMP
    }

    last_external_id = war['images'][-1]['external_id']

    external_id = body.get('external_id')
    image_url = body.get('image_url')

    if external_id and image_url:
        if external_id == last_external_id:
            return jsonify({
                'request_status': 'ERROR',
                'reason': 'User external id cannot be the same for consecutive images in war'
            })
        patch['images'] = war['images'] + [{external_id: image_url}]
    doc.update(patch)

    return jsonify({
        'request_status': 'SUCCESS',
        'war': war.update(patch)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
