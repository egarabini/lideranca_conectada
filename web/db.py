import os

import psycopg

# Configurar DATABASE_URL se não estiver definido
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://david:troque_por_senha_segura@127.0.0.1:5433/lideranca_test"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    nome            VARCHAR(150) NOT NULL,
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pessoas (
    id              SERIAL PRIMARY KEY,
    nome_completo   VARCHAR(255) NOT NULL,
    telefone        VARCHAR(20),
    ind_whatsapp    BOOLEAN DEFAULT TRUE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    nome_empresa    VARCHAR(255),
    cargo_funcao    VARCHAR(255),
    cidade_uf       VARCHAR(255),
    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    alterado_em     TIMESTAMPTZ DEFAULT NOW()
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
    organizacao_id  INTEGER REFERENCES organizacoes(id) ON DELETE SET NULL,
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

CREATE TABLE IF NOT EXISTS participantes (
    id              SERIAL PRIMARY KEY,
    palestra_id     INTEGER NOT NULL REFERENCES palestras(id) ON DELETE CASCADE,
    pessoa_id       INTEGER REFERENCES pessoas(id) ON DELETE CASCADE,
    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (palestra_id, pessoa_id)
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

CREATE TABLE IF NOT EXISTS investigacoes (
    id                      SERIAL PRIMARY KEY,
    palestra_organizacao_id INTEGER NOT NULL REFERENCES palestras_organizacoes(id) ON DELETE CASCADE,
    colaborador_id          INTEGER REFERENCES colaboradores(id),
    nome_respondente        VARCHAR(150),
    email_respondente       VARCHAR(255),
    cargo                   VARCHAR(100),
    departamento            VARCHAR(100),
    q1                      VARCHAR(255),
    q1_outro                TEXT,
    q2                      VARCHAR(255),
    q3                      SMALLINT CHECK (q3 BETWEEN 0 AND 10),
    q4                      VARCHAR(255),
    q5                      TEXT,
    q6                      TEXT,
    q7                      TEXT,
    q8                      TEXT,
    q8_outro                TEXT,
    q9                      VARCHAR(255),
    q10                     TEXT,
    criado_em               TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS formularios (
    id              SERIAL PRIMARY KEY,
    titulo          VARCHAR(255) NOT NULL,
    descricao       TEXT,
    texto_final     TEXT,
    tipo            VARCHAR(30) NOT NULL DEFAULT 'investigacao',
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS questoes (
    id              SERIAL PRIMARY KEY,
    formulario_id   INTEGER NOT NULL REFERENCES formularios(id) ON DELETE CASCADE,
    ordem           INTEGER NOT NULL DEFAULT 0,
    bloco           VARCHAR(150),
    pergunta        TEXT NOT NULL,
    tipo_resposta   VARCHAR(30) NOT NULL DEFAULT 'texto',
    obrigatoria     BOOLEAN DEFAULT TRUE,
    tem_outro       BOOLEAN DEFAULT FALSE,
    opcoes          TEXT,
    criado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS respostas_formulario (
    id                      SERIAL PRIMARY KEY,
    formulario_id           INTEGER NOT NULL REFERENCES formularios(id) ON DELETE CASCADE,
    questao_id              INTEGER NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
    palestra_organizacao_id INTEGER NOT NULL REFERENCES palestras_organizacoes(id) ON DELETE CASCADE,
    colaborador_id          INTEGER REFERENCES colaboradores(id),
    nome_respondente        VARCHAR(150),
    email_respondente       VARCHAR(255),
    cargo                   VARCHAR(100),
    departamento            VARCHAR(100),
    valor                   TEXT,
    criado_em               TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_colaboradores_org ON colaboradores(organizacao_id);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_palestra_org ON avaliacoes(palestra_organizacao_id);
CREATE INDEX IF NOT EXISTS idx_investigacoes_palestra_org ON investigacoes(palestra_organizacao_id);
CREATE INDEX IF NOT EXISTS idx_questoes_formulario ON questoes(formulario_id);
CREATE INDEX IF NOT EXISTS idx_respostas_formulario ON respostas_formulario(palestra_organizacao_id);
CREATE INDEX IF NOT EXISTS idx_participantes_palestra ON participantes(palestra_id);
CREATE INDEX IF NOT EXISTS idx_pessoas_email ON pessoas(email);
"""


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return psycopg.connect(database_url, connect_timeout=5)


MIGRATIONS = [
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS organisacao_id INTEGER REFERENCES organizacoes(id) ON DELETE SET NULL",
    "ALTER TABLE palestras ADD COLUMN IF NOT EXISTS formulario_investigacao_id INTEGER REFERENCES formularios(id) ON DELETE SET NULL",
    "ALTER TABLE palestras ADD COLUMN IF NOT EXISTS formulario_avaliacao_id INTEGER REFERENCES formularios(id) ON DELETE SET NULL",
    "ALTER TABLE formularios ADD COLUMN IF NOT EXISTS texto_final TEXT",
    "ALTER TABLE respostas_formulario ADD COLUMN IF NOT EXISTS participante_id INTEGER REFERENCES participantes(id) ON DELETE CASCADE",
    "ALTER TABLE respostas_formulario ALTER COLUMN formulario_id DROP NOT NULL",
    "ALTER TABLE respostas_formulario ALTER COLUMN palestra_organizacao_id DROP NOT NULL",
    # Tabela de logs para backup completo de respostas
    """DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'respostas_log') THEN
            CREATE TABLE respostas_log (
                id              SERIAL PRIMARY KEY,
                participante_id INTEGER REFERENCES participantes(id) ON DELETE CASCADE,
                json_completo   JSONB NOT NULL,
                criado_em       TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX idx_respostas_log_participante ON respostas_log(participante_id);
            CREATE INDEX idx_respostas_log_criado_em ON respostas_log(criado_em);
        END IF;
    END$$""",
    # Adicionar tabela pessoas e atualizar participantes
    """DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pessoas') THEN
            CREATE TABLE pessoas (
                id              SERIAL PRIMARY KEY,
                nome_completo   VARCHAR(255) NOT NULL,
                telefone        VARCHAR(20),
                ind_whatsapp    BOOLEAN DEFAULT TRUE,
                email           VARCHAR(255) UNIQUE NOT NULL,
                nome_empresa    VARCHAR(255),
                cargo_funcao    VARCHAR(255),
                cidade_uf       VARCHAR(255),
                criado_em       TIMESTAMPTZ DEFAULT NOW(),
                alterado_em     TIMESTAMPTZ DEFAULT NOW()
            );
        END IF;
    END $$;""",
    """DO $$
    DECLARE col_exists INTEGER;
    BEGIN
        SELECT COUNT(*) INTO col_exists
        FROM information_schema.columns
        WHERE table_name = 'participantes' AND column_name = 'pessoa_id';
        IF col_exists = 0 THEN
            ALTER TABLE participantes RENAME COLUMN nome TO nome_old;
            ALTER TABLE participantes RENAME COLUMN email TO email_old;
            ALTER TABLE participantes ADD COLUMN pessoa_id INTEGER REFERENCES pessoas(id) ON DELETE CASCADE;
            ALTER TABLE participantes ADD CONSTRAINT participantes_palestra_pessoa_unique UNIQUE (palestra_id, pessoa_id);
            ALTER TABLE participantes DROP COLUMN nome_old;
            ALTER TABLE participantes DROP COLUMN email_old;
        END IF;
    END $$;""",
]


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
                for mig in MIGRATIONS:
                    cursor.execute(mig)
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
