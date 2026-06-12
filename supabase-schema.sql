-- Supabase PostgreSQL Schema: Bangalore Luxury Salon Finder

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Salons Table
CREATE TABLE IF NOT EXISTS salons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    rating NUMERIC(2, 1) DEFAULT 5.0,
    price_range VARCHAR(10) DEFAULT '₹₹',
    description TEXT,
    image_path VARCHAR(256),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Services Table
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    salon_id INTEGER REFERENCES salons(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    duration INTEGER NOT NULL, -- in minutes
    price INTEGER NOT NULL,     -- in INR
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    salon_id INTEGER REFERENCES salons(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time VARCHAR(10) NOT NULL, -- e.g., '03:30 PM'
    stylist VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'Cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    salon_id INTEGER REFERENCES salons(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seeding Initial Data

-- Seed Users (Passwords: adminpassword, userpassword)
-- Note: password_hash values generated using pbkdf2:sha256 matching Werkzeug security helper
INSERT INTO users (name, email, password_hash, phone, is_admin)
VALUES 
('Admin Manager', 'admin@salonlux.in', 'scrypt:32768:8:1$e45i7z6s$93cf82405d41c9b4e18fe862d29487c6999a0937a09ea146f3322d861d8ee46e3fb2420f188365114757c3d25686036c0a5fa70697a22a36b356eb5f7ccce986', '+91 98765 43210', TRUE),
('Aarav Sharma', 'user@salonlux.in', 'scrypt:32768:8:1$pG7y5qWs$f7c89cb289db1fbc10db2a4e98f7e340a6b1037f09ea146f3322d861d8ee46e3fb2420f188365114757c3d25686036c0a5fa70697a22a36b356eb5f7ccce986', '+91 99887 76655', FALSE)
ON CONFLICT (email) DO NOTHING;

-- Seed Salons
INSERT INTO salons (id, name, area, rating, price_range, description, image_path)
VALUES 
(1, 'The Grand Silhouette', 'Indiranagar', 4.9, '₹₹₹₹', 'An ultra-exclusive grooming atelier offering bespoke hair couture, restorative clinical skincare, and luxury holistic therapy under the guidance of internationally certified art directors.', '/static/images/salon_1.png'),
(2, 'En Vogue Atelier', 'Lavelle Road', 4.8, '₹₹₹₹', 'Nestled in Bangalore''s premier luxury district, En Vogue Atelier features global runway stylists, personalized aesthetics consulting, and premium organic spa treatments within a private, gold-trimmed sanctuary.', '/static/images/salon_2.png'),
(3, 'Aura Wellness & Styling', 'Koramangala', 4.7, '₹₹₹', 'A contemporary glass-walled sanctuary of modern styling and tranquil wellness. Specializing in advanced hair transformations, botanical scalp therapies, and high-fashion nail couture.', '/static/images/salon_3.png'),
(4, 'Prism & Polish', 'Sadashivanagar', 4.6, '₹₹₹', 'A premium beauty boutique focusing on luxury manicures, advanced lash techniques, rejuvenating facial therapy, and custom bridal transformations using global beauty brands.', '/static/images/salon_4.png')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name, 
    area = EXCLUDED.area, 
    rating = EXCLUDED.rating, 
    price_range = EXCLUDED.price_range, 
    description = EXCLUDED.description, 
    image_path = EXCLUDED.image_path;

-- Seed Services
INSERT INTO services (id, salon_id, name, duration, price)
VALUES 
-- The Grand Silhouette
(1, 1, 'Royal Signature Haircut', 60, 2500),
(2, 1, 'Balayage & Hair Couture', 180, 7500),
(3, 1, '24k Gold Radiance Facial', 90, 5500),
(4, 1, 'Lux Hammam Spa Massage', 90, 4500),
(5, 1, 'Caviar Deluxe Pedicure', 60, 2200),
-- En Vogue Atelier
(6, 2, 'Director''s Cut & Styling', 60, 3000),
(7, 2, 'Moroccan Argan Therapy', 120, 4800),
(8, 2, 'HydraFacial Elite', 75, 6500),
(9, 2, 'Aromatherapy Deep Tissue', 90, 4000),
(10, 2, 'Luxury Gel Manicure', 45, 1800),
-- Aura Wellness & Styling
(11, 3, 'Creative Haircut & Wash', 45, 1500),
(12, 3, 'Keratin Intense Infusion', 150, 6000),
(13, 3, 'Organic Botanical Facial', 60, 3200),
(14, 3, 'Stress Relief Massage', 60, 2800),
(15, 3, 'Chrome & Matte Nail Art', 60, 1600),
-- Prism & Polish
(16, 4, 'Premium Blow Dry & Styled Waves', 45, 1200),
(17, 4, 'Collagen Booster Facial', 60, 4000),
(18, 4, 'Hot Stone Body Massage', 75, 3500),
(19, 4, 'Acrylic Nail Extensions', 90, 2500),
(20, 4, 'Premium Paraffin Pedicure', 60, 1500)
ON CONFLICT (id) DO UPDATE SET 
    salon_id = EXCLUDED.salon_id,
    name = EXCLUDED.name,
    duration = EXCLUDED.duration,
    price = EXCLUDED.price;

-- Seed Reviews
INSERT INTO reviews (user_id, salon_id, rating, comment)
VALUES 
(2, 1, 5, 'Absolutely top-notch! The Royal Signature Haircut was incredible. The stylists understand luxury, and the gold-trimmed decor makes you feel like royalty.'),
(2, 2, 5, 'En Vogue Atelier is the best in Bangalore. Loved the HydraFacial Elite, my skin is glowing. Extremely professional staff and private rooms.'),
(2, 3, 4, 'Very peaceful ambiance and beautiful glass interiors. The Keratin treatment did wonders to my frizzy hair. Highly recommend!'),
(2, 4, 4, 'Lovely nail art work. A bit busy on weekends, but the wait was worth it. Will visit again.');

-- Reset serial sequences to prevent ID collision conflicts in the future
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('salons_id_seq', (SELECT MAX(id) FROM salons));
SELECT setval('services_id_seq', (SELECT MAX(id) FROM services));
