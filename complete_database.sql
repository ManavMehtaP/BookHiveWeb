CREATE DATABASE IF NOT EXISTS seathive_db;

USE seathive_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_user VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    event_end_time TIME,
    price DECIMAL(10,2) NOT NULL,
    available_seats INT DEFAULT 100,
    total_seats INT DEFAULT 100,
    image_url TEXT,
    image_filename VARCHAR(255),
    image_path VARCHAR(500),
    description TEXT,
    created_by INT,
    featured BOOLEAN DEFAULT FALSE,
    status ENUM('active', 'cancelled', 'postponed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS event_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#ff5e1a',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NULL,
    booking_reference VARCHAR(50) UNIQUE,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    seats_booked INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    booking_status ENUM('active', 'cancelled') DEFAULT 'active',
    payment_status ENUM('paid', 'refunded') DEFAULT 'paid',
    notes TEXT,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    profile_picture VARCHAR(255),
    bio TEXT,
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zip_code VARCHAR(20),
    favorite_genres JSON,
    social_links JSON,
    notification_preferences JSON,
    privacy_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    total_bookings INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    upcoming_bookings INT DEFAULT 0,
    past_bookings INT DEFAULT 0,
    cancelled_bookings INT DEFAULT 0,
    favorite_category VARCHAR(100),
    last_booking_date TIMESTAMP NULL,
    average_booking_value DECIMAL(10,2) DEFAULT 0.00,
    most_expensive_booking DECIMAL(10,2) DEFAULT 0.00,
    membership_tier ENUM('bronze', 'silver', 'gold', 'platinum') DEFAULT 'bronze',
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    promotional_emails BOOLEAN DEFAULT TRUE,
    booking_reminders BOOLEAN DEFAULT TRUE,
    event_recommendations BOOLEAN DEFAULT TRUE,
    newsletter_subscription BOOLEAN DEFAULT FALSE,
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency_preference VARCHAR(3) DEFAULT 'USD',
    theme_preference ENUM('light', 'dark', 'auto') DEFAULT 'auto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    booking_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_title VARCHAR(255),
    would_recommend BOOLEAN DEFAULT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_event_review (user_id, event_id)
);

CREATE TABLE IF NOT EXISTS user_login_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_status ENUM('success', 'failed') DEFAULT 'success',
    session_duration INT NULL,
    logout_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    method_type ENUM('credit_card', 'debit_card', 'paypal', 'stripe') NOT NULL,
    method_nickname VARCHAR(100),
    card_last_four VARCHAR(4),
    card_brand VARCHAR(50),
    expiry_month INT,
    expiry_year INT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_event_id ON bookings(event_id);
CREATE INDEX idx_bookings_status ON bookings(booking_status);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_genre ON events(genre);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_statistics_user_id ON user_statistics(user_id);
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_reviews_user_id ON user_reviews(user_id);
CREATE INDEX idx_user_reviews_event_id ON user_reviews(event_id);
CREATE INDEX idx_user_reviews_booking_id ON user_reviews(booking_id);
CREATE INDEX idx_user_login_history_user_id ON user_login_history(user_id);
CREATE INDEX idx_user_login_history_login_time ON user_login_history(login_time);
CREATE INDEX idx_user_payment_methods_user_id ON user_payment_methods(user_id);


CREATE OR REPLACE VIEW user_booking_history AS
SELECT 
    b.id,
    b.user_id,
    b.event_id,
    b.booking_reference,
    b.customer_name,
    b.customer_email,
    b.phone,
    b.seats_booked,
    b.total_price,
    b.booking_status,
    b.payment_status,
    b.booking_date,
    b.notes,
    e.title as event_title,
    e.genre as event_genre,
    e.event_date,
    e.event_time,
    e.location,
    e.venue,
    u.username as booked_by_username,
    u.full_name as booked_by_name
FROM bookings b
LEFT JOIN events e ON b.event_id = e.id
LEFT JOIN users u ON b.user_id = u.id
ORDER BY b.booking_date DESC;

CREATE OR REPLACE VIEW user_booking_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    COUNT(b.id) as total_bookings,
    COALESCE(SUM(b.total_price), 0) as total_spent,
    COUNT(CASE WHEN e.event_date >= CURDATE() THEN 1 END) as upcoming_bookings,
    COUNT(CASE WHEN e.event_date < CURDATE() THEN 1 END) as past_bookings,
    COUNT(CASE WHEN b.booking_status = 'cancelled' THEN 1 END) as cancelled_bookings,
    COALESCE(AVG(b.total_price), 0) as average_booking_value,
    COALESCE(MAX(b.total_price), 0) as most_expensive_booking,
    MAX(b.booking_date) as last_booking_date
