import os

import psycopg

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    nome            VARCHAR(150) NOT NULL,
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS leads (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    whatsapp        VARCHAR(20) NOT NULL,
    empresa         VARCHAR(255) NOT NULL,
    cargo           VARCHAR(255) NOT NULL,
    colaboradores   VARCHAR(50) NOT NULL,
    cidade_uf       VARCHAR(255),
    status          VARCHAR(30) DEFAULT 'novo',
    source          VARCHAR(100) DEFAULT 'lp',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organizacoes (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(200) NOT NULL,
    cnpj            VARCHAR(18),
    segmento        VARCHAR(100),
    contato_nome    VARCHAR(150),
    contato_email   VARCHAR(255),
    contato_telefone VARCHAR(20),
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS colaboradores (
    id              SERIAL PRIMARY KEY,
    organizacao_id  INTEGER NOT NULL REFERENCES organizacoes(id) ON DELETE CASCADE,
    nome            VARCHAR(150) NOT NULL,
    email           VARCHAR(255),
    cargo           VARCHAR(100),
    departamento    VARCHAR(100),
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS palestras (
    id              SERIAL PRIMARY KEY,
    titulo          VARCHAR(255) NOT NULL,
    descricao       TEXT,
    data_realizacao DATE,
    local           VARCHAR(255),
    modalidade      VARCHAR(30) DEFAULT 'presencial',
    carga_horaria   INTEGER,
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS palestras_organizacoes (
    id              SERIAL PRIMARY KEY,
    palestra_id     INTEGER NOT NULL REFERENCES palestras(id) ON DELETE CASCADE,
    organizacao_id  INTEGER NOT NULL REFERENCES organizacoes(id) ON DELETE CASCADE,
    data_realizacao DATE,
    observacoes     TEXT,
    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (palestra_id, organizacao_id, data_realizacao)
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id                      SERIAL PRIMARY KEY,
    palestra_organizacao_id INTEGER NOT NULL REFERENCES palestras_organizacoes(id) ON DELETE CASCADE,
    colaborador_id          INTEGER REFERENCES colaboradores(id),
    nome_respondente        VARCHAR(150),
    email_respondente       VARCHAR(255),
    nota_geral              SMALLINT CHECK (nota_geral BETWEEN 1 AND 5),
    nota_conteudo           SMALLINT CHECK (nota_conteudo BETWEEN 1 AND 5),
    nota_aplicabilidade     SMALLINT CHECK (nota_aplicabilidade BETWEEN 1 AND 5),
    nota_facilitador        SMALLINT CHECK (nota_facilitador BETWEEN 1 AND 5),
    o_que_aprendeu          TEXT,
    o_que_vai_aplicar       TEXT,
    sugestoes               TEXT,
    criado_em               TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_colaboradores_org ON colaboradores(organizacao_id);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_palestra_org ON avaliacoes(palestra_organizacao_id);
"""


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return psycopg.connect(database_url, connect_timeout=5)


def init_db():
    try:
        conn = get_db_connection()
        if conn is None:
            return
        statements = [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]
        with conn:
            with conn.cursor() as cursor:
                for stmt in statements:
                    cursor.execute(stmt)
        conn.close()
    except Exception:
        pass


def query(sql, params=None, one=False):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                cols = [d[0] for d in cursor.description] if cursor.description else []
                if one:
                    row = cursor.fetchone()
                    return dict(zip(cols, row)) if row else None
                rows = cursor.fetchall()
                return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()


def execute(sql, params=None):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                if cursor.description:
                    return cursor.fetchall()
                return None
    finally:
        conn.close()
