# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file
from werkzeug.utils import secure_filename
from os import path, getcwd

from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle

app = Flask(__name__)

app.config.from_object('config.Config')
assets: str = app.config['ASSETS']
app.face = FaceRecognition(storageFolderPath='{}/storage/'.format(assets),
                           knownFolderPath='{}/known/'.format(assets),
                           unkwonFolderPath='{}/unknown/'.format(assets),
                           outputFolderPath='{}/output'.format(assets))
# app.face.parseKnownFaces()


def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": error_message}), status=status, mimetype=mimetype)

# route for homepage
@app.route('/', methods=['GET'])
def page_home():

    return render_template('index.html')

#
@app.route('/api', methods=['GET'])
def homepage():
    output = json.dumps({"api": '1.0'})
    return success_handle(output)


# route to train a face
@app.route('/api/train', methods=['POST'])
def train():
    return_output = json.dumps({"success": True})

    if 'file' not in request.files:

        print("Face image is required")
        return error_handle("Face image is required.")
    else:

        print("File request", request.files)
        file = request.files['file']

        if file.mimetype not in app.config['FILE_ALLOWED']:

            print("File extension is not allowed")

            return error_handle("Imagens suportadas: *.png , *.jpg")
        else:

            # get name in form data
            name = request.form['hash']

            print("Information of that face", name)

            print("File is allowed and will be saved in ", app.config['ASSETS'])
            filename = secure_filename(name+'.jpg')
            trained_storage = path.join(app.config['ASSETS'], 'known')
            file_path = path.join(trained_storage, filename)
            file.save(file_path)

            faceBundle = app.face.addKnownFace(file_path)

            return_output = json.dumps(faceBundle.toData())
            # return_output = json.dumps({"success": True, "name": name, "face": [json_data]}, indent=2, sort_keys=True)
            #         return success_handle(return_output)
            #         return error_handle("error message")

    print(return_output)
    return success_handle(return_output)

# route for extract faces from image/video
# TODO: it may be not used.
@app.route('/api/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return error_handle("Image or Video is required")
    else:
        file = request.files['file']
        if file.mimetype not in app.config['FILE_ALLOWED']:
            return error_handle("File extension is not allowed")
        else:

            filename = secure_filename(file.filename)
            unknown_storage = path.join(app.config["ASSETS"], 'extract')
            file_path = path.join(unknown_storage, filename)
            file.save(file_path)

            faces = app.face.pullFaces(file_path)

            data_output = ""

            for face in faces:
                # print(face.toData())
                data_output += json.dumps(face.toData())
                # return_output += json.dumps(face.__dict__)

            return_output = json.dumps({"success": True, "number": len(faces), "data": data_output})
            return success_handle(return_output)

            #         return_output = json.dumps({"name": name, "face": [face_data]})
            #         return success_handle(return_output)
            #         return error_handle("error message")

# route for recognize a unknown face
@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return error_handle("Image or Video is required")
    else:
        file = request.files['file']
        id = request.form['id']
        if file.mimetype not in app.config['FILE_ALLOWED']:
            return error_handle("File extension is not allowed")
        else:
            filename = secure_filename(file.filename)
            unknown_storage = path.join(app.config["ASSETS"], 'unknown')
            file_path = path.join(unknown_storage, filename)
            file.save(file_path)

            if file.mimetype in app.config['SUPPORTED_VIDEOS_EXT']:
                frame_list = app.face.videoRecognition(file_path, id=id)
                if len(frame_list) > 0:
                    aux_list = []
                    for frame in frame_list:
                        aux_list.append(frame.to_data())
                    return_output = json.dumps(aux_list)
                else:
                    return error_handle("Nenhuma face reconhecida no video.")
            else:
                name_list = app.face.findMatches(file_path, id=id)
                if len(name_list):
                    return_output = json.dumps({"path": "./assets/output/result_"+id+".jpg", "name": [name_list]}, indent=2, sort_keys=True)
                else:
                    return error_handle("Face não reconhecida na imagem.")
            return success_handle(return_output)

# route to get frame image
@app.route('/video/<string:rid>/<int:frame>', methods=['GET'])
def get_frame(rid, frame):
    file_path = app.config['ASSETS']+'/output/result_{}_{}.jpg'.format(rid, frame)
    # if parameter ?return=path
    if request.args.get('return') == 'path':
        # return path for video image frame
        return_output = json.dumps({"rid": rid, "frame": frame, "path": file_path}, indent=2, sort_keys=True)
        return success_handle(return_output)
    else:
        # return video image frame
        print('File Path: {}'.format(file_path))
        return send_file(file_path)

# route to get image
@app.route('/image/<string:rid>', methods=['GET'])
def get_image(rid):
    file_path = app.config['ASSETS']+'/output/result_{}.jpg'.format(rid)
    # if parameter ?return=path
    if request.args.get('return') == 'path':
        # return path for image
        return_output = json.dumps({"rid": rid, "path": file_path}, indent=2, sort_keys=True)
        return success_handle(return_output)
    else:
        # return image
        return send_file(file_path)

# route to get image
@app.route('/known/<string:id>', methods=['GET'])
def get_known(id):
    file_path = app.config['ASSETS']+'/known/{}.jpg'.format(id)
    # return image
    return send_file(file_path)

# route to register facebundle list
@app.route('/register-list', methods=['POST'])
def register_list(face_list: list):
    if isinstance(list, face_list):
        for face in face_list:
            if isinstance(FaceBundle, face):
                app.face.add_known(face)
            else:
                error_handle('Not a Valid Path Variable')
                return
        success_handle('Done!')
    else:
        error_handle('Not a Valid Path Variable')

@app.route('/retrieve', methods=['POST'])
def retrieve_images():
    if 'id' in request.form:
        request_id = request.form['id']
    else:
        return error_handle('Need an id to search')

    if 'face_id' in request.form:
        face_id = request.form['face_id']
    else:
        return error_handle('Need an id to search')

    if 'face' in request.form:
        face_json: str = request.form['face']
        print(face_json)
        face: FaceBundle = FaceBundle.parseJson(json.loads(face_json))
        # return success_handle(json.dumps({'message': 'Face {} was added'.format(face.getName())}))
    else:
        return error_handle('No face file provided')

    app.face.add_known(face)
    number_of_files = app.face.mark_face(face_id)
    return_output = json.dumps({"face_id": face_id, "nfiles": number_of_files}, indent=2, sort_keys=True)
    return success_handle(return_output)

# route to get image for group
@app.route('/image/<string:face_id>/<string:file_number>', methods=['GET'])
def get_image_group(face_id, file_number):
    file_path = app.config['ASSETS']+'/output/result_{}_{}.jpg'.format(face_id, file_number)
    # if parameter ?return=path
    if request.args.get('return') == 'path':
        # return path for image
        return_output = json.dumps({"face_id": face_id, "path": file_path}, indent=2, sort_keys=True)
        return success_handle(return_output)
    else:
        # return image
        return send_file(file_path)


# Run the app
app.run(host=app.config['FLASK_RUN_HOST'], port=app.config['FLASK_RUN_PORT'])
