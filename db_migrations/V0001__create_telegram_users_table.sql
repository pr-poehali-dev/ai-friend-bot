CREATE TABLE IF NOT EXISTS telegram_users (
    telegram_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    personality_mode VARCHAR(50) DEFAULT 'friendly',
    is_premium BOOLEAN DEFAULT FALSE,
    nsfw_enabled BOOLEAN DEFAULT FALSE,
    spicy_level INTEGER DEFAULT 30,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_telegram_id ON chat_history(telegram_id);
CREATE INDEX idx_created_at ON chat_history(created_at);