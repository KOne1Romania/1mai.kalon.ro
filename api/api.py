import os

from flask import Flask, make_response, redirect, json, request
from flask.ext.mongoengine import MongoEngine
from flask_restful import Resource, Api

from config import HOST, MONGODB_SETTINGS, ALLOWED_EXTENSIONS, UPLOAD_FOLDER

db = MongoEngine()
app = Flask('1mai')
# App configuration
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS

# Start services
db.init_app(app)
api = Api(app)


class Card(db.Document):
    name = db.StringField(max_length=70, required=True)
    photo_path = db.StringField(max_length=70, required=True)


class GetCardResource(Resource):
    def get(self, card_id):
        data_object = Card.objects.get_or_404(id=card_id)
        return raw_object(data_object)


class CreateCardResource(Resource):
    def post(self):
        args = json.loads(request.data)
        photo = request.files.get('file')

        if not photo:
            return redirect('/card/create')

        if photo and allowed_file(photo.filename):
            photo_filename = secure_filename(photo.filename)
            try:
                photo_path = photo.save(
                    os.path.join(UPLOAD_FOLDER, photo_filename))

            except Exception as e:
                return {'message': "Error saving photo: {0}".format(e)}

        try:
            card = Card(name=args['name'], photo_path=photo_path).save()
        except Exception as e:
            return {'message': "Error saving card: {0}".format(e)}

        return redirect('/card/%d' % card.id)


def allowed_file(photo_filename):
    if ('.' in photo_filename and
        photo_filename.split('.')[1] in app.config['ALLOWED_EXTENSIONS']):
        return True
    return False


api.add_resource(GetCardResource, '/card/<card_id>')
api.add_resource(CreateCardResource, '/card/create')


if __name__ == '__main__':
    app.run(host=HOST, debug=True)
