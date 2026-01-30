-- Сначала создаем таблицу (Требование ТЗ)
CREATE TABLE IF NOT EXISTS price_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    timestamp BIGINT NOT NULL,  -- UNIX timestamp (Требование ТЗ)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Потом создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_price_data_ticker ON price_data(ticker);
CREATE INDEX IF NOT EXISTS idx_price_data_timestamp ON price_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_price_data_ticker_timestamp ON price_data(ticker, timestamp DESC);

-- Комментарии к таблице
COMMENT ON TABLE price_data IS 'Хранение цен с Deribit (ТЗ: btc_usd и eth_usd)';
COMMENT ON COLUMN price_data.ticker IS 'Тикер валюты (btc_usd или eth_usd)';
COMMENT ON COLUMN price_data.price IS 'Цена валюты (index price)';
COMMENT ON COLUMN price_data.timestamp IS 'Время в UNIX timestamp (Требование ТЗ)';
