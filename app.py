#!flask/bin/python
import six
from PIL import Image
from flask import Flask, jsonify, abort, request, make_response, url_for, Response, send_file
from flask_restful import Api, Resource, reqparse, fields, marshal
from pathlib import Path
from dotenv import load_dotenv
from source.database import Database, create_table
import os, io
import json
from source.config import app_config
from source.models.image import ImageEntity
from source.utils.handle import *
from source.views.imageView import *
import logging
from logging.config import fileConfig
from source.repository.image import imageImpl as image_repository_interface
from source.repository.handle import *

fileConfig('source/logging_config.ini')


env_path = Path('.') / '.env_example'
load_dotenv(verbose=True, dotenv_path=env_path, override=True)

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
PORT = os.getenv("PORT")

Database.initialise(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)

app = Flask(__name__, static_url_path="")
app.config.from_object(app_config[os.getenv('FLASK_MODE')])
api = Api(app)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/")
def hello():
    return make_response(jsonify({'message': 'Hello world'}), 200)


class PostImage(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PostImage, self).__init__()

    def post(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            message = CustomResponse(
                False,
                "No file part", 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res
            
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename    
        if file.filename == '':
            message = CustomResponse(
                False,
                "Malformed Data", 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        img = Image.open(file.stream)  # PIL image
        """
        JPG not support alpha = transparency
        RGBA, P has alpha = transparency
            RGBA= Red Green Blue Alpha

        solution
        --> before save to JPG, discard alpha = transparency
            such as: convert Image to RGB
        then save to JPG
        """ 
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # save image to database
        texture = io.BytesIO()
        img.save(texture, format="JPEG")
        texture = texture.getvalue()

        file_name = os.path.splitext(file.filename)[0]
        image_entity = ImageEntity(texture)

        img_repo = image_repository_interface.NewImageRepository()
        status, img_object = img_repo.upload_image(image_entity, file_name)
        if not status_as_bool(status):
            message = CustomResponse(
                status_as_bool(status),
                status_as_string(status), 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        # return 
        imageFactory = ImageSchema()
        ser_data = imageFactory.dump(img_object)
        message = CustomResponse(
            status_as_bool(status),
            status_as_string(status),
            ser_data,
        )
        message.__dict__['code'] = 90001

        rep_message = json.dumps(message.__dict__, sort_keys=False)
        res = Response(rep_message, content_type='application/json', status=201)
        return res

class SearchImage(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(SearchImage, self).__init__()
    def post(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            message = CustomResponse(
                False,
                "No file part", 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename    
        if file.filename == '':
            message = CustomResponse(
                False,
                "Malformed Data", 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        offset = request.form.get('offset') 
        limit = request.form.get('limit')

        # Run load more for infinite scroll
        img_repo = image_repository_interface.NewImageRepository()
        status, load_more_object = img_repo.load_more_images(offset, limit)
        if not status_as_bool(status):
            message = CustomResponse(
                status_as_bool(status),
                status_as_string(status), 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        img = Image.open(file.stream)  # PIL image
        # Run Search
        img_repo = image_repository_interface.NewImageRepository()
        status, search_object = img_repo.search_image(img, load_more_object)
        if not status_as_bool(status):
            message = CustomResponse(
                status_as_bool(status),
                status_as_string(status), 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        # return 
        searchFactory = SearchView()
        ser_data = searchFactory.dump(search_object, many=True)
        message = CustomResponse(
            status_as_bool(status),
            status_as_string(status),
            ser_data,
        )
        message.__dict__['code'] = 90000

        rep_message = json.dumps(message.__dict__, sort_keys=False)
        res = Response(rep_message, content_type='application/json', status=200)
        return res
        
class ViewImage(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ViewImage, self).__init__()

    def get(self, id):
        if id.isalnum() == False:
            message = CustomResponse(
                False,
                "Malformed Data", 
                [],
            )
            message.__dict__['code'] = 90006

            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        # Run Get Image Texture
        img_repo = image_repository_interface.NewImageRepository()
        status, image_object = img_repo.get_image_by_name(id)
        if not status_as_bool(status):
            message = CustomResponse(
                status_as_bool(status),
                status_as_string(status), 
                [],
            )
            message.__dict__['code'] = 90006

            # return error
            rep_message = json.dumps(message.__dict__, sort_keys=False)
            res = Response(rep_message, content_type='application/json', status=400)
            return res

        """
        buffer_display handle serving image
        buffer_file_extension handle detecting file formats
        """
        buffer_display = io.BytesIO(image_object['texture'])
        buffer_file_extension = io.BytesIO(image_object['texture'])
        img = Image.open(buffer_file_extension)

        # return
        """
        adding argument `as_attachment` to send_file 
            if you want the browser to save the file
            instead of displaying it 
        rememeber to set attachment filename if `as_attachment` set to True
        """
        return send_file(
            buffer_display,
            mimetype=Image.MIME[img.format],
        )

api.add_resource(PostImage, '/upload/images', endpoint='upload', methods=['POST'])
api.add_resource(SearchImage, '/search/images', endpoint='search', methods=['POST'])
api.add_resource(ViewImage, '/images/<id>', endpoint='view', methods=['GET'])

if __name__ == '__main__':
    HOST = os.getenv("APP_SERVICE")
    PORT = os.getenv("APP_PORT")

    create_table()
    app.run(host=HOST, port=int(PORT))