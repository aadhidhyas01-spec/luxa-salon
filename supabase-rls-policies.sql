-- =============================================
-- RLS Policies for Salon Lux App
-- Run this in Supabase SQL Editor to allow
-- the anon key to read and write all tables.
-- =============================================

-- Enable RLS on all tables (if not already enabled)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE salons ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------
-- SALONS: Public read, anon can insert/update/delete
-- -----------------------------------------------
DROP POLICY IF EXISTS "Allow public read on salons" ON salons;
CREATE POLICY "Allow public read on salons" ON salons
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Allow anon insert on salons" ON salons;
CREATE POLICY "Allow anon insert on salons" ON salons
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon update on salons" ON salons;
CREATE POLICY "Allow anon update on salons" ON salons
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon delete on salons" ON salons;
CREATE POLICY "Allow anon delete on salons" ON salons
    FOR DELETE TO anon, authenticated USING (true);

-- -----------------------------------------------
-- SERVICES: Public read, anon can insert/update/delete
-- -----------------------------------------------
DROP POLICY IF EXISTS "Allow public read on services" ON services;
CREATE POLICY "Allow public read on services" ON services
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Allow anon insert on services" ON services;
CREATE POLICY "Allow anon insert on services" ON services
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon update on services" ON services;
CREATE POLICY "Allow anon update on services" ON services
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon delete on services" ON services;
CREATE POLICY "Allow anon delete on services" ON services
    FOR DELETE TO anon, authenticated USING (true);

-- -----------------------------------------------
-- USERS: Anon can read, insert, update
-- -----------------------------------------------
DROP POLICY IF EXISTS "Allow public read on users" ON users;
CREATE POLICY "Allow public read on users" ON users
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Allow anon insert on users" ON users;
CREATE POLICY "Allow anon insert on users" ON users
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon update on users" ON users;
CREATE POLICY "Allow anon update on users" ON users
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

-- -----------------------------------------------
-- BOOKINGS: Anon can read, insert, update, delete
-- -----------------------------------------------
DROP POLICY IF EXISTS "Allow public read on bookings" ON bookings;
CREATE POLICY "Allow public read on bookings" ON bookings
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Allow anon insert on bookings" ON bookings;
CREATE POLICY "Allow anon insert on bookings" ON bookings
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon update on bookings" ON bookings;
CREATE POLICY "Allow anon update on bookings" ON bookings
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon delete on bookings" ON bookings;
CREATE POLICY "Allow anon delete on bookings" ON bookings
    FOR DELETE TO anon, authenticated USING (true);

-- -----------------------------------------------
-- REVIEWS: Anon can read, insert
-- -----------------------------------------------
DROP POLICY IF EXISTS "Allow public read on reviews" ON reviews;
CREATE POLICY "Allow public read on reviews" ON reviews
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Allow anon insert on reviews" ON reviews;
CREATE POLICY "Allow anon insert on reviews" ON reviews
    FOR INSERT TO anon, authenticated WITH CHECK (true);

-- -----------------------------------------------
-- Reset sequences if tables were seeded with IDs
-- -----------------------------------------------
SELECT setval('users_id_seq',   COALESCE((SELECT MAX(id) FROM users),   1));
SELECT setval('salons_id_seq',  COALESCE((SELECT MAX(id) FROM salons),  1));
SELECT setval('services_id_seq',COALESCE((SELECT MAX(id) FROM services),1));
