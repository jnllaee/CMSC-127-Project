-- creation of user
CREATE OR REPLACE USER 'foodreviews'@'localhost' IDENTIFIED BY '127project';

-- Creation of database
DROP DATABASE IF EXISTS `restaurant`;
CREATE DATABASE IF NOT EXISTS `restaurant`;
GRANT ALL ON restaurant.* TO 'foodreviews'@'localhost';
USE `restaurant`;

-- Creation of tables

-- CUSTOMER(Customer id, Username, Name, Password)
CREATE TABLE IF NOT EXISTS customer(
    customer_id INT(10) NOT NULL AUTO_INCREMENT,
    username VARCHAR(40) NOT NULL,
    name VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY(customer_id)
);

-- FOOD_ESTABLISHMENT(Establishment id, Name, Contact info, Average rating, Website, Location)
CREATE TABLE IF NOT EXISTS food_establishment(
    establishment_id INT(10) NOT NULL AUTO_INCREMENT,
    name VARCHAR (40) NOT NULL,
    contact_info VARCHAR(50) DEFAULT NULL,
    average_rating INT(2) NOT NULL DEFAULT 0,
    website VARCHAR(50) DEFAULT NULL,
    location VARCHAR (100) NOT NULL,
    PRIMARY KEY(establishment_id)
);

-- FOOD_ITEM_TYPE(Food type id, Food type)
CREATE TABLE IF NOT EXISTS food_item_type(
    food_type_id INT(2) NOT NULL AUTO_INCREMENT,
    food_type VARCHAR(50) NOT NULL,
    PRIMARY KEY(food_type_id)
);

-- FOOD_ITEM(Item id, Name, Price, Average rating, Establishment id)
CREATE TABLE IF NOT EXISTS food_item(
    item_id INT(10) NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    price INT(5) NOT NULL,
    average_rating INT(2) NOT NULL DEFAULT 0,
    establishment_id INT(10) NOT NULL,
    food_type_id INT(2) NOT NULL,
    PRIMARY KEY(item_id),
    FOREIGN KEY(establishment_id) REFERENCES food_establishment(establishment_id),
    FOREIGN KEY(food_type_id) REFERENCES food_item_type(food_type_id)
);

-- FOOD_REVIEWS(Item id, Customer id, Date, Content, Rating)
CREATE TABLE IF NOT EXISTS food_reviews(
    food_reviews_id INT(10) NOT NULL AUTO_INCREMENT,
    item_id INT(10) NOT NULL,
    customer_id INT(10) NOT NULL,
    date DATE NOT NULL,
    content VARCHAR(100) DEFAULT NULL,
    rating INT(2) NOT NULL DEFAULT 0,
    PRIMARY KEY(food_reviews_id),
    FOREIGN KEY(item_id) REFERENCES food_item(item_id),
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);

-- ESTABLISHMENT_REVIEWS(Item id, Customer id, Date, Content, Rating)
CREATE TABLE IF NOT EXISTS establishment_reviews(
    establishment_reviews_id INT(10) NOT NULL AUTO_INCREMENT,
    establishment_id INT(10) NOT NULL,
    customer_id INT(10) NOT NULL,
    date DATE NOT NULL,
    content VARCHAR(100) DEFAULT NULL,
    rating INT(2) NOT NULL DEFAULT 0,
    PRIMARY KEY(establishment_reviews_id),
    FOREIGN KEY(establishment_id) REFERENCES food_establishment(establishment_id),
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);

-- Insert dummy data into CUSTOMER table
INSERT INTO customer (username, name) VALUES
('john_doe', 'John Doe'),
('jane_smith', 'Jane Smith'),
('alice_wonder', 'Alice Wonderland'),
('bob_builder', 'Bob Builder');

-- Insert dummy data into FOOD_ESTABLISHMENT table
INSERT INTO food_establishment (name, contact_info, average_rating, website, location) VALUES
('The Food Place', '123-456-7890', 4, 'www.thefoodplace.com', '123 Main St'),
('Burger Haven', '234-567-8901', 5, 'www.burgerhaven.com', '456 Elm St'),
('Pizza Paradise', '345-678-9012', 3, 'www.pizzaparadise.com', '789 Oak St'),
('Taco Town', '456-789-0123', 4, 'www.tacotown.com', '101 Pine St');

-- Insert dummy data into FOOD_ITEM_TYPE table
INSERT INTO food_item_type (food_type) VALUES
('Burger'),
('Pizza'),
('Taco'),
('Pasta');

-- Insert dummy data into FOOD_ITEM table
INSERT INTO food_item (name, price, average_rating, establishment_id, food_type_id) VALUES
('Classic Burger', 10, 5, 2, 1),
('Cheese Pizza', 12, 4, 3, 2),
('Beef Taco', 8, 4, 4, 3),
('Spaghetti Carbonara', 15, 5, 1, 4);

