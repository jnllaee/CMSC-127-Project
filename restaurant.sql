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
    average_rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    website VARCHAR(50) DEFAULT NULL,
    location VARCHAR (100) NOT NULL,
    PRIMARY KEY(establishment_id)
);

-- FOOD_ITEM(Item id, Name, Price, Average rating, Establishment id)
CREATE TABLE IF NOT EXISTS food_item(
    item_id INT(10) NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    price INT(5) NOT NULL,
    average_rating INT(2) NOT NULL DEFAULT 0,
    establishment_id INT(10) NOT NULL,
    PRIMARY KEY(item_id),
    FOREIGN KEY(establishment_id) REFERENCES food_establishment(establishment_id)
);

-- FOOD_ITEM_TYPE(Item id, Food type)
CREATE TABLE IF NOT EXISTS food_item_type(
    item_id INT(10) NOT NULL,
    food_type VARCHAR(50) NOT NULL,
    FOREIGN KEY(item_id) REFERENCES food_item(item_id)
);

-- FOOD_REVIEWS(Item id, Customer id, Date, Content, Rating)
CREATE TABLE IF NOT EXISTS food_reviews(
    food_reviews_id INT(10) NOT NULL AUTO_INCREMENT,
    item_id INT(10) NOT NULL,
    customer_id INT(10) NOT NULL,
    establishment_id INT(10) NOT NULL,
    date DATE NOT NULL,
    content VARCHAR(100) DEFAULT NULL,
    rating INT(2) NOT NULL DEFAULT 0,
    PRIMARY KEY(food_reviews_id),
    FOREIGN KEY(item_id) REFERENCES food_item(item_id),
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY(establishment_id) REFERENCES food_establishment(establishment_id)
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

-- Insertion of dummy data

INSERT INTO customer (customer_id, username, name) VALUES
(1, 'april_may', 'April May'),
(2, 'june_july', 'June July'),
(3, 'aug_sept', 'Aug Sept');

INSERT INTO food_establishment (establishment_id, name, contact_info, website, location) VALUES
(1, 'Burger Place', '0912-345-6789', 'www.burgerplace.com', '123 That Burger Place'),
(2, 'Sushi Place', '0998-765-4321', 'www.sushiplace.com', '456 Sushi Place Building'),
(3, 'Dumplings Place', '0956-789-1234', 'www.dumplingsplace.com', '789 Dumplings St., Place');

INSERT INTO food_item (item_id, name, price, average_rating, establishment_id) VALUES
(1, 'Cheeseburger', 75, 3, 1),
(2, 'California Maki', 105, 4, 2),
(3, 'Xiaolongbao', 70, 5, 3),
(4, 'Yumburger', 225, 5, 1),
(5, 'Torched Salmon Roll', 155, 4, 2),
(6, 'Gyoza', 170, 3, 3);

INSERT INTO food_item_type (item_id, food_type) VALUES
(1, 'Burgers'),
(2, 'Sushi'),
(3, 'Dumplings'),
(4, 'Meat'),
(5, 'Fish'),
(6, 'Vegetable');

INSERT INTO food_reviews (food_reviews_id, item_id, customer_id, establishment_id, date, content, rating) VALUES
(1, 1, 1, 1, '2023-01-06', 'yummy burger!', 3),
(2, 2, 2, 2, '2024-02-05', 'great sushi', 4),
(3, 3, 3, 3, '2023-03-04', 'the best xiaolongbao', 5),
(4, 4, 1, 1, '2022-04-03', 'best burger in town', 5),
(5, 5, 2, 2, '2024-05-02', 'delicious sushi', 3),
(6, 6, 3, 3, '2022-06-01', 'nice gyoza', 3);

INSERT INTO establishment_reviews (establishment_reviews_id, establishment_id, customer_id, date, content, rating) VALUES
(1, 1, 1, '2022-01-04', 'best resto', 5),
(2, 2, 2, '2023-02-05', 'great ambience', 4),
(3, 3, 3, '2024-03-06', 'classy yet comfy', 5);

UPDATE food_establishment AS e
SET e.average_rating = (
        SELECT AVG(er.rating)
        FROM establishment_reviews AS er
        WHERE er.establishment_id = e.establishment_id
);

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