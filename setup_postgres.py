import psycopg2


def create_tables():
    """ create tables in the 
     database"""
    commands = (
        """
        CREATE SCHEMA missing_finder AUTHORIZATION postgres;
        """,
        """
        CREATE TABLE missing_finder.usuario (
            id serial PRIMARY KEY,
            nome_usuario VARCHAR NULL,
            email VARCHAR NULL,
            senha VARCHAR NULL,
            telefone VARCHAR NULL,
            nome_completo VARCHAR NULL,
            data_criacao TIMESTAMP,
            data_atualizacao TIMESTAMP
        );
        """,
        """
        CREATE TABLE missing_finder.pessoa_desaparecida (
            id serial PRIMARY KEY,
            nome VARCHAR NULL,
            usuario_id INTEGER NOT NULL REFERENCES missing_finder.usuario(id),
            nascimento DATE NULL,
            idade INTEGER NULL,
            data_desaparecimento DATE NULL,
            parentesco VARCHAR NULL,
            mensagem_de_aviso VARCHAR NULL,
            mensagem_para_desaparecido VARCHAR NULL,
            ativo BOOLEAN NULL,
            endereco JSON NULL,
            encoding JSON NULL,
            data_criacao TIMESTAMP,
            data_desativacao TIMESTAMP NULL
        );
        """,
        """
        CREATE TABLE missing_finder.pessoa_achada (
            id serial PRIMARY KEY,
            nome VARCHAR NULL,
            idade INTEGER NULL,
            ativo BOOLEAN NULL,
            tip JSON[] NULL,
            encoding JSON NULL,
            data_criacao TIMESTAMP,
            data_desativacao TIMESTAMP NULL
        );
        """,
        )
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'postgres',
            user = 'postgres',
            password = 'mysecretpassword'
        )
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()