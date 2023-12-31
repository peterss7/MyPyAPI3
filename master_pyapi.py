from flask import Flask, request, send_from_directory, abort
from flask_cors import CORS
from flask_restful import Api, Resource
import os
import random
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

def get_rand_from_dir_tree(search_dir):
    try:
        focused_dir = f'{base_dir}{search_dir}'
        subdirs = [f'{focused_dir}/{dir}' for dir in os.listdir(focused_dir)]
        subdir_num = len(os.listdir(focused_dir))

        isSearching = True
        dir_index = 0
        image_result = ''
        while isSearching:
            dir_index = random.randint(0, subdir_num - 1)
            if len(os.listdir(subdirs[dir_index])) > 0:
                subdir = subdirs[dir_index]
                subdir_num = len(os.listdir(subdir))
                subdir_index = random.randint(0, subdir_num - 1)
                selection = os.listdir(subdir)[subdir_index]
                selection_path = os.path.join(subdir, selection)
                isFile = os.path.isfile(selection_path)
                if isFile:
                    isSearching = False
                    image_result = send_from_directory(subdir, selection)
        return image_result
    except Exception as e:
        return None


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

class GetRandomImageDeep(Resource):
    @staticmethod
    def get():
        try: 
            result = get_rand_from_dir_tree(dir)
            if result is not None:
                return  result
            else:
                raise RandomImageException('Failed to find random image')
        except RandomImageException as e:
            return {e}, 404
        
class RandomImageException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

api.add_resource(SpecificImg, '/api/img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(DirectorySize, '/api/data/<directory>', strict_slashes=False)
api.add_resource(FileMover, '/api/move-img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(DeleteImg, '/api/delete-img/<directory>/<int:img_index>', strict_slashes=False)
api.add_resource(GetDirValidity, '/api/valid_dir/<directory>', strict_slashes=False)
api.add_resource(GetSubDirs, '/api/info/', strict_slashes=False)
api.add_resource(GetRandomImage, '/api/rnd-img', strict_slashes=False)
api.add_resource(GetRandomImageDeep, 'api/rnd-img-deep/<directory>', strict_slashes=False)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.86.26', port=5500)
