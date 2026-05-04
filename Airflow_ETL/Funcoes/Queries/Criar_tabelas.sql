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

    credito_total DECIMAL(14,2),
    credito_pf DECIMAL(14,2),
    credito_pj DECIMAL(14,2),

    concessoes_total DECIMAL(14,2),
    concessoes_pf DECIMAL(14,2),
    concessoes_pj DECIMAL(14,2),

    selic DECIMAL(5,2),
    ipca DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (tipo IN ('PF', 'PJ')),

    pd DOUBLE PRECISION,

    -- =========================
    -- PF
    -- =========================
    idade INTEGER,
    score DOUBLE PRECISION,
    renda DOUBLE PRECISION,
    comprometimento_renda DOUBLE PRECISION,
    tempo_empresa INTEGER,
    patrimonio DOUBLE PRECISION,
    tempo_relacionamento INTEGER,

    -- =========================
    -- PJ
    -- =========================
    faturamento_mensal DOUBLE PRECISION,
    faturamento_anual DOUBLE PRECISION,
    margem_lucro DOUBLE PRECISION,
    alavancagem DOUBLE PRECISION,
    setor TEXT,
    num_funcionarios INTEGER,

    -- =========================
    -- comum
    -- =========================
    historico_atraso INTEGER,

    inativo_meses INTEGER DEFAULT 0,
    removido BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operacoes (
    id TEXT PRIMARY KEY,

    cliente_id TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('PF', 'PJ')),

    pd DOUBLE PRECISION,

    valor DOUBLE PRECISION,
    prazo INTEGER,
    juros DOUBLE PRECISION,

    saldo_devedor DOUBLE PRECISION,

    parcelas_total INTEGER,
    parcelas_pagas INTEGER,
    parcela_valor DOUBLE PRECISION,

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

CREATE TABLE IF NOT EXISTS clientes_historico (
    cliente_id TEXT,
    data_ref DATE,

    tipo TEXT CHECK (tipo IN ('PF', 'PJ')),
    pd DOUBLE PRECISION,

    -- PF
    idade INTEGER,
    score DOUBLE PRECISION,
    renda DOUBLE PRECISION,
    comprometimento_renda DOUBLE PRECISION,
    tempo_empresa INTEGER,
    patrimonio DOUBLE PRECISION,
    tempo_relacionamento INTEGER,

    -- PJ
    faturamento_mensal DOUBLE PRECISION,
    faturamento_anual DOUBLE PRECISION,
    margem_lucro DOUBLE PRECISION,
    alavancagem DOUBLE PRECISION,
    setor TEXT,
    num_funcionarios INTEGER,

    -- comum
    historico_atraso INTEGER,

    inativo_meses INTEGER,
    removido BOOLEAN,
    created_at TIMESTAMP,

    PRIMARY KEY (cliente_id, data_ref)
);

CREATE TABLE IF NOT EXISTS operacoes_historico (
    id TEXT,
    data_ref DATE,

    cliente_id TEXT,
    tipo TEXT CHECK (tipo IN ('PF', 'PJ')),

    pd DOUBLE PRECISION,

    valor DOUBLE PRECISION,
    prazo INTEGER,
    juros DOUBLE PRECISION,

    saldo_devedor DOUBLE PRECISION,

    parcelas_total INTEGER,
    parcelas_pagas INTEGER,
    parcela_valor DOUBLE PRECISION,

    status TEXT CHECK (
        status IN ('ativa', 'over 30', 'over 60', 'over 90')
    ),

    meses_em_atraso INTEGER,
    data_contratacao DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id, data_ref)
);