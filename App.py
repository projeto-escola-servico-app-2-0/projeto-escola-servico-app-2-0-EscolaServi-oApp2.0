from flask import Flask
from flask import request
from flask import jsonify
from flask_json_schema import JsonSchema, JsonValidationError
import logging
import sqlite3

app = Flask(__name__)


from Entidades.Aluno import Aluno
from Entidades.Escola import Escola
from Entidades.Campus import Campus
from Entidades.Curso import Curso
from Entidades.Disciplina import Disciplina
from Entidades.Endereco import Endereco
from Entidades.Turma import Turma
from Entidades.Turno import Turno
from Entidades.Professor import Professor

# Logging
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("escolaapp.log")
handler.setFormatter(formatter)
logger = app.logger
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# validação
schema = JsonSchema()
schema.init_app(app)

aluno_schema = {
    'required': ['nome', 'matricula', 'cpf', 'nascimento','id_endereco','id_curso' ],
    'properties': {
        'nome': {'type': 'string'},
        'matricula': {'type': 'string'},
        'cpf': {'type': 'string'},
        'nascimento': {'type': 'string'},
        'id_endereco': {'type': 'string'},
        'id_curso': {'type': 'string'}

    }
}

endereco_schema = {
    'required': ['logradouro', 'complemento', 'bairro', 'cep','numero'],
    'properties': {
        'logradouro': {'type': 'string'},
        'complemento': {'type': 'string'},
        'bairro': {'type': 'string'},
        'cep': {'type': 'string'},
        'numero': {'type': 'string'}
    }
}

escola_schema = {
    'required': ['nome','id_endereco','id_campus'],
    'properties': {
        'nome': {'type': 'string'},
        'id_endereco': {'type': 'string'},
        'id_campus': {'type': 'string'}
    }
}

professor_schema = {
    'required': ['nome','id_endereco'],
    'properties': {
        'nome': {'type': 'string'},
        'id_endereco': {'type': 'string'}
    }
}

turma_schema = {
    'required': ['nome','id_curso'],
    'properties': {
        'nome': {'type': 'string'},
        'id_curso': {'type': 'string'}
    }
}

curso_schema = {
    'required': ['nome','id_turno'],
    'properties': {
        'nome': {'type': 'string'},
        'id_turno': {'type': 'string'}
    }
}

turno_schema = {
    'required': ['nome','id_professor'],
    'properties': {
        'nome': {'type': 'string'},
        'id_professor': {'type': 'string'}
    }
}

campus_schema = {
    'required': ['sigla', 'cidade'],
    'properties': {
        'sigla': {'type': 'string'},
        'cidade': {'type': 'string'}
    }
}

disciplina_schema = {
    'required': ['nome','id_professor'],
    'properties': {
        'nome': {'type': 'string'},
        'id_professor': {'type': 'string'}
    }
}

DATABASE_NAME = "EscolaApp_versao2.db"

@app.route("/alunos", methods = ["GET"])
def getAlunos():
    logger.info("Listando alunos.")

    try:
        alunos = []
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_aluno;
        """)

        for linha in cursor.fetchall():
            aluno = {
                "id" : linha[0],
                "nome" : linha[1],
                "matricula" : linha[2],
                "cpf" : linha[3],
                "nascimento" : linha[4],
                "fk_id_endereco" : linha[5],
                "fk_id_curso" : linha[6]
            }
            alunos.append(aluno)
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro")
    logger.info("Alunos listado com sucesso.")
    return jsonify(alunos)


@app.route("/alunos/<int:id>", methods = ["GET"])
def getAlunosId(id):
    logger.info("Listando aluno.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_aluno where id_aluno = ?;
        """, (id, ))

        linha = cursor.fetchone()
        aluno = {
            "id" : linha[0],
            "nome" : linha[1],
            "matricula" : linha[2],
            "cpf" : linha[3],
            "nascimento" : linha[4],
            "fk_id_endereco" : linha[4],
            "fk_id_curso" : linha[5]
        }

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Aluno listado com sucesso.")
    return jsonify(aluno)


