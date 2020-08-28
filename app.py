# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file, jsonify
from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from os import path, getcwd
from werkzeug.utils import secure_filename
from pymongo import MongoClient, ReturnDocument
from bson.json_util import loads
from bson.json_util import dumps
from bson.objectid import ObjectId


app = Flask(__name__)
app.config.from_object('config.Config')

assets: str = app.config['ASSETS']
s3_util = S3Util('mantovanellos-bucket')
app.face = FaceRecognition(storageFolderPath='storage/',
                           knownFolderPath='known/',
                           unknownFolderPath='unknown/',
                           outputFolderPath='output/',
                           s3_util=s3_util)
# app.face.parseKnownFaces()

client = MongoClient('mongodb://localhost:27017/test')
db = client['test_database']


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

# API missing person
@app.route('/api/missingPerson/<id>/<status>', methods=['GET'])
def missing_person(id, status):
    cursor = db.missed.find_one({
        "_id": ObjectId(id),
        "status": status,
    })
    print(cursor)
    result = loads(json.dumps(cursor, default=str))
    return jsonify(result)

@app.route('/api/allMissingPerson', methods=['GET'])
def get_all_missing_person():
    cursor = list(db.missed.find())
    result = loads(json.dumps(cursor, default=str))
    return jsonify(result)

@app.route('/api/missingPerson/save', methods=['POST'])
def missing_person_save():
    body = request.get_json()
    result = db.missed.insert_one(body)
    return success_handle(result)

@app.route('/api/missingPerson/updateStatus/<id>/<status>', methods=['PUT'])
def missing_person_update(id, status):
    output = db.missed.find_one_and_update(
        { "_id": ObjectId(id) },
        { "$set": { "status": status }},
    )
    result = loads(json.dumps(output, default=str))
    return jsonify(result)
# API missing person

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
            # name = request.form['hash']
            user_id = request.form['id']
            name = request.form['name']
            age = request.form['age']


            print("Information of that face", name)
            print("File is allowed and will be saved in AWS S3 bucket folder")

            filename = secure_filename(name+'.jpg')
            file_path = path.join('known/', filename)
            file_content = file.read()

            body = {"id": int(user_id), "name": name, "age": int(age)}
            item = user_controller.save_missed_person(body)
            output = json.dumps(item)

            s3_path = "missing/" + user_id + "/" + filename

            s3_util.upload_file(file_content=file_content, object_name=s3_path)

            # faceBundle = app.face.addKnownFace(file_path, file_content=file_content)
            faceBundle = app.face.addKnownFace(s3_path, file_content=file_content)

            return_output = output + json.dumps(faceBundle.toData())
            # return_output = json.dumps({"success": True, "name": name, "face": [json_data]}, indent=2, sort_keys=True)
            #         return success_handle(return_output)
            #         return error_handle("error message")
    print(return_output)
    return success_handle(return_output)

# route for recognize a unknown face
@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return error_handle("Image or Video is required")
    else:
        file = request.files['file']
        id = request.form['id']
        if 'tolerance' in request.form:
            tolerance = float(request.form['tolerance'])
        else:
            tolerance = 0.6
        if file.mimetype not in app.config['FILE_ALLOWED']:
            return error_handle("File extension is not allowed")
        else:
            filename = secure_filename(file.filename)
            file_path = path.join('unknown/', id+"_"+filename)
            file_content = file.read()

            s3_util.upload_file(file_content=file_content, object_name="unknown/"+id+"_"+filename)

            name_list = app.face.findMatches(file_path, tolerance, id=id)
            if len(name_list):
                return_output = json.dumps({"path": "S3 Bucket - ./output/result_"+id+".jpg", "name": [name_list]}, indent=2, sort_keys=True)
            else:
                return error_handle("Face não reconhecida na imagem.")
        return success_handle(return_output)

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

# Run the app
app.run(host=app.config['FLASK_RUN_HOST'], port=app.config['FLASK_RUN_PORT'])
