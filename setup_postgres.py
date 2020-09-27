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
            nome_usuario varchar NULL,
            id serial PRIMARY KEY,
            email varchar NULL,
            senha varchar NULL,
            telefone int4 NULL,
            nome_completo varchar NULL
        );
        """,
        """
        CREATE TABLE missing_finder.pessoa_desaparecida (
            nome varchar NULL,
            id serial PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES missing_finder.usuario(id),
            nascimento date NULL,
            data_desaparecimento date NULL,
            parentesco varchar NULL,
            mensagem_de_aviso varchar NULL,
            mensagem_para_desaparecido varchar NULL,
            status_desaparecido bool NULL,
            endereco json NULL
        );
        """,
        """
        CREATE TABLE missing_finder.pistas_pessoa_desaparecida (
            nome varchar NULL,
            idade int4 NULL,
            descricao varchar NULL,
            endereco json NULL,
            id serial PRIMARY KEY,
            pessoa_desaparecida_id int NOT NULL REFERENCES missing_finder.pessoa_desaparecida(id)
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