import json

from datetime import datetime, timezone
from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
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
        return _error(reason='Empty request body')

    display_name = body.get('display_name', None)

    if not display_name:
        return _error(reason='No display name provided')

    external_user_id = body.get('external_user_id', None)
    image_url = body.get('image_url', None)

    if not external_user_id or not image_url:
        return _error(reason='No external user id or image url provided')

    timestamp = datetime.now(timezone.utc)

    war = {
        'uuid': war_uuid,
        'display_name': display_name,
        'images': [{'external_user_id': external_user_id,
                    'image_url': image_url}],
        'created_at': str(timestamp),
        'updated_at': str(timestamp)
    }

    db.collection(WARS_COLLECTION)\
        .document(war_uuid)\
        .set(war)

    return jsonify({
        'request_status': 'SUCCESS',
        'war': json.dumps(war)
    })


@app.route('/v1/wars/<war_uuid>', methods=['GET'])
def get_war(war_uuid):
    doc = db.collection(WARS_COLLECTION)\
        .document(war_uuid)\
        .get()

    if not doc.exists:
        return _error(reason='War not found with uuid {}'.format(war_uuid))

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
        return _error(reason='Empty request body')

    doc = db.collection(WARS_COLLECTION)\
        .document(war_uuid)\
        .get()

    if not doc.exists:
        return _error(reason='War not found with uuid {}'.format(war_uuid))

    war = doc.to_dict()

    patch = {
        'updated_at': str(datetime.now(timezone.utc))
    }

    last_external_user_id = war['images'][-1]['external_user_id']

    display_name = body.get('display_name', None)

    if display_name:
        patch['display_name'] = display_name

    external_user_id = body.get('external_user_id', None)
    image_url = body.get('image_url', None)

    if external_user_id and image_url:
        if external_user_id == last_external_user_id:
            return _error(reason='User external id cannot be the same for consecutive images in war')

        patch['images'] = war['images'] + [{
            'external_user_id': external_user_id,
            'image_url': image_url
        }]

    db.collection(WARS_COLLECTION)\
        .document(war_uuid)\
        .update(patch)

    war.update(patch)

    return jsonify({
        'request_status': 'SUCCESS',
        'war': war
    })


def _error(reason):
    return jsonify({
        'request_status': 'ERROR',
        'reason': reason
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
