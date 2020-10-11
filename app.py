# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file, jsonify
from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from os import path, getcwd
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import json
from datetime import datetime
import asyncio
from flask_login import login_user, login_manager
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config.from_object('config.Config')

assets: str = app.config['ASSETS']
s3_util = S3Util('missing-finder-bucket')
# app.face.parseKnownFaces()

conn = psycopg2.connect(
    host = '127.0.0.1',
    database = 'postgres',
    user = 'postgres',
    password = 'mysecretpassword'
)
cur = conn.cursor()

app.face = FaceRecognition(storageFolderPath='storage/',
                           knownFolderPath='known/',
                           unknownFolderPath='unknown/',
                           outputFolderPath='output/',
                           s3_util=s3_util,
                           cur=cur)

# login_manager = LoginManager()
# login_manager.init_app(app)

def buildInformationFoundPerson(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "idade": value[2],
            "ativo": value[3],
            "tip": value[4],
            "encoding": value[5]
        }
        result.append(buildData)
    return result

def buildInformationMissedPerson(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "data_nascimento": value[2],
            "idade": value[3],
            "data_desaparecimento": value[4],
            "parentesco": value[5],
            "mensagem_de_aviso": value[6],
            "mensagem_para_desaparecido": value[7],
            "ativo": value[8],
            "endereco": value[9],
            "encoding": value[10],
            "user": {
                "id": value[11],
                "email": value[12],
                "telefone": value[13],
                "nome": value[14],
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

@app.route('/api/people/missed', methods=['GET'])
def get_all_missed_person():
    query = """
        select pd.id, pd.nome, pd.nascimento, pd.idade, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.ativo, pd.endereco, pd.encoding, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida as pd 
        INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id
    """
    cur.execute(query)
    result = cur.fetchall()
    return jsonify(buildInformationMissedPerson(result))

@app.route('/api/people/missed/<id>', methods=['GET'])
def get_one_missed_person(id):
    query = """
        select pd.id, pd.nome, pd.nascimento, pd.idade, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.ativo, pd.endereco, pd.encoding, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida as pd 
        INNER JOIN missing_finder.usuario u on pd.usuario_id = u.id
        WHERE pd.id = %s
    """
    cur.execute(query, (id))
    result = cur.fetchall()
    return jsonify(buildInformationMissedPerson(result)[0])

@app.route('/api/people/missed', methods=['POST'])
def create_one_missed_person():
    body = request.get_json(force=True)

    source_file_path = body['input_path']

    faceBundle = train(source_file_path)

    id = insert_missed_person(body, faceBundle)

    target_file_path = '{}/{}/reference.jpg'.format('missed', id)
    s3_util.move_file(source_file_path, target_file_path)

    if id:
        return success_handle(json.dumps({
            'id': id,
            'message': 'Pessoa desaparecida cadastrada com sucesso.'
        }))
    else:
        return error_handle("Não foi possível cadastrar a pessoa desaparecida.")

def insert_missed_person(body, faceBundle):
    query = "INSERT INTO missing_finder.pessoa_desaparecida (nome, nascimento, idade, data_desaparecimento, parentesco, mensagem_de_aviso, mensagem_para_desaparecido, usuario_id, endereco, ativo, encoding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true, %s::json) RETURNING id"

    data = (body['nome'], body['nascimento'], relativedelta(datetime.today(), datetime.strptime(body['nascimento'], '%Y-%m-%d')).years, body['data_desaparecimento'], body['parentesco'], body['mensagem_de_aviso'], body['mensagem_para_desaparecido'], body['usuario_id'], json.dumps(body['endereco']), json.dumps(faceBundle.getEncodings().tolist()))

    cur.execute(query, data)
    id = cur.fetchone()[0]
    conn.commit()

    return id

@app.route('/api/people/missed/<id>', methods=['PATCH'])
def deactivate_missed_person(id):
    body = request.get_json(force=True)

    query = "UPDATE missing_finder.pessoa_desaparecida SET ativo = %s WHERE id = %s"

    data = (body['ativo'], id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Status de ativação da pessoa desaparecida atualizado com sucesso.'
        }))

