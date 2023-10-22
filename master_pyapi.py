from flask import Flask, request, jsonify, send_file, send_from_directory, abort
from flask_cors import CORS
from flask_restful import Api, Resource
import os
import sys
import json
import random
import base64
import shutil
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
base_dir: str = "C:/...../"
app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def directory_exists(cur_dir):
    return os.path.exists(cur_dir) and os.path.isdir(cur_dir)


class SpecificImg(Resource):
    @staticmethod
    def get(directory, img_index):
        cur_dir = f"{base_dir}{directory}"
        try:
            if cur_dir:
                if not directory_exists(cur_dir):
                    raise FileNotFoundError
                else:
                    img_filename = os.listdir(cur_dir)[img_index]
                    return send_from_directory(cur_dir, img_filename)
        except FileNotFoundError:
            return {"ERROR": "File not found."}, 404
        

class DirectorySize(Resource):
    @staticmethod
    def get(directory):
        cur_dir = f"{base_dir}{directory}"
        return len(os.listdir(cur_dir))


class FileMover(Resource):
    @staticmethod
    def post(directory, img_index):
        data = request.json
        target_dir_data = data.get('target')
        source_img_index = img_index
        target_dir = f"{base_dir}{target_dir_data}"
        source_dir = f"{base_dir}{directory}"
        try:
            source_img = os.listdir(source_dir)[source_img_index]
            destination_img = f"{target_dir}/{source_img}"
            if not directory_exists(target_dir):
                os.makedirs(target_dir)
            source_path = f"{source_dir}/{source_img}"
            shutil.move(source_path, destination_img)
            return {'message': 'File was moved.'}, 200
        except Exception as e:
            return {'Error': f'File was not moved: {str(e)}'}, 500


class DeleteImg(Resource):
    @staticmethod
    def delete(directory, img_index):
        target_dir = f"{base_dir}{directory}"
        if not directory_exists(target_dir):
            return {"ERROR": f"Directory: {target_dir} does not exist."}, 404
        target_img = os.listdir(target_dir)[img_index]
        if not target_img:
            abort(404)
        img_fullpath = f"{target_dir}/{target_img}"
        try:
            os.remove(img_fullpath)
            return {"Image deleted: ": f"{img_fullpath}"}, 200
        except FileNotFoundError:
            return {f"Could not delete: {img_fullpath}"}, 500


class GetDirValidity(Resource):
    @staticmethod
    def get(directory):
        cur_dir = base_dir + directory
        return directory_exists(cur_dir)


class GetSubDirs(Resource):
    @staticmethod
    def get():
        return [directory for directory in os.listdir(base_dir) if
                os.path.isdir(os.path.join(base_dir, directory))]
    
class GetRandomImage(Resource):
    @staticmethod
    def get():
        index = random.randint(0, len(os.listdir(base_dir)) - 1)
        try:
            return send_from_directory(base_dir, os.listdir(base_dir)[index])
        except FileNotFoundError as e:
            return {e}, 404
        except Exception as e:
            return {e}, 404


api.add_resource(SpecificImg, '/api/img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(DirectorySize, '/api/data/<directory>', strict_slashes=False)
api.add_resource(FileMover, '/api/move-img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(DeleteImg, '/api/delete-img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(GetDirValidity, '/api/valid_dir/<directory>', strict_slashes=False)
api.add_resource(GetSubDirs, '/api/info/', strict_slashes=False)
api.add_resource(GetRandomImage, '/api/rnd-img', strict_slashes=False)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.86.36', port=5500)
