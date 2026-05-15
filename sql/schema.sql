-- =====================================================================
-- Product QR — PostgreSQL Schema
-- =====================================================================
-- Drops are commented out by default; uncomment if rebuilding from scratch.
-- DROP TABLE IF EXISTS qr_codes, generation_batches, whatsapp_presets,
--                      quantities, products, app_settings, admin_users CASCADE;

-- ---------------------------------------------------------------------
-- Admin users (JWT auth)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(150) UNIQUE NOT NULL,
    full_name       VARCHAR(150),
    hashed_password VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed default admin: email=admin@company.com password=admin123
-- (bcrypt hash of "admin123")
INSERT INTO admin_users (email, full_name, hashed_password, is_superuser)
VALUES (
    'admin@company.com',
    'Default Admin',
    '$2b$12$sDcNDRsOFUkKScVGCzaTcekyWb5EYcurxg/j1FjBeDa9iu9Z30TCO',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ---------------------------------------------------------------------
-- Products
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    initials    VARCHAR(4)   NOT NULL UNIQUE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

-- ---------------------------------------------------------------------
-- Quantities
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quantities (
    id            SERIAL PRIMARY KEY,
    label         VARCHAR(50) NOT NULL,
    internal_code CHAR(4)     NOT NULL UNIQUE,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_internal_code_len CHECK (char_length(internal_code) = 4)
);
CREATE INDEX IF NOT EXISTS idx_quantities_active ON quantities(is_active);

-- ---------------------------------------------------------------------
-- WhatsApp Presets
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS whatsapp_presets (
    id              SERIAL PRIMARY KEY,
    preset_name     VARCHAR(150) NOT NULL,
    whatsapp_number VARCHAR(20)  NOT NULL,
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_wa_presets_active ON whatsapp_presets(is_active);

-- Ensure at most one default preset
CREATE UNIQUE INDEX IF NOT EXISTS uq_wa_presets_default
    ON whatsapp_presets(is_default) WHERE is_default = TRUE;

-- ---------------------------------------------------------------------
-- Generation batches
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS generation_batches (
    id                SERIAL PRIMARY KEY,
    batch_name        VARCHAR(60) NOT NULL UNIQUE,
    total_codes       INTEGER NOT NULL DEFAULT 0,
    zoho_synced       INTEGER NOT NULL DEFAULT 0,
    zoho_failed       INTEGER NOT NULL DEFAULT 0,
    excel_file_path   TEXT,
    product_id        INTEGER REFERENCES products(id),
    quantity_id       INTEGER REFERENCES quantities(id),
    whatsapp_preset_id INTEGER REFERENCES whatsapp_presets(id),
    manufacturing_month SMALLINT,
    manufacturing_year  SMALLINT,
    created_by        INTEGER REFERENCES admin_users(id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_batches_created ON generation_batches(created_at DESC);

-- ---------------------------------------------------------------------
-- QR Codes (main records)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS qr_codes (
    id                  BIGSERIAL PRIMARY KEY,
    code                CHAR(15)    NOT NULL UNIQUE,
    short_token         VARCHAR(7)  NOT NULL UNIQUE,
    short_link          TEXT        NOT NULL,
    product_id          INTEGER     NOT NULL REFERENCES products(id),
    quantity_id         INTEGER     NOT NULL REFERENCES quantities(id),
    manufacturing_month SMALLINT    NOT NULL,
    manufacturing_year  SMALLINT    NOT NULL,
    whatsapp_preset_id  INTEGER     NOT NULL REFERENCES whatsapp_presets(id),
    whatsapp_link       TEXT        NOT NULL,
    zoho_record_id      VARCHAR(50),
    zoho_sync_status    VARCHAR(20) NOT NULL DEFAULT 'PENDING',
        -- PENDING | SYNCED | FAILED
    zoho_last_sync_at   TIMESTAMPTZ,
    zoho_error          TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'UNUSED',
        -- UNUSED | USED
    batch_id            INTEGER     NOT NULL REFERENCES generation_batches(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_code_len CHECK (char_length(code) = 15),
    CONSTRAINT chk_token_len CHECK (char_length(short_token) BETWEEN 5 AND 7)
);
CREATE INDEX IF NOT EXISTS idx_qr_batch        ON qr_codes(batch_id);
CREATE INDEX IF NOT EXISTS idx_qr_sync_status  ON qr_codes(zoho_sync_status);
CREATE INDEX IF NOT EXISTS idx_qr_product      ON qr_codes(product_id);
CREATE INDEX IF NOT EXISTS idx_qr_created      ON qr_codes(created_at DESC);

-- ---------------------------------------------------------------------
-- App settings (Zoho creds, short domain, etc.) — single-row key/value
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS app_settings (
    key         VARCHAR(80) PRIMARY KEY,
    value       TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed defaults (empty values; admin fills in via UI)
INSERT INTO app_settings (key, value) VALUES
    ('zoho_client_id', ''),
    ('zoho_client_secret', ''),
    ('zoho_refresh_token', ''),
    ('zoho_organization_id', ''),
    ('zoho_api_domain', 'https://www.zohoapis.com'),
    ('zoho_module_name', 'Product_QR'),
    ('short_domain', 'https://qr.company.com')
ON CONFLICT (key) DO NOTHING;

-- ---------------------------------------------------------------------
-- Sample seed data (safe to remove)
-- ---------------------------------------------------------------------
INSERT INTO products (name, initials) VALUES
    ('Vajeer', 'VJ'),
    ('Vegmax', 'VG')
ON CONFLICT (initials) DO NOTHING;

INSERT INTO quantities (label, internal_code) VALUES
    ('1L',     '1000'),
    ('500ml',  '0500'),
    ('250ml',  '0250')
ON CONFLICT (internal_code) DO NOTHING;

INSERT INTO whatsapp_presets (preset_name, whatsapp_number, is_default) VALUES
    ('Sales Team',   '919999999999', TRUE),
    ('Support Team', '918888888888', FALSE)
ON CONFLICT DO NOTHING;
