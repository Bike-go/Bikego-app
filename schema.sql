-- Schema and Search Path Setup
CREATE SCHEMA IF NOT EXISTS {{db_schema_name}};
SET search_path TO {{db_schema_name}};

-- Role Enum
DROP TYPE IF EXISTS role_enum CASCADE;
CREATE TYPE role_enum AS ENUM ('Admin', 'Employee', 'Customer', 'Service');

-- User Table
CREATE TABLE IF NOT EXISTS "user" (
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
CREATE TABLE IF NOT EXISTS "news" (
  "id" SERIAL PRIMARY KEY,
  "title" VARCHAR(45) NOT NULL,
  "content" TEXT NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "published_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "author_id" UUID REFERENCES "user"("id") ON DELETE SET NULL
);

-- Category Table
CREATE TABLE IF NOT EXISTS "category" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR(45) NOT NULL UNIQUE,
  "description" TEXT
);

-- Price Table
CREATE TABLE IF NOT EXISTS "price" (
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
CREATE TABLE IF NOT EXISTS "bike" (
  "id" UUID PRIMARY KEY,
  "model" VARCHAR(45) NOT NULL,
  "frame_material" frame_material_enum NOT NULL,
  "brake_type" brake_type_enum NOT NULL,
  "brand" VARCHAR(45) NOT NULL,
  "description" TEXT,
  "category_id" INTEGER NOT NULL REFERENCES "category"("id") ON DELETE SET NULL,
  "price_id" INTEGER NOT NULL REFERENCES "price"("id") ON DELETE SET NULL
);

-- Size Enum
DROP TYPE IF EXISTS size_enum CASCADE;
CREATE TYPE size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');

-- Status Enum
DROP TYPE IF EXISTS status_enum CASCADE;
CREATE TYPE status_enum AS ENUM ('Available', 'Rented', 'Under_Repair', 'Out_of_Service');

-- Instance of Bike Table
CREATE TABLE IF NOT EXISTS "instance_bike" (
  "id" UUID PRIMARY KEY,
  "size" size_enum NOT NULL,
  "color" VARCHAR(45) NOT NULL,
  "purchase_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "last_service_at" TIMESTAMPTZ DEFAULT NOW(),
  "status" status_enum NOT NULL DEFAULT 'Available',
  "bike_id" UUID NOT NULL REFERENCES "bike"("id") ON DELETE SET NULL
);

-- Reservation Table
CREATE TABLE IF NOT EXISTS "reservation" (
  "id" SERIAL PRIMARY KEY,
  "reservation_start" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "reservation_end" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "ready_to_pickup" BOOLEAN NOT NULL,
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE SET NULL,
  "instance_bike_id" UUID NOT NULL REFERENCES "instance_bike"("id") ON DELETE SET NULL
);

-- Review Table
CREATE TABLE IF NOT EXISTS "review" (
  "id" SERIAL PRIMARY KEY,
  "rating" INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  "comment" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "published_at" TIMESTAMPTZ,
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE RESTRICT
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
CREATE TABLE IF NOT EXISTS "payment" (
  "id" SERIAL PRIMARY KEY,
  "amount" INTEGER NOT NULL,
  "payment_method" payment_method_enum NOT NULL,
  "payment_status" payment_status_enum NOT NULL DEFAULT 'Pending',
  "transaction_id" VARCHAR(100),
  "confirmation" TIMESTAMPTZ,
  "currency" currency_enum NOT NULL DEFAULT 'EUR',
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Rental Table
CREATE TABLE IF NOT EXISTS "rental" (
  "id" SERIAL PRIMARY KEY,
  "start_time" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "end_time" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "total_price" INTEGER NOT NULL,
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE SET NULL,
  "payment_id" INTEGER REFERENCES "payment"("id") ON DELETE SET NULL,
  "instance_bike_id" UUID NOT NULL REFERENCES "instance_bike"("id") ON DELETE SET NULL
);

-- Inspection Table
CREATE TABLE IF NOT EXISTS "inspection" (
  "id" SERIAL PRIMARY KEY,
  "inspection_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "comments" VARCHAR(45),
  "finished" BOOLEAN NOT NULL DEFAULT FALSE,
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE SET NULL,
  "rental_id" INTEGER NOT NULL REFERENCES "rental"("id") ON DELETE SET NULL
);

-- Repair Table
CREATE TABLE IF NOT EXISTS "repair" (
  "id" SERIAL PRIMARY KEY,
  "description" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE SET NULL,
  "inspection_id" INTEGER NOT NULL REFERENCES "inspection"("id") ON DELETE SET NULL
);

-- Maintenance Table
CREATE TABLE IF NOT EXISTS "maintenance" (
  "id" SERIAL PRIMARY KEY,
  "description" VARCHAR(255),
  "maintenance_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "user_id" UUID NOT NULL REFERENCES "user"("id") ON DELETE SET NULL,
  "inspection_id" INTEGER NOT NULL REFERENCES "inspection"("id") ON DELETE SET NULL
);

-- Picture Table
CREATE TABLE IF NOT EXISTS "picture" (
  "id" SERIAL PRIMARY KEY,
  "bike_picture_url" VARCHAR(255) NOT NULL,
  "picture_delete_hash" VARCHAR(255) NOT NULL,
  "description" VARCHAR(45),
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "instance_bike_id" UUID NOT NULL REFERENCES "instance_bike"("id") ON DELETE SET NULL
);