@app.route("/aluno", methods = ["POST"])
@schema.validate(aluno_schema)
def setAluno():
    logger.info("Cadastrando aluno...")
    aluno = request.get_json()
    nome = aluno["nome"]
    matricula = aluno["matricula"]
    cpf = aluno["cpf"]
    nascimento = aluno["nascimento"]
    id_endereco = aluno["id_endereco"]
    id_curso = aluno["id_curso"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tb_aluno(nome, matricula, cpf, nascimento, fk_id_endereco, fk_id_curso)
            values(?,?,?,?,?,?);
        """, (nome, matricula, cpf, nascimento, id_endereco, id_curso))

        conn.commit()
        conn.close()
        id = cursor.lastrowid
        aluno["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Aluno Cadastrado com sucesso.")
    return jsonify(aluno)

@app.route("/aluno/<int:id>", methods=['PUT'])
@schema.validate(aluno_schema)
def updateAluno(id):

    aluno = request.get_json()
    nome = aluno["nome"]
    matricula = aluno["matricula"]
    cpf = aluno["cpf"]
    nascimento = aluno["nascimento"]
    fk_id_endereco = aluno["fk_id_endereco"]
    fk_id_curso = aluno["fk_id_curso"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_aluno WHERE id_aluno = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_aluno
                SET nome=?, matricula=?, cpf=?, nascimento=?, fk_id_endereco=?, fk_id_curso=?
                WHERE id_aluno = ?;
            """, (nome, matricula, cpf, nascimento, fk_id_endereco, fk_id_curso, id))
            conn.commit()
        else:
            logger.info("Inserindo")

            cursor.execute("""
                INSERT INTO tb_aluno(nome, matricula, cpf, nascimento, fk_id_endereco, fk_id_curso)
                VALUES(?, ?, ?, ?, ?, ?);
            """, (nome, matricula, cpf, nascimento, fk_id_endereco, fk_id_curso))
            conn.commit()

            id = cursor.lastrowid
            aluno["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(aluno)

@app.route("/professores",  methods = ["GET"])
def getProfessores():
    logger.info("Listando professores.")
    professores = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_professor;
        """)

        for linha in cursor.fetchall():
            professor = {
                "id" : linha[0],
                "nome" : linha[1],
                "fk_id_endereco" : linha[2]
            }
            professores.append(professor)
        conn.close()
    except(sqlite3.Error):
         logger.error("Aconteceu um erro.")
    logger.info("Professores listados com sucesso.")
    return jsonify(professores)


@app.route("/professores/<int:id>", methods = ["GET"])
def getProfessoresId(id):
    logger.info("Listando professor.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_professor where id_professor = ?;
        """, (id, ))

        linha = cursor.fetchone()
        professor = {
            "id" : linha[0],
            "nome" : linha[1],
            "fk_id_endereco" : linha[2]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Professor listado com sucesso.")
    return jsonify(professor)


@app.route("/professor", methods = ["POST"])
@schema.validate(professor_schema)
def setProfessor():
    logger.info("Cadastrando professor.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        professor = request.get_json()
        nome = professor["nome"]
        id_endereco = professor["id_endereco"]

        cursor.execute("""
            insert into tb_professor(nome, fk_id_endereco)
            values(?,?);
        """, (nome,id_endereco))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        professor["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    return jsonify(professor)
    logger.info("Professor cadastrado com sucesso.")

@app.route("/professor/<int:id>", methods=['PUT'])
@schema.validate(professor_schema)
def updateProfessor(id):

    professor = request.get_json()
    nome = professor["nome"]
    fk_id_endereco = professor["fk_id_endereco"]
    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_professor WHERE id_professor = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_professor
                SET nome=?, fk_id_endereco=?
                WHERE id_professor = ?;
            """, (nome, fk_id_endereco, id))
            conn.commit()
        else:
            logger.info("Inserindo.")

            cursor.execute("""
                INSERT INTO tb_endereco(nome, fk_id_endereco)
                VALUES(?, ?);
            """, (nome, fk_id_endereco))
            conn.commit()

            id = cursor.lastrowid
            professor["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(professor)

@app.route("/turnos",  methods = ["GET"])
def getTurnos():
    logger.info("Listando turnos.")
    turnos = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_turno;
        """)

        for linha in cursor.fetchall():
            turno = {
                "id" : linha[0],
                "nome" : linha[1]
            }
            turnos.append(turno)
        conn.close()
    except(sqlite3.Error):
         logger.error("Aconteceu um erro.")
    logger.info("Turnos listados com sucesso.")
    return jsonify(turnos)


@app.route("/turnos/<int:id>", methods = ["GET"])
def getTurnoID(id):
    logger.info("Listando turno.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_turno where id_turno = ?;
        """, (id, ))

        linha = cursor.fetchone()
        turno = {
            "id" : linha[0],
            "nome" : linha[1]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Turno listado com sucesso.")
    return jsonify(turno)


@app.route("/turno", methods = ["POST"])
@schema.validate(turno_schema)
def setTurno():
    logger.info("Cadastrando turno.")
    turno = request.get_json()
    nome = turno["nome"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            insert into tb_turno(nome)
            values(?);
        """, (nome, ))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        turno["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Turno cadastrado com sucesso.")
    return jsonify(turno)

@app.route("/turno/<int:id>", methods=['PUT'])
@schema.validate(turno_schema)
def updateTurno(id):

    turno = request.get_json()
    nome = turno["nome"]
    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_turno WHERE id_turno = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_turno
                SET nome=?
                WHERE id_turno = ?;
            """, (nome, id))
            conn.commit()
        else:
            logger.info("Inserindo.")

            cursor.execute("""
                INSERT INTO tb_turno(nome)
                VALUES(?);
            """, (nome, ))
            conn.commit()

            id = cursor.lastrowid
            turno["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(turno)

@app.route("/enderecos",  methods = ["GET"])
def getEnderecos():
    logger.info("Listando endereços.")
    enderecos = []

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_endereco;
        """)

        for linha in cursor.fetchall():
            endereco = {
                "id" : linha[0],
                "logradouro" : linha[1],
                "complemento" : linha[2],
                "bairro" : linha[3],
                "cep" : linha[4],
                "numero" : linha[5]
            }
            enderecos.append(endereco)
        conn.close()
    except(sqlite3.Error):
         logger.error("Aconteceu um erro.")
    logger.info("Endereços listados com sucesso.")
    return jsonify(enderecos)


@app.route("/enderecos/<int:id>", methods = ["GET"])
def getEnderecoId(id):
    logger.info("Listando endereço.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_endereco where idtb_endereco = ?;
        """, (id, ))

        linha = cursor.fetchone()
        endereco = {
            "id" : linha[0],
            "logradouro" : linha[1],
            "complemento" : linha[2],
            "bairro" : linha[3],
            "cep" : linha[4],
            "numero" : linha[5]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Endereço listado com sucesso.")
    return jsonify(endereco)


@app.route("/endereco", methods = ["POST"])
@schema.validate(endereco_schema)
def setEndereco():
    logger.info("Cadastrando endereco.")
    endereco = request.get_json()
    logradouro = endereco["logradouro"]
    complemento = endereco["complemento"]
    bairro = endereco["bairro"]
    cep = endereco["cep"]
    numero = endereco["numero"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            insert into tb_endereco(logradouro, complemento, bairro, cep, numero)
            values(?,?,?,?,?);
        """, (logradouro, complemento, bairro, cep, numero))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        endereco["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Endereço cadastrado com sucesso.")
    return jsonify(endereco)


@app.route("/endereco/<int:id>", methods=['PUT'])
@schema.validate(endereco_schema)
def updateEndereco(id):

    endereco = request.get_json()
    logradouro = endereco["logradouro"]
    complemento = endereco["complemento"]
    bairro = endereco["bairro"]
    cep = endereco["cep"]
    numero = endereco["numero"]
    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_endereco WHERE idtb_endereco = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_endereco
                SET logradouro=?, complemento=?, bairro=?, cep=?, numero=?
                WHERE idtb_endereco = ?;
            """, (logradouro, complemento, bairro, cep, numero, id))
            conn.commit()
        else:
            logger.info("Inserindo.")

            cursor.execute("""
                INSERT INTO tb_endereco(logradouro, complemento, bairro, cep, numero)
                VALUES(?, ?, ?, ?, ?);
            """, (logradouro, complemento, bairro, cep, numero))
            conn.commit()

            id = cursor.lastrowid
            endereco["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(endereco)

@app.route("/campi", methods = ["GET"])
def getCampi():
    logger.info("Listando campus")
    campi = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_campus;
        """)
        for linha in cursor.fetchall():
            campus = {
                "id" : linha[0],
                "sigla" : linha[1],
                "cidade" : linha[2]
            }
            campi.append(campus)
        conn.close()
    except(sqlite3.Error):
         logger.error("Aconteceu um erro.")
    logger.info("Campus listados com sucesso.")
    return jsonify(campi)

