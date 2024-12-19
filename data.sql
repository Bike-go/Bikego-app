-- Sample Data for Role Enum
INSERT INTO bikego."user" ("id", "username", "password_hash", "email", "phone_number", "created_at", "last_login", "profile_picture_url", "picture_delete_hash", "email_verified", "darkmode", "role")
VALUES
  ('c9a1d5d3-1111-4c65-8355-9d54c7e34321', 'admin_user', 'scrypt:32768:8:1$omao1ZekoCsmuR1x$a6e176f471174109b2b7289c8cdabb6f29e42cd98ebe74c4ad94a3f32171026dbfc53c25e178dde5a3c964cbb9c09d696005660c239a3df3a003de198ed68db2', 'admin@example.com', '+1234567890', NOW(), NOW(), NULL, NULL, TRUE, FALSE, 'Admin'),
  ('c9a1d5d3-2222-4c65-8355-9d54c7e34321', 'employee_user', 'scrypt:32768:8:1$omao1ZekoCsmuR1x$a6e176f471174109b2b7289c8cdabb6f29e42cd98ebe74c4ad94a3f32171026dbfc53c25e178dde5a3c964cbb9c09d696005660c239a3df3a003de198ed68db2', 'employee@example.com', '+1234567891', NOW(), NULL, NULL, NULL, TRUE, TRUE, 'Employee'),
  ('c9a1d5d3-3333-4c65-8355-9d54c7e34321', 'customer_user', 'scrypt:32768:8:1$omao1ZekoCsmuR1x$a6e176f471174109b2b7289c8cdabb6f29e42cd98ebe74c4ad94a3f32171026dbfc53c25e178dde5a3c964cbb9c09d696005660c239a3df3a003de198ed68db2', 'customer@example.com', '+1234567892', NOW(), NULL, NULL, NULL, TRUE, FALSE, 'Customer');

-- Sample Data for News
INSERT INTO bikego."news" ("title", "content", "created_at", "published_at", "author_id")
VALUES
  ('New Mountain Bikes', '🥳Check out our latest mountain bikes!', NOW(), NOW(), 'c9a1d5d3-1111-4c65-8355-9d54c7e34321'),
  ('Repair Offers', '🤩Discounted repairs available this month!', NOW(), NOW(), 'c9a1d5d3-2222-4c65-8355-9d54c7e34321');

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