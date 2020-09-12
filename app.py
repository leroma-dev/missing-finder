# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file, jsonify
from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from os import path, getcwd
from werkzeug.utils import secure_filename
import psycopg2
import json
from datetime import datetime



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

def get_tips(id):
    query = """
        Select ppa.id, ppa.usuario_id, ppa.data, ppa.descricao_pessoa, ppa.descricao_lugar, ppa.endereco,
        u.id, u.email, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pistas_pessoa_achada as ppa
        INNER JOIN missing_finder.usuario u on u.id = ppa.usuario_id
        WHERE ppa.pessoa_achada_id = %s 
    """
    cur.execute(query, (str(id)))
    result = cur.fetchall()

    if result:
        tips = []
        for value in result:
            tip = {
                "id": value[0],
                "usuario_id": value[1],
                "data": value[2],
                "descricao_pessoa": value[3],
                "descricao_lugar": value[4],
                "endereco": value[5],
                "user": {
                    "id": value[6],
                    "email": value[7],
                    "telefone": value[8],
                    "nome": value[9],
                },
            }
            tips.append(tip)
        return tips
    return []

def buildInformationFoundPerson(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "idade": value[2],
            "pistas": get_tips(value[0])
        }
        result.append(buildData)
    return result


def buildInformationMissedPerson(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "idade": value[2],
            "data_desaparecimento": value[3],
            "parentesco": value[4],
            "mensagem_de_aviso": value[5],
            "mensagem_para_desaparecido": value[6],
            "endereco": value[7],
            "user": {
                "id": value[8],
                "email": value[9],
                "telefone": value[10],
                "nome": value[11],
            },
        }
        result.append(buildData)
    return result

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

@app.route('/api/allMissedPerson', methods=['GET'])
def missing_person():
    query = """
        select pd.id, pd.nome, pd.nascimento, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.endereco, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida as pd 
        INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id
    """
    cur.execute(query)
    result = cur.fetchall()
    return jsonify(buildInformationMissedPerson(result))

@app.route('/api/missedPerson/<id>', methods=['GET'])
def one_missing_person(id):
    query = """
        select pd.id, pd.nome, pd.nascimento, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.endereco, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida as pd 
        INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id
        WHERE pd.id = %s
    """
    cur.execute(query, (id))
    result = cur.fetchall()
    return jsonify(buildInformationMissedPerson(result))

@app.route('/api/allMissedPerson/found', methods=['GET'])
def missing_person_found():
    query = """
        select id, nome, idade FROM missing_finder.pessoa_achada
    """
    cur.execute(query)
    result = cur.fetchall()
    return jsonify(buildInformationFoundPerson(result))

@app.route('/api/missedPerson/found/<id>', methods=['GET'])
def one_missing_person_found(id):
    query = """
        select id, nome, idade FROM missing_finder.pessoa_achada WHERE id = %s
    """
    cur.execute(query, (id))
    result = cur.fetchall()
    return jsonify(buildInformationFoundPerson(result))

@app.route('/api/missedPerson/createDefaultUser', methods=['POST'])
def missing_person_createDefaultUser():
    body = request.get_json(force=True)

    query = "INSERT INTO missing_finder.usuario (nome_usuario, email, senha, telefone, nome_completo) VALUES (%s, %s, %s, %s, %s)"

    data = (body['nome_usuario'], body['email'], body['senha'], body['telefone'], body['nome_completo'])

    item = cur.execute(query, data)
    conn.commit()
 
    output = json.dumps(item)
    return success_handle(output)

@app.route('/api/missedPerson/save', methods=['POST'])
def missing_person_save():
    body = request.get_json(force=True)

    query = "INSERT INTO missing_finder.pessoa_desaparecida (nome, nascimento, data_desaparecimento, parentesco, mensagem_de_aviso, mensagem_para_desaparecido, usuario_id, endereco) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    data = (body['nome'], body['nascimento'], body['data_desaparecimento'], body['parentesco'], body['mensagem_de_aviso'], body['mensagem_para_desaparecido'], body['usuario_id'], json.dumps(body['endereco']))

    item = cur.execute(query, data)
    conn.commit()
 
    output = json.dumps(item)
    return success_handle(output)

@app.route('/api/missedPerson/save/found', methods=['POST'])
def missing_person_save_found():
    body = request.get_json(force=True)

    query = "INSERT INTO missing_finder.pessoa_achada (nome, idade) VALUES (%s, %s)"

    data = (body['nome'], body['idade'])

    item = cur.execute(query, data)
    conn.commit()
 
    output = json.dumps(item)
    return success_handle(output)

@app.route('/api/missedPerson/save/found/tip', methods=['POST'])
def missing_person_save_tip():
    body = request.get_json(force=True)

    body['data'] = datetime.today()
    print(body['data'])

    query = "INSERT INTO missing_finder.pistas_pessoa_achada (usuario_id, data, descricao_pessoa, descricao_lugar, endereco, pessoa_achada_id) VALUES (%s, %s, %s, %s, %s, %s)"

    data = (body['usuario_id'], body['data'], body['descricao_pessoa'], body['descricao_lugar'], json.dumps(body['endereco']), body['pessoa_achada_id'])

    item = cur.execute(query, data)
    conn.commit()
 
    output = json.dumps(item)
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
