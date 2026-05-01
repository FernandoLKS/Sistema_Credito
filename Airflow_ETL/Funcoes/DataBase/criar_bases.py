from conexoes import executar_sql

def criar_tabelas():

  def criar_tabelas():

    query = """
    -- ============================================
    -- TABELA: BCB INDICADORES MACRO
    -- ============================================
    CREATE TABLE IF NOT EXISTS bcb_macro (
        data DATE PRIMARY KEY,
        
        inadimplencia_total_mais_90dias DECIMAL(5,2),
        inadimplencia_pf_mais_90dias DECIMAL(5,2),
        inadimplencia_pj_mais_90dias DECIMAL(5,2),
        inadimplencia_total_15_90dias DECIMAL(5,2),
        inadimplencia_pf_15_90dias DECIMAL(5,2),
        inadimplencia_pj_15_90dias DECIMAL(5,2),
        
        juros_credito DECIMAL(5,2),
        spread_bancario DECIMAL(5,2),
        
        credito_total DECIMAL(12,2),
        credito_pf DECIMAL(12,2),
        credito_pj DECIMAL(12,2),
        concessoes_total DECIMAL(12,2),
        concessoes_pf DECIMAL(12,2),
        concessoes_pj DECIMAL(12,2),
        
        selic DECIMAL(5,2),
        ipca DECIMAL(5,2)
    );

    -- ============================================
    -- TABELA: CLIENTES (ESTADO ATUAL)
    -- ============================================
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id TEXT PRIMARY KEY,
        tipo TEXT NOT NULL CHECK (tipo IN ('PF', 'PJ')),

        pd NUMERIC(10,6),

        renda NUMERIC,
        faturamento_anual NUMERIC,

        inativo_meses INTEGER DEFAULT 0,
        removido BOOLEAN DEFAULT FALSE,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    -- ============================================
    -- TABELA: OPERACOES (ESTADO ATUAL)
    -- ============================================
    CREATE TABLE IF NOT EXISTS operacoes (
        id SERIAL PRIMARY KEY,

        cliente_id TEXT NOT NULL,
        tipo TEXT CHECK (tipo IN ('PF', 'PJ')),

        pd NUMERIC(10,6),

        valor NUMERIC,
        prazo INTEGER,
        juros NUMERIC(10,6),

        saldo_devedor NUMERIC,

        parcelas_total INTEGER,
        parcelas_pagas INTEGER,
        parcela_valor NUMERIC,

        status TEXT CHECK (
            status IN ('ativa', 'over 30', 'over 60', 'over 90')
        ),

        meses_em_atraso INTEGER DEFAULT 0,

        data_contratacao DATE DEFAULT CURRENT_DATE,

        CONSTRAINT fk_cliente
            FOREIGN KEY(cliente_id)
            REFERENCES clientes(cliente_id)
            ON DELETE CASCADE
    );


    -- ============================================
    -- TABELA: CLIENTES HISTORICO
    -- ============================================
    CREATE TABLE IF NOT EXISTS clientes_historico (
        data_ref DATE NOT NULL,
        cliente_id TEXT NOT NULL,

        tipo TEXT,
        pd NUMERIC(10,6),

        inativo_meses INTEGER,
        removido BOOLEAN,

        PRIMARY KEY (data_ref, cliente_id)
    );


    -- ============================================
    -- TABELA: OPERACOES HISTORICO
    -- ============================================
    CREATE TABLE IF NOT EXISTS operacoes_historico (
        data_ref DATE NOT NULL,
        operacao_id INTEGER NOT NULL,

        cliente_id TEXT,

        saldo_devedor NUMERIC,
        status TEXT,
        meses_em_atraso INTEGER,

        PRIMARY KEY (data_ref, operacao_id)
    );


    -- ============================================
    -- ÍNDICES (PERFORMANCE)
    -- ============================================

    CREATE INDEX IF NOT EXISTS idx_clientes_tipo
        ON clientes(tipo);

    CREATE INDEX IF NOT EXISTS idx_clientes_removido
        ON clientes(removido);

    CREATE INDEX IF NOT EXISTS idx_operacoes_cliente
        ON operacoes(cliente_id);

    CREATE INDEX IF NOT EXISTS idx_operacoes_status
        ON operacoes(status);

    CREATE INDEX IF NOT EXISTS idx_operacoes_historico_data
        ON operacoes_historico(data_ref);

    CREATE INDEX IF NOT EXISTS idx_clientes_historico_data
        ON clientes_historico(data_ref);

    """

    executar_sql(query, fetch=False)