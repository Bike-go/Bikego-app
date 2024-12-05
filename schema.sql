-- Schema and Search Path Setup
CREATE SCHEMA IF NOT EXISTS {{db_schema_name}};
SET search_path TO {{db_schema_name}};

-- Role Enum
DROP TYPE IF EXISTS role_enum CASCADE;
CREATE TYPE role_enum AS ENUM ('Admin', 'Employee', 'Customer', 'Service');

-- User Table
CREATE TABLE IF NOT EXISTS "User" (
  "id" UUID PRIMARY KEY,
  "username" VARCHAR(45) NOT NULL,
  "password_hash" VARCHAR(255) NOT NULL,
  "email" VARCHAR(100) NOT NULL,
  "phone_number" VARCHAR(15),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "last_login" TIMESTAMPTZ,
  "profile_picture_url" VARCHAR(255),
  "picture_delete_hash" VARCHAR(255),
  "email_verified" BOOLEAN NOT NULL,
  "darkmode" BOOLEAN NOT NULL,
  "role" role_enum NOT NULL
);

-- News Table
CREATE TABLE IF NOT EXISTS "News" (
  "id" SERIAL PRIMARY KEY,
  "title" VARCHAR(45) NOT NULL,
  "content" TEXT NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "published_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "author_id" UUID REFERENCES "User"("id") ON DELETE SET NULL
);

-- Category Table
CREATE TABLE IF NOT EXISTS "Category" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(45) NOT NULL UNIQUE,
  "description" TEXT
);

-- Price Table
CREATE TABLE IF NOT EXISTS "Price" (
  "id" SERIAL PRIMARY KEY,
  "price_per_hour" INTEGER NOT NULL,
  "price_per_day" INTEGER NOT NULL
);

-- Frame Material Enum
DROP TYPE IF EXISTS frame_material_enum CASCADE;
CREATE TYPE frame_material_enum AS ENUM ('Aluminum', 'Carbon', 'Steel', 'Titanium');

-- Brake Type Enum
DROP TYPE IF EXISTS brake_type_enum CASCADE;
CREATE TYPE brake_type_enum AS ENUM ('Disc', 'Rim', 'Hydraulic');

-- Bike Category Enum
DROP TYPE IF EXISTS bike_category_enum CASCADE;
CREATE TYPE bike_category_enum AS ENUM ('Mountain', 'Road', 'Hybrid', 'Electric');

-- Bike Model Table
CREATE TABLE IF NOT EXISTS "Bike" (
  "id" UUID PRIMARY KEY,
  "model" VARCHAR(45) NOT NULL,
  "frame_material" frame_material_enum NOT NULL,
  "brake_type" brake_type_enum NOT NULL,
  "brand" VARCHAR(45) NOT NULL,
  "description" TEXT,
  "Category_id" INTEGER NOT NULL REFERENCES "Category"("id") ON DELETE SET NULL,
  "Price_id" INTEGER NOT NULL REFERENCES "Price"("id") ON DELETE SET NULL
);

-- Size Enum
DROP TYPE IF EXISTS size_enum CASCADE;
CREATE TYPE size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');

-- Status Enum
DROP TYPE IF EXISTS status_enum CASCADE;
CREATE TYPE status_enum AS ENUM ('Available', 'Rented', 'Under_Repair', 'Out_of_Service');

-- Instance of Bike Table
CREATE TABLE IF NOT EXISTS "Instance_Bike" (
  "id" UUID PRIMARY KEY,
  "size" size_enum NOT NULL,
  "color" VARCHAR(45) NOT NULL,
  "purchase_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "last_service_at" TIMESTAMPTZ DEFAULT NOW(),
  "status" status_enum NOT NULL DEFAULT 'Available',
  "Bike_id" UUID NOT NULL REFERENCES "Bike"("id") ON DELETE SET NULL
);

-- Reservation Table
CREATE TABLE IF NOT EXISTS "Reservation" (
  "id" SERIAL PRIMARY KEY,
  "reservation_start" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "reservation_end" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "ready_to_pickup" BOOLEAN NOT NULL,
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "Instance_Bike_id" UUID NOT NULL REFERENCES "Instance_Bike"("id") ON DELETE SET NULL
);

-- Repair Table
CREATE TABLE IF NOT EXISTS "Repair" (
  "id" SERIAL PRIMARY KEY,
  "description" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "Instance_Bike_id" UUID NOT NULL REFERENCES "Instance_Bike"("id") ON DELETE SET NULL
);

