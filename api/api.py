import os

from flask import Flask, make_response, redirect, json, request
from flask.ext.mongoengine import MongoEngine
from werkzeug import secure_filename

from config import HOST, MONGODB_SETTINGS, ALLOWED_EXTENSIONS, UPLOAD_FOLDER

db = MongoEngine()
app = Flask('1mai')
# App configuration
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
app.config['DEFAULT_PARSERS'] = [
    'flask.ext.api.parsers.JSONParser',
    'flask.ext.api.parsers.URLEncodedParser',
    'flask.ext.api.parsers.MultiPartParser'
]
# Start services
db.init_app(app)

class Card(db.Document):
    name = db.StringField(max_length=70, required=True)


def allowed_file(photo_filename):
    if ('.' in photo_filename and
        photo_filename.split('.')[1] in app.config['ALLOWED_EXTENSIONS']):
        return True
    return False


@app.route('/card/create')
def card_create():
    name = request.form.get('name')
    photo = request.files.get('file')

    if not name or photo:
        return redirect('/card/create')

    try:
        card = Card(name=args['name']).save()
    except Exception as e:
        return {'message': "Error saving card: {0}".format(e)}

    if photo and allowed_file(photo.filename):
        photo_filename = secure_filename(photo.filename)
        try:
            photo_filename = "%s.%s" % (card.id, photo.filename.split('.')[1])
            photo_path = photo.save(
                os.path.join(UPLOAD_FOLDER, photo_filename))

        except Exception as e:
            return {'message': "Error saving photo: {0}".format(e)}

    return redirect('/card/%d' % card.id)


app.add_url_rule('/card/create', 'create_card', card_create, methods=['POST'])


if __name__ == '__main__':
    app.run(host=HOST, debug=True)