@app.route("/campi/<int:id>", methods = ["GET"])
def getCampiId(id):
    logger.info("Listando campus")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_campus where id_campus = ?;
        """, (id, ))

        linha = cursor.fetchone()
        campi = {
            "id" : linha[0],
            "sigla" : linha[1],
            "cidade" : linha[2]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Campus listado com sucesso.")
    return jsonify(campi)


@app.route("/campus", methods = ["POST"])
@schema.validate(campus_schema)
def setCampus():
    logger.info("Cadastrando campus.")
    campus = request.get_json()
    sigla = campus["sigla"]
    cidade = campus["cidade"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            insert into tb_campus(sigla, cidade)
            values(?,?);
        """, (sigla, cidade))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        campus["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("campus cadastrado com sucesso.")
    return jsonify(campus)


@app.route("/Campus/<int:id>", methods=['PUT'])
@schema.validate(campus_schema)
def updateCampus(id):

    campus = request.get_json()
    sigla = campus["sigla"]
    cidade = campus["cidade"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_campus WHERE id_campus = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_campus
                SET sigla=?, cidade=?
                WHERE id_campus = ?;
            """, (sigla, cidade, id))
            conn.commit()
        else:
            logger.info("Inserindo.")
            cursor.execute("""
                INSERT INTO tb_campus(sigla, cidade)
                VALUES(?, ?);
            """, (sigla, cidade))
            conn.commit()

            id = cursor.lastrowid
            campus["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(Campus)

@app.route("/escolas", methods = ["GET"])
def getEscolas():
    logger.info("Listando escolas.")
    escolas = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_escola;
        """)

        for linha in cursor.fetchall():
            escola = {
                "id" : linha[0],
                "nome" : linha[1],
                "fk_id_endereco" : linha[2],
                "fk_id_campus" : linha[3]
            }
            escolas.append(escola)
        conn.close()
    except(sqlite3.Error):
         logger.error("Aconteceu um erro.")
    return jsonify(escolas)
    logger.info("Escolas listada com sucesso.")

@app.route("/escolas/<int:id>", methods = ["GET"])
def getEscolasId(id):
    logger.info("Listando escola.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_escola where id_escola = ?;
        """, (id, ))

        linha = cursor.fetchone()
        escola = {
            "id" : linha[0],
            "nome" : linha[1],
            "fk_id_endereco" : linha[2],
            "fk_id_campus" : linha[3]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Escola listada com sucesso.")
    return jsonify(escola)


@app.route("/escola", methods = ["POST"])
@schema.validate(escola_schema)
def setEscola():
    logger.info("Cadastrando escola.")
    escola = request.get_json()
    nome = escola["nome"]
    id_endereco = escola["id_endereco"]
    id_campus = escola["id_campus"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            insert into tb_escola(nome, fk_id_endereco, fk_id_campus)
            values(?,?,?);
        """, (nome, id_endereco, id_campus))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        escola["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Escola cadastrada com sucesso.")
    return jsonify(escola)


@app.route("/escola/<int:id>", methods=['PUT'])
@schema.validate(escola_schema)
def updateEscola(id):

    escola = request.get_json()
    nome = escola["nome"]
    fk_id_endereco = escola["fk_id_endereco"]
    fk_id_campus = escola["fk_id_campus"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_escola WHERE id_escola = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_escola
                SET nome=?, fk_id_endereco=?, fk_id_campus=?
                WHERE id_escola = ?;
            """, (nome, fk_id_endereco, fk_id_campus, id))
            conn.commit()
        else:
            logger.info("Inserindo.")

            cursor.execute("""
                INSERT INTO tb_escola(nome, fk_id_endereco, fk_id_campus)
                VALUES(?, ?, ?);
            """, (nome, fk_id_endereco, fk_id_campus))
            conn.commit()

            id = cursor.lastrowid
            escola["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(escola)

@app.route("/cursos", methods = ["GET"])
def getCursos():
    logger.info("Listando cursos.")
    cursos = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_curso;
        """)

        for linha in cursor.fetchall():
            curso = {
                "id" : linha[0],
                "nome" : linha[1],
                "fk_id_turno" : linha[2]
            }
            cursos.append(curso)
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Cursos listados com sucesso.")
    return jsonify(cursos)


@app.route("/cursos/<int:id>", methods = ["GET"])
def getCursosId(id):
    logger.info("Listando curso.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_curso where id_curso = ?;
        """, (id, ))
        linha = cursor.fetchone()
        curso = {
            "id" : linha[0],
            "nome" : linha[1],
            "fk_id_turno" : linha[2]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Curso listado com sucesso.")
    return jsonify(curso)


@app.route("/curso", methods = ["POST"])
@schema.validate(curso_schema)
def setCurso():
    logger.info("Cadastrando curso.")
    curso = request.get_json()
    nome = curso["nome"]
    id_turno = curso["id_turno"]
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            insert into tb_curso(nome, fk_id_turno)
            values(?,?);
        """, (nome, id_turno))
        conn.commit()
        conn.close()
        id = cursor.lastrowid
        curso["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Curso cadastrado com sucesso.")
    return jsonify(curso)


@app.route("/curso/<int:id>", methods=['PUT'])
@schema.validate(curso_schema)
def updateCurso(id):

    curso = request.get_json()
    nome = curso["nome"]
    fk_id_turno = curso["fk_id_turno"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_curso WHERE id_curso = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_curso
                SET nome=?, fk_id_turno=?
                WHERE id_curso = ?;
            """, (nome,fk_id_turno, id))
            conn.commit()
        else:
            logger.info("Inserindo")

            cursor.execute("""
                INSERT INTO tb_curso(nome, fk_id_turno)
                VALUES(?, ?);
            """, (nome, fk_id_turno))
            conn.commit()

            id = cursor.lastrowid
            curso["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(curso)

@app.route("/turmas", methods = ["GET"])
def getTurmas():
    logger.info("Listando turmas.")
    turmas = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_turma;
        """)

        for linha in cursor.fetchall():
            turma = {
                "id" : linha[0],
                "nome" : linha[1],
                "fk_id_curso" : linha[2]
            }
            turmas.append(turma)
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Turmas listadas com sucesso.")
    return jsonify(turmas)


@app.route("/turmas/<int:id>", methods = ["GET"])
def getTurmasId(id):
    logger.info("Listando turma.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_turma where id_turma = ?;
        """, (id, ))
        linha = cursor.fetchone()
        turma = {
            "id" : linha[0],
            "nome" : linha[1],
            "fk_id_curso" : linha[2]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Turma listada com sucesso.")
    return jsonify(turma)


@app.route("/turma", methods = ["POST"])
@schema.validate(turma_schema)
def setTurma():
    logger.info("Cadastrando turma.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        turma = request.get_json()
        nome = turma["nome"]
        id_curso = turma["id_curso"]
        cursor = conn.cursor()
        cursor.execute("""
            insert into tb_turma(nome, fk_id_curso)
            values(?,?);
        """, (nome, id_curso))
        conn.commit()
        conn.close()

        id = cursor.lastrowid
        turma["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Turma cadastrada com sucesso.")
    return jsonify(turma)


@app.route("/turma/<int:id>", methods=['PUT'])
@schema.validate(turma_schema)
def updateTurma(id):

    turma = request.get_json()
    nome = turma["nome"]
    fk_id_curso = turma["fk_id_curso"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_turma WHERE id_turma = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:

            cursor.execute("""
                UPDATE tb_turma
                SET nome=?, fk_id_curso=?
                WHERE id_turma = ?;
            """, (nome, fk_id_curso, id))
            conn.commit()
        else:
            logger.info("Inserindo")

            cursor.execute("""
                INSERT INTO tb_turma(nome, fk_id_curso)
                VALUES(?, ?);
            """, (nome, fk_id_curso))
            conn.commit()

            id = cursor.lastrowid
            aluno["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(turma)

@app.route("/disciplinas", methods = ["GET"])
def getDisciplinas():
    logger.info("Listando disciplinas.")
    disciplinas = []
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_disciplina;
        """)

        for linha in cursor.fetchall():
            disciplina = {
                "id" : linha[0],
                "nome" : linha[1],
                "fk_id_professor" : linha[2]
            }
            disciplinas.append(disciplina)
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Disciplinas listadas com sucesso.")
    return jsonify(disciplinas)


@app.route("/disciplinas/<int:id>", methods = ["GET"])
def getDisciplinasId(id):
    logger.info("Listando disciplina.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            select * from tb_disciplina where id_disciplina = ?;
        """, (id, ))

        linha = cursor.fetchone()
        disciplina = {
            "id" : linha[0],
            "nome" : linha[1],
            "fk_id_professor" : linha[2]
        }
        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Disciplina listada com sucesso.")
    return jsonify(disciplina)


@app.route("/disciplina", methods = ["POST"])
@schema.validate(disciplina_schema)
def setDisciplina():
    logger.info("Cadastrando disciplina.")
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        disciplina = request.get_json()
        nome = disciplina["nome"]
        id_professor = disciplina["id_professor"]
        cursor.execute("""
            insert into tb_disciplina(nome, fk_id_professor)
            values(?,?);
        """, (nome, id_professor))
        conn.commit()
        conn.close()
        id = cursor.lastrowid
        disciplina["id"] = id
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")
    logger.info("Disciplina cadastrada com sucesso.")
    return jsonify(disciplina)


@app.route("/disciplina/<int:id>", methods=['PUT'])
@schema.validate(disciplina_schema)
def updateDisciplina(id):

    disciplina = request.get_json()
    nome = disciplina["nome"]
    fk_id_professor = disciplina["fk_id_professor"]

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tb_disciplina WHERE id_disciplina = ?;
        """, (id, ))

        data = cursor.fetchone()

        if data is not None:
            cursor.execute("""
                UPDATE tb_disciplina
                SET nome=?, fk_id_professor=?
                WHERE id_disciplina = ?;
            """, (nome, fk_id_professor, id))
            conn.commit()
        else:
            logger.info("Inserindo")
            cursor.execute("""
                INSERT INTO tb_disciplina(nome, fk_id_professor)
                VALUES(?, ?);
            """, (nome, fk_id_professor))
            conn.commit()

            id = cursor.lastrowid
            aluno["id"] = id

        conn.close()
    except(sqlite3.Error):
        logger.error("Aconteceu um erro.")

    return jsonify(disciplina)

def dict_factory(linha, cursor):
    dicionario = {}
    for idx, col in enumerate(cursor.description):
        dicionario[col[0]] = linha[idx]
    return dicionario

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error  in e.errors]})

if(__name__ == '__main__'):
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
