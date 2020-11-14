# coding=utf-8
from flask import Flask, json, Response, request, render_template, send_file, jsonify
from libs.FaceRecognition import FaceRecognition
from libs.models.FaceBundle import FaceBundle
from libs.S3Util import S3Util
from os import path, getcwd
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import simplejson as json
from datetime import datetime
import asyncio
from flask_login import login_user, LoginManager
import base64
import hashlib
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config.from_object('config.Config')
assets: str = app.config['ASSETS']

# Instantiate S3 util class
s3_util = S3Util('missing-finder-bucket')

# Create cursor to PostgreSQL DB
conn = psycopg2.connect(
    host = '127.0.0.1',
    database = 'postgres',
    user = 'postgres',
    password = 'mysecretpassword'
)
cur = conn.cursor()

# Instantiate FaceRecognition class
app.face = FaceRecognition(storageFolderPath='storage/',
                           knownFolderPath='known/',
                           unknownFolderPath='unknown/',
                           outputFolderPath='output/',
                           s3_util=s3_util,
                           cur=cur)

# Instantiate login class
login_manager = LoginManager()
login_manager.init_app(app)

def buildInformationFoundPerson(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "idade": value[2],
            "url_imagem": 'https://missing-finder-bucket.s3-sa-east-1.amazonaws.com/{}/{}/reference.jpg'.format('found', value[0]),
            "ativo": value[3],
            "encoding": value[4],
            "data_criacao": value[5],
            "data_desativacao": value[6],
            "tipo": 'ACHADA',
            "dica": {
                "id": value[7],
                "mensagem_de_aviso": value[8],
                "lat": json.dumps(json.Decimal(value[9])),
                "long": json.dumps(json.Decimal(value[10])),
                "endereco": value[11],
                "data_criacao": value[12],
                "data_atualizacao": value[13],
                "user": {
                    "id": value[14],
                    "email": value[15],
                    "telefone": value[16],
                    "nome": value[17]
                } 
            }  
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
            "url_imagem": 'https://missing-finder-bucket.s3-sa-east-1.amazonaws.com/{}/{}/reference.jpg'.format('missed', value[0]),
            "ativo": value[8],
            "endereco": value[9],
            "encoding": value[10],
            "tipo": 'DESAPARECIDA',
            "data_criacao": value[11],
            "data_desativacao": value[12],
            "user": {
                "id": value[13],
                "email": value[14],
                "telefone": value[15],
                "nome": value[16]
            } 
        }
        result.append(buildData)
    return result

def buildPersonInformation(values):
    result = []
    for value in values:
        buildData = {
            "id": value[0],
            "nome": value[1],
            "idade": value[2],
            "url_imagem": 'https://missing-finder-bucket.s3-sa-east-1.amazonaws.com/{}/{}/reference.jpg'.format('missed' if value[4] == 'DESAPARECIDA' else 'found', value[0]),
            "ativo": value[3],
            "tipo": value[4],
            "data_criacao": value[5],
            "data_desativacao": value[6]
        }
        result.append(buildData)
    return result

def success_handle(output=None, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)