@app.route('/api/people/found', methods=['GET'])
def get_all_found_person():
    query = """
        select id, nome, idade, ativo, tip, encoding FROM missing_finder.pessoa_achada
    """
    cur.execute(query)
    result = cur.fetchall()
    return jsonify(buildInformationFoundPerson(result))

@app.route('/api/people/found/<id>', methods=['GET'])
def get_one_found_person(id):
    query = """
        select id, nome, idade, ativo, tip, encoding FROM missing_finder.pessoa_achada WHERE id = %s
    """
    cur.execute(query, (id))
    result = cur.fetchall()
    return jsonify(buildInformationFoundPerson(result)[0])

@app.route('/api/people/found/<id>', methods=['PATCH'])
def add_tip_of_found_person(id):
    body = request.get_json(force=True)

    query = "UPDATE missing_finder.pessoa_achada set tip = tip || %s::json where id = %s"

    data = (json.dumps(body['tip']), id)

    item = cur.execute(query, data)
    conn.commit()
 
    if item == None:
        return success_handle(json.dumps({
            'message': 'Pessoa achada atualizada com sucesso.'
        }))

@app.route('/api/people/found/<id>', methods=['PATCH'])
def deactivate_found_person(id):
    body = request.get_json(force=True)

    query = "UPDATE missing_finder.pessoa_achada SET ativo = %s WHERE id = %s"

    data = (body['ativo'], id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Status de ativação da pessoa achada atualizado com sucesso.'
        }))

@app.route('/api/people/found', methods=['POST'])
def create_one_found_person():
    body = request.get_json(force=True)

    source_file_path = body['input_path']

    faceBundle = train(source_file_path)

    id = insert_found_person(body, faceBundle)

    target_file_path = '{}/{}/reference.jpg'.format('found', id)
    s3_util.move_file(source_file_path, target_file_path)

    if id:
        return success_handle(json.dumps({
            'id': id,
            'message': 'Pessoa achada cadastrada com sucesso.'
        }))
    else:
        return error_handle("Não foi possível cadastrar a pessoa achada.")

def insert_found_person(body, faceBundle):
    query = "INSERT INTO missing_finder.pessoa_achada (nome, idade, tip, ativo, encoding) VALUES (%s, %s, array[%s::json], true, %s::json) RETURNING id"

    data = (body['nome'], body['idade'], json.dumps(body['tip']), json.dumps(faceBundle.getEncodings().tolist()))

    cur.execute(query, data)
    id = cur.fetchone()[0]
    conn.commit()

    return id

#
#    <----    USER ENDPOINTS   ---->
#

# route to create application user
@app.route('/api/users', methods=['POST'])
def user_create():
    body = request.get_json(force=True)

    body['senha'] = generate_password_hash(body['senha'], method='sha256')

    query = "INSERT INTO missing_finder.usuario (nome_usuario, email, senha, telefone, nome_completo) VALUES (%s, %s, %s, %s, %s)"

    data = (body['nome_usuario'], body['email'], body['senha'], body['telefone'], body['nome_completo'])

    # still under testing
    # data.senha = generate_password_hash(data.senha, method='sha256')

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Usuário cadastrado com sucesso'
        }))

# route to select user by id
@app.route('/api/users/<id>', methods=['GET'])
def one_user_id(id):
    query = """
        select u.id, u.nome_usuario, u.email, u.senha, u.telefone, u.nome_completo
        FROM missing_finder.usuario u
        WHERE id = %s;
    """
    cur.execute(query, (id,))
    result = cur.fetchall()
    
    return jsonify(buildUser(result))

