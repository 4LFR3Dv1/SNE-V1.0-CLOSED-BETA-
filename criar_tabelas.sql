-- Script SQL para criar tabelas iniciais do SNE 1.0 Cloud
-- Execute este script no Cloud SQL via Cloud Shell

-- Tabela users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela signals
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    price DECIMAL(18, 8),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela trades
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);

-- Verificar tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;