def error_handle(error_message=None, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": error_message}), status=status, mimetype=mimetype)

# Route for homepage
@app.route('/', methods=['GET'])
def page_home():
    return render_template('index.html')

# Route for health check
@app.route('/api', methods=['GET'])
def homepage():
    output = json.dumps({"api": '1.0'})
    return success_handle(output)

#
#    <----    PEOPLE ENDPOINTS   ---->
#

# Route to get all people
@app.route('/api/people', methods=['GET'])
def get_all_people():
    active = request.args.get('active')
    user_id = request.args.get('userId')

    query = """
        SELECT pd.id, pd.nome, pd.idade, pd.ativo, 'DESAPARECIDA', pd.data_criacao, pd.data_desativacao
        FROM missing_finder.pessoa_desaparecida pd
        UNION
        SELECT pa.id, pa.nome, pa.idade, pa.ativo, 'ACHADA', pa.data_criacao, pa.data_desativacao
        FROM missing_finder.pessoa_achada pa;
    """
    
    cur.execute(query)

    result = cur.fetchall()
    return jsonify(buildPersonInformation(result))

# Route to get all missed people
@app.route('/api/people/missed', methods=['GET'])
def get_all_missed_person():
    active = request.args.get('active')
    user_id = request.args.get('userId')

    query = """
        SELECT pd.id, pd.nome, pd.nascimento, pd.idade, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.ativo, pd.endereco, pd.encoding, pd.data_criacao, pd.data_desativacao, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida pd 
        INNER JOIN missing_finder.usuario u ON pd.usuario_id = u.id
        WHERE 1 = 1
    """

    data = ()

    if active:
        query = query + " AND pd.ativo = %s"
        data = (data + (active,))

    if user_id:
        query = query + " AND u.id = %s"
        data = (data + (user_id,))

    query = query + ";"

    if data:
        cur.execute(query, data)
    else:
        cur.execute(query)

    result = cur.fetchall()
    return jsonify(buildInformationMissedPerson(result))

# Route to get one missed person
@app.route('/api/people/missed/<id>', methods=['GET'])
def get_one_missed_person(id):
    result = find_missed_person_by_id(id)
    return jsonify(buildInformationMissedPerson(result)[0])

def find_missed_person_by_id(id):
    query = """
        SELECT pd.id, pd.nome, pd.nascimento, pd.idade, pd.data_desaparecimento, pd.parentesco, pd.mensagem_de_aviso, pd.mensagem_para_desaparecido, pd.ativo, pd.endereco, pd.encoding, pd.data_criacao, pd.data_desativacao, u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_desaparecida pd 
        INNER JOIN missing_finder.usuario u ON pd.usuario_id = u.id
        WHERE pd.id = %s;
    """

    data = (id,)

    cur.execute(query, data)
    return cur.fetchall()

# Route to create one missed person
@app.route('/api/people/missed', methods=['POST'])
def create_one_missed_person():
    body = request.get_json(force=True)

    source_file_path = body['input_path']

    faceBundle = extract_face(source_file_path)

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
    query = """
        INSERT INTO missing_finder.pessoa_desaparecida (nome, nascimento, idade, data_desaparecimento, parentesco, mensagem_de_aviso, mensagem_para_desaparecido, usuario_id, endereco, ativo, encoding, data_criacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, True, %s::json, %s)
        RETURNING id;
    """

    data = (body['nome'], body['nascimento'], relativedelta(datetime.today(), datetime.strptime(body['nascimento'], '%Y-%m-%d')).years, body['data_desaparecimento'], body['parentesco'], body['mensagem_de_aviso'], body['mensagem_para_desaparecido'], body['usuario_id'], json.dumps(body['endereco']), json.dumps(faceBundle.getEncodings().tolist()), datetime.now())

    cur.execute(query, data)
    id = cur.fetchone()[0]
    conn.commit()

    return id

# Route to update one missed person activation status
@app.route('/api/people/missed/<id>/deactivate', methods=['PATCH'])
def deactivate_missed_person(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.pessoa_desaparecida
        SET ativo = %s, data_desativacao = %s
        WHERE id = %s;
    """

    data = (body['ativo'], datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Status de ativação da pessoa desaparecida atualizado com sucesso.'
        }))

# Route to get all found people
@app.route('/api/people/found', methods=['GET'])
def get_all_found_person():
    active = request.args.get('active')
    user_id = request.args.get('userId')

    query = """
        SELECT pa.id, pa.nome, pa.idade, pa.ativo, pa.encoding, pa.data_criacao, pa.data_desativacao, 
        d.id, d.mensagem_de_aviso, d.latitude, d.longitude, d.endereco, d.data_criacao, d.data_atualizacao,
        u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_achada pa
        INNER JOIN missing_finder.dica d ON pa.id = d.pessoa_achada_id
        INNER JOIN missing_finder.usuario u ON d.usuario_id = u.id
        WHERE 1 = 1
    """
    
    data = ()

    if active:
        query = query + " AND pa.ativo = %s"
        data = (data + (active,))

    if user_id:
        query = query + " AND u.id = %s"
        data = (data + (user_id,))

    query = query + ";"

    if data:
        cur.execute(query, data)
    else:
        cur.execute(query)
    
    result = cur.fetchall()
    return jsonify(buildInformationFoundPerson(result))

# Route to get one found person
@app.route('/api/people/found/<id>', methods=['GET'])
def get_one_found_person(id):
    result = find_found_person_by_id(id)
    return jsonify(buildInformationFoundPerson(result)[0])

def find_found_person_by_id(id):
    query = """
        SELECT pa.id, pa.nome, pa.idade, pa.ativo, pa.encoding, pa.data_criacao, pa.data_desativacao,
        d.id, d.mensagem_de_aviso, d.latitude, d.longitude, d.endereco, d.data_criacao, d.data_atualizacao,
        u.id, u.email, u.telefone, u.nome_completo
        FROM missing_finder.pessoa_achada pa
        INNER JOIN missing_finder.dica d ON pa.id = d.pessoa_achada_id
        INNER JOIN missing_finder.usuario u ON d.usuario_id = u.id
        WHERE pa.id = %s;
    """

    data = (id,)

    cur.execute(query, data)
    return cur.fetchall()

# Route to update one found person with a tip
@app.route('/api/people/found/<id>', methods=['PATCH'])
def add_tip_of_found_person(id):
    body = request.get_json(force=True)

    tipId = insert_tip(body, body['pessoa_achada_id'])

    if tipId:
        return success_handle(json.dumps({
            'message': 'Pessoa achada atualizada com sucesso.'
        }))

# Route to update one found person activation status
@app.route('/api/people/found/<id>/deactivate', methods=['PATCH'])
def deactivate_found_person(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.pessoa_achada
        SET ativo = %s, data_desativacao = %s
        WHERE id = %s;
    """

    data = (body['ativo'], datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Status de ativação da pessoa achada atualizado com sucesso.'
        }))

