import bson
from werkzeug.exceptions import BadRequest
from werkzeug.routing import BaseConverter


class ObjectIdConverter(BaseConverter):
    '''Converts string to :class:`~bson.objectid.ObjectId` and
    vise versa::
        @app.route('/users/<ObjectId:user_id>', methods=['GET'])
        def get_user(user_id):
            ...
    To register it in `Flask`, add it to converters dict::
        app.url_map.converters['ObjectId'] = ObjectIdConverter
    Alternative registration way::
        ObjectIdConverter.register_in_flask(app)
    '''

    def to_python(self, value):
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId as e:
            raise BadRequest(e)

    def to_url(self, value):
        return str(value)

    @classmethod
    def register_in_flask(cls, flask_app):
        flask_app.url_map.converters['ObjectId'] = cls