-- Insert dummy data into FOOD_REVIEWS table
INSERT INTO food_reviews (item_id, customer_id, date, content, rating) VALUES
(1, 1, '2023-05-01', 'Amazing burger, will come again!', 5),
(2, 2, '2023-05-02', 'Great pizza but a bit too salty.', 3),
(3, 3, '2023-05-03', 'Tacos are delicious!', 4),
(4, 4, '2023-05-04', 'Best pasta I ever had.', 5);

-- Insert dummy data into ESTABLISHMENT_REVIEWS table
INSERT INTO establishment_reviews (establishment_id, customer_id, date, content, rating) VALUES
(1, 1, '2023-05-01', 'Love the ambiance and food!', 5),
(2, 2, '2023-05-02', 'Best burger place in town.', 5),
(3, 3, '2023-05-03', 'Good pizza but slow service.', 3),
(4, 4, '2023-05-04', 'Taco Town never disappoints.', 4);

UPDATE food_item SET average_rating = (SELECT AVG(rating) FROM food_reviews WHERE food_reviews.item_id = food_item.item_id);

UPDATE food_establishment SET average_rating = (SELECT AVG(rating) FROM establishment_reviews WHERE establishment_reviews.establishment_id = food_establishment.establishment_id);

-- Features

-- Add, update, and delete a food review

-- INSERT INTO food_reviews (item_id, customer_id, establishment_id, date, content, rating) VALUES
-- (4, 1, 1, '2023-07-03', 'lacks ketchup', 3);

-- UPDATE food_reviews SET rating = 5 WHERE item_id = 3;

-- DELETE FROM food_reviews WHERE customer_id = 3;

-- -- Add, delete, search, and update a food establishment

-- INSERT INTO food_establishment (establishment_id, name, contact_info, average_rating, website, location) VALUES
-- (4, 'Papas Pizzeria', '0909-909-0909', 4, 'www.papaspizzeria.com', '101 That Building');

-- DELETE FROM food_establishment WHERE establishment_id = 4;

-- SELECT
--     name AS "Food Establishment Name",
--     contact_info AS "Contact Information",
--     average_rating AS "Average Rating",
--     website AS "Website",
--     location AS "Location",
-- FROM food_establishment;

-- UPDATE food_establishment SET average_rating = 3 WHERE average_rating = 4;

-- -- Add, delete, search, and update a food item

-- INSERT INTO food_item (item_id, name, price, average_rating, establishment_id) VALUES
-- (7, 'Pizza', 100, 4, 4);

-- DELETE FROM food_item WHERE average_rating < 3;

-- SELECT
--     name AS "Food Name",
--     price AS "Price",
--     average_rating AS "Average Rating",
-- FROM food_item;

-- -- Reports to be generated

-- -- View all food establishments
-- SELECT * FROM food_establishment;

-- -- View food reviews for an establishment or a food item
-- SELECT * FROM food_reviews;
-- SELECT * FROM establishment_reviews;

-- -- View all food items from an establishment
-- SELECT fi.* FROM food_item fi
-- JOIN food_establishment fe
-- ON fi.establishment_id = fe.establishment_id;

-- -- View all food items from an establishment that belong to a food type
-- SELECT fi.* FROM food_item fi
-- JOIN food_item_type fit
-- ON fi.item_id = fit.item_id
-- WHERE fi.establishment_id = (SELECT establishment_id e FROM food_establishment fe)
-- AND fit.food_type IS NOT NULL;

-- -- View all reviews made within a month for an establishment or a food item

-- SELECT * FROM food_reviews
-- WHERE DATE_FORMAT(date, '%Y-%m') = DATE_FORMAT(CURRENT_DATE(), '%Y-%m');

-- -- View all establishments with a high average rating (rating >= 4)
-- -- Ratings from 1-5, highest is 5
-- SELECT * FROM food_establishment
-- WHERE average_rating >= 4;

-- -- View all food items from an establishment arranged according to price
-- SELECT * FROM food_item
-- WHERE establishment_id = 3
-- ORDER BY price ASC;


-- -- Search food items from any establishment based on a given price range and/or food type
-- SELECT fi.*
-- FROM food_item fi
-- JOIN food_item_type fit ON fi.item_id = fit.item_id
-- JOIN food_establishment fe ON fi.establishment_id = fe.establishment_id
-- WHERE fi.price BETWEEN (
--         SELECT MIN(price) FROM food_item WHERE establishment_id = 2
--     ) AND (
--         SELECT MAX(price) FROM food_item WHERE establishment_id = 2
--     )
-- AND (fit.food_type = 'Burgers');