-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    referred_by_code VARCHAR(20) NULL,
    referred_by_user_id BIGINT NULL,

    -- Profile
    name VARCHAR(100),
    email VARCHAR(100),

    -- Balance
    wallet_balance DECIMAL(15, 2) DEFAULT 0.00,
    total_deposited DECIMAL(15, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(15, 2) DEFAULT 0.00,
    total_commission_earned DECIMAL(15, 2) DEFAULT 0.00,

    -- UPI Details
    upi_id VARCHAR(100),
    upi_holder_name VARCHAR(100),
    bank_name VARCHAR(100),
    is_upi_bound BOOLEAN DEFAULT FALSE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,

    FOREIGN KEY (referred_by_user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by_user_id);

-- Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin' CHECK (role IN ('super_admin', 'admin', 'support')),

    permissions JSONB,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username);
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);

-- Crypto Wallets Table
CREATE TABLE IF NOT EXISTS crypto_wallets (
    id BIGSERIAL PRIMARY KEY,
    network_type VARCHAR(20) NOT NULL,
    wallet_address VARCHAR(100) NOT NULL UNIQUE,
    currency VARCHAR(10) DEFAULT 'USDT',
    is_active BOOLEAN DEFAULT TRUE,
    assigned_to_user_id BIGINT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_crypto_wallets_network ON crypto_wallets(network_type);
CREATE INDEX IF NOT EXISTS idx_crypto_wallets_address ON crypto_wallets(wallet_address);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_uid VARCHAR(50) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,

    type VARCHAR(20) NOT NULL CHECK (type IN ('deposit', 'withdrawal', 'commission')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'approved', 'rejected', 'completed', 'failed')),

    crypto_network VARCHAR(20),
    crypto_wallet_address VARCHAR(100),
    crypto_amount DECIMAL(15, 6),
    crypto_tx_hash VARCHAR(100),

    screenshot_url VARCHAR(500),
    user_notes TEXT,

    exchange_rate DECIMAL(10, 2),
    platform_fee_percent DECIMAL(5, 2),
    platform_fee_amount DECIMAL(15, 2),
    bonus_percent DECIMAL(5, 2) DEFAULT 0,
    bonus_amount DECIMAL(15, 2) DEFAULT 0,

    gross_inr_amount DECIMAL(15, 2),
    net_inr_amount DECIMAL(15, 2),

    user_upi_id VARCHAR(100),
    user_bank_name VARCHAR(100),

    admin_id BIGINT NULL,
    admin_reviewed_at TIMESTAMP NULL,
    admin_notes TEXT,
    rejection_reason TEXT,

    payment_reference VARCHAR(100),
    payment_completed_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- Commissions Table
CREATE TABLE IF NOT EXISTS commissions (
    id BIGSERIAL PRIMARY KEY,
    referrer_user_id BIGINT NOT NULL,
    referred_user_id BIGINT NOT NULL,
    transaction_id BIGINT NOT NULL,

    commission_percent DECIMAL(5, 2) NOT NULL,
    base_amount DECIMAL(15, 2) NOT NULL,
    commission_amount DECIMAL(15, 2) NOT NULL,

    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'credited', 'cancelled')),
    credited_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (referrer_user_id) REFERENCES users(id),
    FOREIGN KEY (referred_user_id) REFERENCES users(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

CREATE INDEX IF NOT EXISTS idx_commissions_referrer ON commissions(referrer_user_id);
CREATE INDEX IF NOT EXISTS idx_commissions_transaction ON commissions(transaction_id);

-- Team Members Table
CREATE TABLE IF NOT EXISTS team_members (
    id BIGSERIAL PRIMARY KEY,
    parent_user_id BIGINT NOT NULL,
    child_user_id BIGINT NOT NULL,
    level INT DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_user_id) REFERENCES users(id),
    FOREIGN KEY (child_user_id) REFERENCES users(id),
    UNIQUE (parent_user_id, child_user_id)
);

CREATE INDEX IF NOT EXISTS idx_team_members_parent ON team_members(parent_user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_child ON team_members(child_user_id);

-- Platform Settings Table
CREATE TABLE IF NOT EXISTS platform_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    data_type VARCHAR(20) DEFAULT 'string' CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,

    updated_by_admin_id BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_platform_settings_key ON platform_settings(setting_key);

-- Activity Logs Table
CREATE TABLE IF NOT EXISTS activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NULL,
    admin_id BIGINT NULL,

    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,

    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_admin ON activity_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,

    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'transaction')),

    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,

    related_transaction_id BIGINT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_transaction_id) REFERENCES transactions(id)
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);

-- Insert Default Platform Settings
INSERT INTO platform_settings (setting_key, setting_value, data_type, description) VALUES
('usdt_to_inr_rate', '98.94', 'number', 'Current USDT to INR exchange rate'),
('platform_fee_percent', '2.0', 'number', 'Platform fee percentage on deposits'),
('bonus_percent', '2.0', 'number', 'Bonus percentage on deposits'),
('inr_bonus_ratio', '4.0', 'number', 'INR deposit bonus ratio'),
('commission_percent', '1.0', 'number', 'Referral commission percentage'),
('min_deposit_usdt', '10', 'number', 'Minimum deposit amount in USDT'),
('max_deposit_usdt', '10000', 'number', 'Maximum deposit amount in USDT'),
('telegram_support_url', 'https://t.me/showpay_support', 'string', 'Telegram support link'),
('trc20_wallet_address', '', 'string', 'TRC-20 USDT wallet address'),
('erc20_wallet_address', '', 'string', 'ERC-20 USDT wallet address')
ON CONFLICT (setting_key) DO NOTHING;