# Route to create one found person
@app.route('/api/people/found', methods=['POST'])
def create_one_found_person():
    body = request.get_json(force=True)

    source_file_path = body['input_path']

    faceBundle = extract_face(source_file_path)

    id = insert_found_person(body, faceBundle)

    if id:
        tipId = insert_tip(body['dica'], id)
        target_file_path = '{}/{}/reference.jpg'.format('found', id)
        s3_util.move_file(source_file_path, target_file_path)

        return success_handle(json.dumps({
            'id': id,
            'message': 'Pessoa achada cadastrada com sucesso.'
        }))
    else:
        return error_handle("Não foi possível cadastrar a pessoa achada.")

def insert_tip(tipBody, id):
    query = """
        INSERT INTO missing_finder.dica (pessoa_achada_id, mensagem_de_aviso, latitude, longitude, usuario_id, endereco, data_criacao, data_atualizacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """

    data = (id, tipBody['mensagem_de_aviso'], tipBody['lat'], tipBody['long'], tipBody['usuario_id'], json.dumps(tipBody['endereco']), datetime.now(), datetime.now())

    cur.execute(query, data)
    tip_id = cur.fetchone()[0]
    conn.commit()

    return tip_id

def insert_found_person(body, faceBundle):
    query = """
        INSERT INTO missing_finder.pessoa_achada (nome, idade, ativo, encoding, data_criacao)
        VALUES (%s, %s, True, %s::json, %s)
        RETURNING id;
    """

    data = (body['nome'], body['idade'], json.dumps(faceBundle.getEncodings().tolist()), datetime.now())

    cur.execute(query, data)
    id = cur.fetchone()[0]
    conn.commit()

    return id

#
#    <----    USERS ENDPOINTS   ---->
#

# Route to create one user
@app.route('/api/users', methods=['POST'])
def create_one_user():
    body = request.get_json(force=True)

    pass_hash = hashlib.sha256(body['senha'].encode())
    body['senha'] = pass_hash.hexdigest()

    query = """
        INSERT INTO missing_finder.usuario (nome_usuario, email, senha, telefone, nome_completo, data_criacao)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    data = (body['nome_usuario'], body['email'], body['senha'], body['telefone'], body['nome_completo'], datetime.now())
    print(data)
    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Usuário cadastrado com sucesso.'
        }))

# Route to get one user
@app.route('/api/users/<id>', methods=['GET'])
def get_one_user(id):
    result = find_user_by_id(id)
    return jsonify(buildUser(result))

def find_user_by_id(id):
    query = """
        SELECT u.id, u.nome_usuario, u.email, u.senha, u.telefone, u.nome_completo, u.data_criacao, u.data_atualizacao
        FROM missing_finder.usuario u
        WHERE u.id = %s;
    """

    data = (id,)

    cur.execute(query, data)
    return cur.fetchall()
    
# Route to update one user fullname
@app.route('/api/users/<int:id>/fullname', methods=['PATCH'])
def change_fullname_user(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.usuario
        SET nome_completo = %s, data_atualizacao = %s
        WHERE id = %s;
    """

    data = (body['nome_completo'], datetime.now(), id)
    
    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Nome completo do usuário atualizado com sucesso.'
        }))

