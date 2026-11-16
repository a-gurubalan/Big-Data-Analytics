CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS waste_records (
    waste_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category_id INTEGER,
    image_path TEXT,
    predicted_label TEXT,
    confidence_score REAL,
    review_status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES waste_categories(category_id)
);

CREATE TABLE IF NOT EXISTS waste_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    waste_group TEXT,
    biodegradability TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    action_title TEXT NOT NULL,
    instructions TEXT,
    disposal_method TEXT,
    FOREIGN KEY (category_id)
        REFERENCES waste_categories(category_id)
);

CREATE TABLE IF NOT EXISTS analytics_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_by INTEGER,
    report_type TEXT,
    date_from TEXT,
    date_to TEXT,
    file_path TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by)
        REFERENCES users(user_id)
);