# route to update user fullname
@app.route('/api/users/<int:id>/<nome_completo>', methods=['PATCH'])
def change_fullname_user(id, nome_completo):
    query = "UPDATE missing_finder.usuario set nome_completo = %s where id = %s"

    item = cur.execute(query, (nome_completo, id,))
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Nome completo do usuário atualizado com sucesso'
        }))

# route to update user email
@app.route('/api/users/<int:id>/<email>', methods=['PATCH'])
def change_email_user(id, email):
    query = "UPDATE missing_finder.usuario set email = %s where id = %s"

    item = cur.execute(query, (email, id,))
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Email do usuário atualizado com sucesso'
        }))

# route to update user phone
@app.route('/api/users/<int:id>/<int:telefone>', methods=['PATCH'])
def change_phone_user(id, telefone):
    query = "UPDATE missing_finder.usuario set telefone = %s where id = %s"

    item = cur.execute(query, (telefone, id,))
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Telefone do usuário atualizado com sucesso'
        }))

# route to update user phone
@app.route('/api/users/<int:id>/<senha>', methods=['PATCH'])
def change_password_user(id, senha):
    query = "UPDATE missing_finder.usuario set senha = %s where id = %s"

    item = cur.execute(query, (senha, id,))
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Senha do usuário atualizado com sucesso'
        }))

# route to authentication login
@app.route('/api/auth', methods=['GET'])
def login(nome_usuario):
    query = """
        select u.id, u.nome_usuario, u.email, u.senha, u.telefone, u.nome_completo
        FROM missing_finder.usuario u
        WHERE nome_usuario = '%s';
    """
    cur.execute(query, (nome_usuario,))
    result = cur.fetchall()

    return jsonify(buildUser(result))

# route to update user info
@app.route('/api/users/<int:id>', methods=['PUT'])
def user_update(id):
    body = request.get_json(force=True)

    body['senha'] = generate_password_hash(body['senha'], method='sha256')

    query = """
        UPDATE missing_finder.usuario set email = %s and senha = %s and telefone = %s and nome_completo = %s
        where id = %s
    """

    data = (body['email'], body['senha'], body['telefone'], body['nome_completo'])

    item = cur.execute(query, (data, id,))
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Usuário atualizado com sucesso'
        }))


# Mount the info returned from users table
def buildUser(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome_usuario": value[1],
            "email": value[2],
            "senha": value[3],
            "telefone": value[4],
            "nome_completo": value[5]
        }
        result.append(buildData)
    return result


#
#   <----      FACE RECOGNITION ENDPOINTS     ---->
#

# route to train a face
def train(image_path) -> FaceBundle:
    if not image_path:
        print("O caminho da imagem do rosto no S3 é obrigatório.")
        return error_handle("O caminho da imagem do rosto no S3 é obrigatório.")
    else:
        return app.face.add_known_face(image_path)

# route for recognize a unknown face
@app.route('/api/face-recognition', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return error_handle("Imagem obrigatória.")
    else:
        file = request.files['file']
        id = request.form['id']

        if 'tolerance' in request.form:
            tolerance = float(request.form['tolerance'])
        else:
            tolerance = 0.6
        if file.mimetype not in app.config['FILE_ALLOWED']:
            return error_handle("Extensão de arquivo não permitida.")
        else:
            filename = secure_filename(file.filename)
            file_path = path.join('unknown/', id + "_" + filename)
            file_content = file.read()

            s3_util.upload_file(file_content=file_content, object_name=file_path)

            name_list = app.face.find_matches(file_path, tolerance, id=id)
            if len(name_list):
                return_output = json.dumps(
                    {
                        "input_path": file_path,
                        "name": name_list
                    }, indent=2, sort_keys=True)
            else:
                return error_handle("Face da imagem não reconhecida.")
        return success_handle(return_output)

# Run the app
app.run(host=app.config['FLASK_RUN_HOST'], port=app.config['FLASK_RUN_PORT'])