# Route to update one user email
@app.route('/api/users/<int:id>/email', methods=['PATCH'])
def change_email_user(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.usuario
        SET email = %s, data_atualizacao = %s
        WHERE id = %s;
    """

    data = (body['email'], datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Email do usuário atualizado com sucesso.'
        }))

# Route to update one user phone
@app.route('/api/users/<int:id>/phone', methods=['PATCH'])
def change_phone_user(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.usuario
    SET telefone = %s, data_atualizacao = %s
        WHERE id = %s;
    """

    data = (body['telefone'], datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Telefone do usuário atualizado com sucesso.'
        }))

# Route to update one user password
@app.route('/api/users/<int:id>/password', methods=['PATCH'])
def change_user_password(id):
    body = request.get_json(force=True)

    if update_user_password(id, body['senha']) == None:
        return success_handle(json.dumps({
            'message': 'Senha do usuário atualizada com sucesso.'
        }))

def update_user_password(id, password):
    pass_hash = hashlib.sha256(password.encode())
    pass_digest = pass_hash.hexdigest()

    query = """
        UPDATE missing_finder.usuario
        SET senha = %s, data_atualizacao = %s
        WHERE id = %s;
    """

    data = (pass_digest, datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    return item

# Route to authenticate a user
@app.route('/api/auth', methods=['GET'])
@login_manager.request_loader
def login():
    api_key = request.headers.get('Authorization')
    
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)

            header_split = api_key.split(b':')
            username = header_split[0].decode("utf-8")
            password = header_split[1].decode("utf-8")

            pass_hash = hashlib.sha256(password.encode())
            password = pass_hash.hexdigest()

            query = """
                SELECT u.id, u.senha
                FROM missing_finder.usuario u
                WHERE u.nome_usuario = %s;
            """

            data = (username,)

            cur.execute(query, data)
            result = cur.fetchall()

            if password == result[0][1]:
                return success_handle(json.dumps({
                    'id': result[0][0],
                    'message': 'Usuário logado com sucesso.'
                }))
            else:
                return error_handle("Senha incorreta.")
        except TypeError:
            pass
    
    return None

# Route to update one user informations
@app.route('/api/users/<int:id>', methods=['PUT'])
def user_update(id):
    body = request.get_json(force=True)

    query = """
        UPDATE missing_finder.usuario
        SET email = %s, senha = %s, telefone = %s, nome_completo = %s, data_atualizacao = %s
        WHERE id = %s;
    """

    data = (body['email'], hashlib.sha256(body['senha'].encode()).hexdigest(), body['telefone'], body['nome_completo'], datetime.now(), id)

    item = cur.execute(query, data)
    conn.commit()

    if item == None:
        return success_handle(json.dumps({
            'message': 'Usuário atualizado com sucesso.'
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
            "nome_completo": value[5],
            "data_criacao": value[6],
            "data_atualizacao": value[7]
        }
        result.append(buildData)
    return result


#
#   <----      FACE RECOGNITION ENDPOINTS     ---->
#

def extract_face(image_path) -> FaceBundle:
    if not image_path:
        print("O caminho da imagem do rosto no S3 é obrigatório.")
        return error_handle("O caminho da imagem do rosto no S3 é obrigatório.")
    else:
        return app.face.add_known_face(image_path)

# Route to recognize a unknown face
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

            result = app.face.find_matches(file_path, tolerance, id=id)
            if len(result):
                return_output = json.dumps(
                    {
                        "input_path": file_path,
                        "result": result
                    }, indent=2, sort_keys=True)
            else:
                return error_handle("Face da imagem não reconhecida.")
        return success_handle(return_output)

# Run the app
app.run(host=app.config['FLASK_RUN_HOST'], port=app.config['FLASK_RUN_PORT'])