FROM users u
LEFT JOIN bookings b ON u.id = b.user_id
LEFT JOIN events e ON b.event_id = e.id
GROUP BY u.id, u.username, u.email;


INSERT INTO categories (name, description, color) VALUES
('Music', 'Live concerts and musical performances', '#ff5e1a'),
('Festivals', 'Cultural celebrations and festive events', '#f59e0b'),
('Food & Drink', 'Culinary events and festivals', '#10b981'),
('Sports', 'Sports events and competitions', '#ef4444'),
('Art', 'Art exhibitions and galleries', '#a855f7'),
('Comedy', 'Stand-up comedy and shows', '#f59e0b');

INSERT INTO users (username, email, password_user, full_name, role) VALUES
('admin', 'admin@seathive.com', 'admin123', 'System Administrator', 'admin');

INSERT INTO users (username, email, password_user, full_name, role) VALUES
('john_doe', 'john@example.com', 'user123', 'John Doe', 'user');

INSERT INTO events (title, genre, location, venue, event_date, event_time, price, available_seats, total_seats, image_url, image_filename, description, featured, status, created_by) VALUES
('Summer Music Festival', 'Music', 'Central Park, New York', 'Central Park Amphitheater', '2024-07-15', '18:00:00', 89.99, 75, 100, 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800', 'summer_music_festival.jpg', 'The biggest music festival of the summer featuring top artists from around the world.', TRUE, 'active', 1),
('Cultural Fest 2024', 'Festivals', 'Central Park, New York', 'Festival Grounds', '2024-08-22', '10:00:00', 299.99, 150, 200, 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800', 'cultural_fest_2024.jpg', 'Annual cultural festival celebrating diversity and heritage.', TRUE, 'active', 1),
('Food & Wine Expo', 'Food & Drink', 'Navy Pier, Chicago', 'Navy Pier Grand Hall', '2024-09-05', '11:00:00', 65.50, 200, 250, 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800', 'food_wine_expo.jpg', 'Experience the finest cuisine and wines from top chefs and wineries.', FALSE, 'active', 1),
('Marathon 2024', 'Sports', 'Downtown, Boston', 'Boston Common Start Line', '2024-10-10', '07:00:00', 120.00, 500, 500, 'https://images.unsplash.com/photo-1530137073521-4391dd269d39?w=800', 'marathon_2024.jpg', 'Annual marathon through the historic streets of Boston.', FALSE, 'active', 1),
('Art Exhibition', 'Art', 'The Met, New York', 'Metropolitan Museum Gallery', '2024-11-15', '10:00:00', 35.00, 80, 100, 'https://images.unsplash.com/photo-1531913764164-f85c52d6e654?w=800', 'art_exhibition.jpg', 'Contemporary art exhibition featuring emerging artists.', FALSE, 'active', 1),
('Comedy Night', 'Comedy', 'Laugh Factory, Los Angeles', 'Laugh Factory Main Stage', '2024-12-05', '20:00:00', 45.00, 90, 120, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800', 'comedy_night.jpg', 'An evening of laughter with top comedians from around the country.', FALSE, 'active', 1);

INSERT INTO bookings (event_id, user_id, booking_reference, customer_name, customer_email, phone, seats_booked, total_price, booking_status, payment_status, notes) VALUES
(1, 2, 'BK20240208ABC123', 'John Doe', 'john@example.com', '555-0101', 2, 179.98, 'active', 'paid', 'Excited for the music festival!'),
(1, NULL, 'BK20240208DEF456', 'Jane Smith', 'jane@email.com', '555-0102', 3, 269.97, 'active', 'paid', 'Guest booking - paid at venue'),
(2, 2, 'BK20240208GHI789', 'John Doe', 'john@example.com', '555-0101', 1, 299.99, 'active', 'paid', 'Looking forward to the cultural festival!'),
(3, NULL, 'BK20240208JKL012', 'Bob Johnson', 'bob@company.com', '555-0103', 5, 327.50, 'active', 'paid', 'Corporate team building event'),
(4, 2, 'BK20240208MNO345', 'John Doe', 'john@example.com', '555-0101', 1, 120.00, 'active', 'paid', 'Work schedule confirmed'),
(5, NULL, 'BK20240208PQR678', 'Alice Brown', 'alice@email.com', '555-0104', 2, 70.00, 'active', 'paid', 'Date night with friend');


INSERT IGNORE INTO user_preferences (user_id) 
SELECT id FROM users WHERE id NOT IN (SELECT user_id FROM user_preferences);

INSERT IGNORE INTO user_statistics (user_id, total_bookings, total_spent)
SELECT 
    u.id,
    COALESCE(booking_counts.total_bookings, 0),
    COALESCE(booking_counts.total_spent, 0.00)
FROM users u
LEFT JOIN (
    SELECT 
        user_id, 
        COUNT(id) as total_bookings, 
        COALESCE(SUM(total_price), 0) as total_spent
    FROM bookings 
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) booking_counts ON u.id = booking_counts.user_id
WHERE u.id NOT IN (SELECT user_id FROM user_statistics);


CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    profile_picture VARCHAR(255),
    bio TEXT,
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zip_code VARCHAR(20),
    favorite_genres JSON,
    social_links JSON,
    notification_preferences JSON,
    privacy_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    total_bookings INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    upcoming_bookings INT DEFAULT 0,
    past_bookings INT DEFAULT 0,
    cancelled_bookings INT DEFAULT 0,
    favorite_category VARCHAR(100),
    last_booking_date TIMESTAMP NULL,
    average_booking_value DECIMAL(10,2) DEFAULT 0.00,
    most_expensive_booking DECIMAL(10,2) DEFAULT 0.00,
    membership_tier ENUM('bronze', 'silver', 'gold', 'platinum') DEFAULT 'bronze',
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    promotional_emails BOOLEAN DEFAULT TRUE,
    booking_reminders BOOLEAN DEFAULT TRUE,
    event_recommendations BOOLEAN DEFAULT TRUE,
    newsletter_subscription BOOLEAN DEFAULT FALSE,
    language_preference VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency_preference VARCHAR(3) DEFAULT 'USD',
    theme_preference ENUM('light', 'dark', 'auto') DEFAULT 'auto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    booking_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_title VARCHAR(255),
    would_recommend BOOLEAN DEFAULT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_event_review (user_id, event_id)
);

CREATE TABLE IF NOT EXISTS user_login_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_status ENUM('success', 'failed') DEFAULT 'success',
    session_duration INT NULL,
    logout_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    method_type ENUM('credit_card', 'debit_card', 'paypal', 'stripe') NOT NULL,
    method_nickname VARCHAR(100),
    card_last_four VARCHAR(4),
    card_brand VARCHAR(50),
    expiry_month INT,
    expiry_year INT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_statistics_user_id ON user_statistics(user_id);
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_reviews_user_id ON user_reviews(user_id);
CREATE INDEX idx_user_reviews_event_id ON user_reviews(event_id);
CREATE INDEX idx_user_login_history_user_id ON user_login_history(user_id);
CREATE INDEX idx_user_login_history_login_time ON user_login_history(login_time);
CREATE INDEX idx_user_payment_methods_user_id ON user_payment_methods(user_id);

CREATE OR REPLACE VIEW user_booking_summary AS
SELECT
    u.id as user_id,
    u.username,
    u.email,
    COUNT(b.id) as total_bookings,
    COALESCE(SUM(b.total_price), 0) as total_spent,
    COUNT(CASE WHEN e.event_date >= CURDATE() THEN 1 END) as upcoming_bookings,
    COUNT(CASE WHEN e.event_date < CURDATE() THEN 1 END) as past_bookings,
    COUNT(CASE WHEN b.booking_status = 'cancelled' THEN 1 END) as cancelled_bookings,
    COALESCE(AVG(b.total_price), 0) as average_booking_value,
    COALESCE(MAX(b.total_price), 0) as most_expensive_booking,
    MAX(b.booking_date) as last_booking_date
FROM users u
LEFT JOIN bookings b ON u.id = b.user_id
LEFT JOIN events e ON b.event_id = e.id
GROUP BY u.id, u.username, u.email;

INSERT IGNORE INTO user_preferences (user_id)
SELECT id FROM users WHERE id NOT IN (SELECT user_id FROM user_preferences);

INSERT IGNORE INTO user_statistics (user_id, total_bookings, total_spent)
SELECT
    u.id,
    COALESCE(booking_counts.total_bookings, 0),
    COALESCE(booking_counts.total_spent, 0.00)
FROM users u
LEFT JOIN (
    SELECT
        user_id,
        COUNT(id) as total_bookings,
        COALESCE(SUM(total_price), 0) as total_spent
    FROM bookings
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) booking_counts ON u.id = booking_counts.user_id
WHERE u.id NOT IN (SELECT user_id FROM user_statistics);