-- Maintenance Table
CREATE TABLE IF NOT EXISTS "Maintenance" (
  "id" SERIAL PRIMARY KEY,
  "description" VARCHAR(255),
  "maintenance_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "Instance_Bike_id" UUID NOT NULL REFERENCES "Instance_Bike"("id") ON DELETE SET NULL
);

-- Review Table
CREATE TABLE IF NOT EXISTS "Review" (
  "id" SERIAL PRIMARY KEY,
  "rating" INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  "comment" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "published_at" TIMESTAMPTZ,
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE RESTRICT
);

-- Currency Enum
DROP TYPE IF EXISTS currency_enum CASCADE;
CREATE TYPE currency_enum AS ENUM ('EUR', 'CZK');

-- Payment Method Enum
DROP TYPE IF EXISTS payment_method_enum CASCADE;
CREATE TYPE payment_method_enum AS ENUM ('Online', 'On_Spot', 'Credit_Card', 'Debit_Card', 'Gift_Card', 'PayPal', 'Cash');

-- Payment Status Enum
DROP TYPE IF EXISTS payment_status_enum CASCADE;
CREATE TYPE payment_status_enum AS ENUM ('Pending', 'Completed', 'Failed', 'Refunded');

-- Payment Table
CREATE TABLE IF NOT EXISTS "Payment" (
  "id" SERIAL PRIMARY KEY,
  "amount" INTEGER NOT NULL,
  "payment_method" payment_method_enum NOT NULL,
  "payment_status" payment_status_enum NOT NULL DEFAULT 'Pending',
  "transaction_id" VARCHAR(100),
  "confirmation" TIMESTAMPTZ,
  "currency" currency_enum NOT NULL DEFAULT 'EUR',
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Statistics Table
CREATE TABLE IF NOT EXISTS "Statistics" (
  "id" SERIAL PRIMARY KEY,
  "report_period" TIMESTAMPTZ DEFAULT NOW(),
  "total_rentals" INTEGER,
  "total_income" INTEGER,
  "most_popular_bike" VARCHAR(45),
  "average_rental_duration" INTERVAL,
  "total_repairs" INTEGER
);

-- Rental Table
CREATE TABLE IF NOT EXISTS "Rental" (
  "id" SERIAL PRIMARY KEY,
  "start_time" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "end_time" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "total_price" INTEGER NOT NULL,
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "Payment_id" INTEGER NOT NULL REFERENCES "Payment"("id") ON DELETE SET NULL,
  "Instance_Bike_id" UUID NOT NULL REFERENCES "Instance_Bike"("id") ON DELETE SET NULL
);

-- Inspection Table
CREATE TABLE IF NOT EXISTS "Inspection" (
  "id" SERIAL PRIMARY KEY,
  "inspection_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "inspectioncol" VARCHAR(45) NOT NULL,
  "brakes_status" VARCHAR(45) NOT NULL,
  "tires_status" VARCHAR(45) NOT NULL,
  "frame_status" VARCHAR(45) NOT NULL,
  "overall_condition" VARCHAR(45) NOT NULL,
  "comments" VARCHAR(45),
  "User_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE SET NULL,
  "Rental_id" INTEGER NOT NULL REFERENCES "Rental"("id") ON DELETE SET NULL
);

-- Picture Table
CREATE TABLE IF NOT EXISTS "Picture" (
  "id" SERIAL PRIMARY KEY,
  "bike_picture_url" VARCHAR(255) NOT NULL,
  "picture_delete_hash" VARCHAR(255) NOT NULL,
  "description" VARCHAR(45),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "Instance_Bike_id" UUID NOT NULL REFERENCES "Instance_Bike"("id") ON DELETE SET NULL
);






-- Sample Data for Role Enum
INSERT INTO bikego."user" ("id", "username", "password_hash", "email", "phone_number", "created_at", "last_login", "profile_picture_url", "picture_delete_hash", "email_verified", "darkmode", "role")
VALUES
  ('c9a1d5d3-1111-4c65-8355-9d54c7e34321', 'admin_user', 'hash123', 'admin@example.com', '+1234567890', NOW(), NOW(), NULL, NULL, TRUE, FALSE, 'Admin'),
  ('c9a1d5d3-2222-4c65-8355-9d54c7e34321', 'employee_user', 'hash456', 'employee@example.com', '+1234567891', NOW(), NULL, NULL, NULL, TRUE, TRUE, 'Employee'),
  ('c9a1d5d3-3333-4c65-8355-9d54c7e34321', 'customer_user', 'hash789', 'customer@example.com', '+1234567892', NOW(), NULL, NULL, NULL, TRUE, FALSE, 'Customer');

-- Sample Data for News
INSERT INTO bikego."news" ("title", "content", "created_at", "published_at", "author_id")
VALUES
  ('New Mountain Bikes', 'Check out our latest mountain bikes!', NOW(), NOW(), 'c9a1d5d3-1111-4c65-8355-9d54c7e34321'),
  ('Repair Offers', 'Discounted repairs available this month!', NOW(), NOW(), 'c9a1d5d3-2222-4c65-8355-9d54c7e34321');

-- Sample Data for Category
INSERT INTO bikego."category" ("name", "description")
VALUES
  ('Mountain', 'Mountain bikes designed for rugged terrain.'),
  ('Road', 'Lightweight bikes optimized for paved roads.');

-- Sample Data for Price
INSERT INTO bikego."price" ("price_per_hour", "price_per_day")
VALUES
  (15, 100),
  (10, 70);

-- Sample Data for Bike
INSERT INTO bikego."bike" ("id", "model", "frame_material", "brake_type", "brand", "description", "Category_id", "Price_id")
VALUES
  ('9f33b8a2-5555-4c77-8b3c-f32b908c5a21', 'TrailBlazer', 'Carbon', 'Disc', 'Trek', 'Top-notch mountain bike.', 1, 1),
  ('9f33b8a2-6666-4c77-8b3c-f32b908c5a21', 'Speedster', 'Aluminum', 'Rim', 'Giant', 'Lightweight road bike.', 2, 2);

-- Sample Data for Instance_Bike
INSERT INTO bikego."instance_Bike" ("id", "size", "color", "purchase_date", "last_service_at", "status", "Bike_id")
VALUES
  ('7a83d8b3-7777-4d8a-9bfc-6b8c98d5e123', 'M', 'Red', NOW(), NOW(), 'Available', '9f33b8a2-5555-4c77-8b3c-f32b908c5a21'),
  ('7a83d8b3-8888-4d8a-9bfc-6b8c98d5e123', 'L', 'Blue', NOW(), NOW(), 'Rented', '9f33b8a2-6666-4c77-8b3c-f32b908c5a21');

-- Sample Data for Reservation
INSERT INTO bikego."reservation" ("reservation_start", "reservation_end", "ready_to_pickup", "User_id", "Instance_Bike_id")
VALUES
  (NOW(), NOW() + INTERVAL '1 day', TRUE, 'c9a1d5d3-3333-4c65-8355-9d54c7e34321', '7a83d8b3-7777-4d8a-9bfc-6b8c98d5e123');

-- Sample Data for Repair
INSERT INTO bikego."repair" ("description", "created_at", "User_id", "Instance_Bike_id")
VALUES
  ('Replaced brake pads.', NOW(), 'c9a1d5d3-2222-4c65-8355-9d54c7e34321', '7a83d8b3-8888-4d8a-9bfc-6b8c98d5e123');

-- Sample Data for Maintenance
INSERT INTO bikego."maintenance" ("description", "maintenance_date", "User_id", "Instance_Bike_id")
VALUES
  ('Lubricated chain and checked tires.', NOW(), 'c9a1d5d3-2222-4c65-8355-9d54c7e34321', '7a83d8b3-7777-4d8a-9bfc-6b8c98d5e123');

-- Sample Data for Review
INSERT INTO bikego."review" ("rating", "comment", "created_at", "published_at", "User_id")
VALUES
  (5, 'Fantastic bike! Highly recommend.', NOW(), NOW(), 'c9a1d5d3-3333-4c65-8355-9d54c7e34321');

-- Sample Data for Payment
INSERT INTO bikego."payment" ("amount", "payment_method", "payment_status", "transaction_id", "confirmation", "currency", "created_at")
VALUES
  (100, 'Credit_Card', 'Completed', 'TX12345', NOW(), 'EUR', NOW());

-- Sample Data for Rental
INSERT INTO bikego."rental" ("start_time", "end_time", "total_price", "User_id", "Payment_id", "Instance_Bike_id")
VALUES
  (NOW(), NOW() + INTERVAL '2 hours', 30, 'c9a1d5d3-3333-4c65-8355-9d54c7e34321', 1, '7a83d8b3-7777-4d8a-9bfc-6b8c98d5e123');

-- Sample Data for Picture
INSERT INTO bikego."picture" ("bike_picture_url", "picture_delete_hash", "description", "created_at", "Instance_Bike_id")
VALUES
  ('https://example.com/bike1.jpg', 'hashabc123', 'Mountain bike picture.', NOW(), '7a83d8b3-7777-4d8a-9bfc-6b8c98d5e123');
