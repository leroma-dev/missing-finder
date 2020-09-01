# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file, jsonify
from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from os import path, getcwd
from werkzeug.utils import secure_filename
import psycopg2
import json
from datetime import date


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

conn = psycopg2.connect(
    host = '127.0.0.1',
    database = 'postgres',
    user = 'postgres',
    password = 'mysecretpassword'
)
cur = conn.cursor()

def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": error_message}), status=status, mimetype=mimetype)

# route for homepage
@app.route('/', methods=['GET'])
def page_home():
    return render_template('index.html')


@app.route('/api', methods=['GET'])
def homepage():
    output = json.dumps({"api": '1.0'})
    return success_handle(output)

@app.route('/api/allMissingPerson', methods=['GET'])
def missing_person():
    cur.execute("select * FROM missing_finder.pessoa_desaparecida as pd INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id;")
    result = cur.fetchall()
    return jsonify(buildInformation(result))

@app.route('/api/missedPerson/<id>', methods=['GET'])
def one_missing_person(id):
    cur.execute("select * FROM missing_finder.pessoa_desaparecida as pd INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id where pd.id = %s;", (id))
    result = cur.fetchall()
    return jsonify(buildInformation(result))

def buildInformation(values):
    result = []
    for value in values:
        buildData = {
            "id": value[1],
            "nome": value[0],
            "idade": value[3],
            "data_desaparecimento": value[4],
            "parentesco": value[5],
            "mensagem_de_aviso": value[6],
            "mensagem_para_desaparecido": value[7],
            "status_desaparecido": value[8],
            "endereco": value[9],
            "user": {
                "nome": value[14],
                "email": value[12],
                "telefone": value[13]
            }
        }
        result.append(buildData)
    return result


# @app.route('/api/allMissingPerson', methods=['GET'])
# def get_all_missing_person():
#     item = user_controller.get_all_missed_person()
#     return (item)

# body request with the data to save {
#     "id": 1,            //Number
#     "name": "janedoe",  //String
#     "age": 25,          //Number
# }
@app.route('/api/missingPerson/save', methods=['POST'])
def missing_person_save():
    body = request.get_json(force=True)

    query = "INSERT INTO missing_finder.pessoa_desaparecida (nome, nascimento, data_desaparecimento, parentesco, mensagem_de_aviso, mensagem_para_desaparecido, usuario_id, endereco, status_desaparecido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    data = (body['nome'], body['nascimento'], body['data_desaparecimento'], body['parentesco'], body['mensagem_de_aviso'], body['mensagem_para_desaparecido'], body['usuario_id'], json.dumps(body['endereco']), body['status_desaparecido'])

    item = cur.execute(query, data)
    conn.commit()
 
    output = json.dumps(item)
    return success_handle(output)

# @app.route('/api/missingPerson/update/<user_id>/<user_type>', methods=['PUT'])
# def missing_person_update(user_id, user_type):
#     output = user_controller.update_state_person_found(user_id, user_type)
#     return (output)

# @app.route('/api/missingPerson/remove/<id>/<type>', methods=['PUT'])
# def missing_person_soft_delete(id, type):
#     output = user_controller.soft_delete_missed_person(id, type)
#     return (output)

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
