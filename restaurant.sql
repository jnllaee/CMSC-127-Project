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
    average_rating DECIMAL(3,2) NOT NULL DEFAULT 0,
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
    average_rating DECIMAL(3,2) NOT NULL DEFAULT 0,
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
('bob_builder', 'Bob Builder'),
('charlie_brown', 'Charlie Brown');

-- Insert dummy data into FOOD_ESTABLISHMENT table
INSERT INTO food_establishment (name, contact_info, website, location) VALUES
('The Food Place', '123-456-7890', 'www.thefoodplace.com', '123 Main St'),
('Burger Haven', '234-567-8901', 'www.burgerhaven.com', '456 Elm St'),
('Pizza Paradise', '345-678-9012', 'www.pizzaparadise.com', '789 Oak St'),
('Taco Town', '456-789-0123', 'www.tacotown.com', '101 Pine St'),
('Pasta Palace', '567-890-1234', 'www.pastapalace.com', '202 Maple St');

-- Insert dummy data into FOOD_ITEM_TYPE table
INSERT INTO food_item_type (food_type) VALUES
('Burger'),
('Pizza'),
('Taco'),
('Pasta'),
('Salad');

-- Insert dummy data into FOOD_ITEM table
INSERT INTO food_item (name, price, establishment_id, food_type_id) VALUES
('Classic Burger', 10, 2, 1),
('Cheese Pizza', 12, 3, 2),
('Beef Taco', 8, 4, 3),
('Spaghetti Carbonara', 15, 5, 4),
('Caesar Salad', 7, 1, 5),
('Double Cheeseburger', 11, 2, 1),
('Pepperoni Pizza', 14, 3, 2),
('Chicken Taco', 9, 4, 3),
('Fettuccine Alfredo', 16, 5, 4),
('Greek Salad', 8, 1, 5),
('Bacon Burger', 12, 2, 1),
('Veggie Pizza', 13, 3, 2),
('Fish Taco', 10, 4, 3),
('Penne Arrabbiata', 14, 5, 4),
('Garden Salad', 7, 1, 5),
('Mushroom Swiss Burger', 13, 2, 1),
('Margherita Pizza', 15, 3, 2),
('Pork Taco', 9, 4, 3),
('Lasagna', 17, 5, 4),
('Cobb Salad', 9, 1, 5);

-- Insert dummy data into FOOD_REVIEWS table
INSERT INTO food_reviews (item_id, customer_id, date, content, rating) VALUES
(1, 1, '2023-05-01', 'Amazing burger, will come again!', 5),
(1, 2, '2023-05-02', 'Good but a bit too greasy.', 4),
(1, 3, '2023-05-03', 'Best burger in town!', 5),
(1, 4, '2023-05-04', 'Not bad, but I had better.', 3),
(1, 5, '2023-05-05', 'Loved the flavors!', 5),
(2, 1, '2023-05-06', 'Cheese Pizza was great!', 4),
(2, 2, '2023-05-07', 'A bit too salty.', 3),
(2, 3, '2023-05-08', 'Perfectly cheesy.', 5),
(2, 4, '2023-05-09', 'Would order again.', 4),
(2, 5, '2023-05-10', 'Tasty and crispy.', 5),
(3, 1, '2023-05-11', 'Tacos are delicious!', 4),
(3, 2, '2023-05-12', 'Too spicy for me.', 3),
(3, 3, '2023-05-13', 'Loved the beef filling.', 5),
(3, 4, '2023-05-14', 'Good portion size.', 4),
(3, 5, '2023-05-15', 'Very flavorful.', 5),
(4, 1, '2023-05-16', 'Best pasta I ever had.', 5),
(4, 2, '2023-05-17', 'Creamy and delicious.', 4),
(4, 3, '2023-05-18', 'A bit too rich for my taste.', 3),
(4, 4, '2023-05-19', 'Perfectly cooked pasta.', 5),
(4, 5, '2023-05-20', 'Would recommend to everyone.', 5),
(5, 1, '2023-05-21', 'Fresh and tasty.', 4),
(5, 2, '2023-05-22', 'Loved the dressing.', 5),
(5, 3, '2023-05-23', 'Crisp and fresh.', 4),
(5, 4, '2023-05-24', 'A bit too much dressing.', 3),
(5, 5, '2023-05-25', 'Perfect light meal.', 5),
(6, 1, '2023-05-26', 'Double Cheeseburger was amazing!', 5),
(6, 2, '2023-05-27', 'Could use more cheese.', 4),
(6, 3, '2023-05-28', 'Loved it, will order again.', 5),
(6, 4, '2023-05-29', 'Good but not great.', 3),
(6, 5, '2023-05-30', 'One of the best burgers I had.', 5),
(7, 1, '2023-05-31', 'Pepperoni Pizza was fantastic!', 5),
(7, 2, '2023-06-01', 'A bit too greasy.', 4),
(7, 3, '2023-06-02', 'Loved the pepperoni.', 5),
(7, 4, '2023-06-03', 'Good but could be better.', 3),
(7, 5, '2023-06-04', 'Will definitely order again.', 5),
(8, 1, '2023-06-05', 'Chicken Taco was great!', 4),
(8, 2, '2023-06-06', 'Loved the seasoning.', 5),
(8, 3, '2023-06-07', 'Good but a bit dry.', 3),
(8, 4, '2023-06-08', 'Perfectly cooked chicken.', 5),
(8, 5, '2023-06-09', 'Tasty and satisfying.', 4),
(9, 1, '2023-06-10', 'Fettuccine Alfredo was delicious!', 5),
(9, 2, '2023-06-11', 'Creamy and rich.', 4),
(9, 3, '2023-06-12', 'A bit too heavy for me.', 3),
(9, 4, '2023-06-13', 'Loved every bite.', 5),
(9, 5, '2023-06-14', 'Will definitely order again.', 5),
(10, 1, '2023-06-15', 'Greek Salad was fresh and tasty.', 4),
(10, 2, '2023-06-16', 'Loved the feta cheese.', 5),
(10, 3, '2023-06-17', 'Perfect mix of ingredients.', 4),
(10, 4, '2023-06-18', 'A bit too salty.', 3),
(10, 5, '2023-06-19', 'Very refreshing.', 5),
(11, 1, '2023-06-20', 'Bacon Burger was fantastic!', 5),
(11, 2, '2023-06-21', 'Loved the crispy bacon.', 5),
(11, 3, '2023-06-22', 'Good but a bit too greasy.', 3),
(11, 4, '2023-06-23', 'Nice flavors.', 4),
(11, 5, '2023-06-24', 'Will order again.', 5),
(12, 1, '2023-06-25', 'Veggie Pizza was very fresh.', 4),
(12, 2, '2023-06-26', 'Loved the toppings.', 5),
(12, 3, '2023-06-27', 'A bit too bland.', 3),
(12, 4, '2023-06-28', 'Healthy and tasty.', 4),
(12, 5, '2023-06-29', 'Will order again.', 5),
(13, 1, '2023-06-30', 'Fish Taco was delicious!', 5),
(13, 2, '2023-07-01', 'Loved the seasoning.', 4),
(13, 3, '2023-07-02', 'Fish was overcooked.', 3),
(13, 4, '2023-07-03', 'Perfectly spiced.', 5),
(13, 5, '2023-07-04', 'Would recommend to friends.', 4),
(14, 1, '2023-07-05', 'Penne Arrabbiata was spicy and delicious.', 5),
(14, 2, '2023-07-06', 'Loved the sauce.', 4),
(14, 3, '2023-07-07', 'A bit too spicy.', 3),
(14, 4, '2023-07-08', 'Perfectly cooked pasta.', 5),
(14, 5, '2023-07-09', 'Will order again.', 5),
(15, 1, '2023-07-10', 'Garden Salad was fresh.', 4),
(15, 2, '2023-07-11', 'Loved the variety of vegetables.', 5),
(15, 3, '2023-07-12', 'A bit too plain.', 3),
(15, 4, '2023-07-13', 'Healthy and tasty.', 4),
(15, 5, '2023-07-14', 'Will order again.', 5),
(16, 1, '2023-07-15', 'Mushroom Swiss Burger was delicious.', 5),
(16, 2, '2023-07-16', 'Loved the mushrooms.', 5),
(16, 3, '2023-07-17', 'A bit too greasy.', 3),
(16, 4, '2023-07-18', 'Nice flavors.', 4),
(16, 5, '2023-07-19', 'Will order again.', 5),
(17, 1, '2023-07-20', 'Margherita Pizza was amazing.', 5),
(17, 2, '2023-07-21', 'Loved the fresh ingredients.', 4),
(17, 3, '2023-07-22', 'A bit too cheesy.', 3),
(17, 4, '2023-07-23', 'Perfectly cooked.', 5),
(17, 5, '2023-07-24', 'Will order again.', 5),
(18, 1, '2023-07-25', 'Pork Taco was delicious.', 5),
(18, 2, '2023-07-26', 'Loved the seasoning.', 4),
(18, 3, '2023-07-27', 'A bit too dry.', 3),
(18, 4, '2023-07-28', 'Perfectly cooked.', 5),
(18, 5, '2023-07-29', 'Will order again.', 5),
(19, 1, '2023-07-30', 'Lasagna was amazing.', 5),
(19, 2, '2023-07-31', 'Loved the layers.', 4),
(19, 3, '2023-08-01', 'A bit too rich.', 3),
(19, 4, '2023-08-02', 'Perfectly cooked.', 5),
(19, 5, '2023-08-03', 'Will order again.', 5),
(20, 1, '2023-08-04', 'Cobb Salad was fresh.', 4),
(20, 2, '2023-08-05', 'Loved the variety of ingredients.', 5),
(20, 3, '2023-08-06', 'A bit too much dressing.', 3),
(20, 4, '2023-08-07', 'Healthy and tasty.', 4),
(20, 5, '2023-08-08', 'Will order again.', 5);

-- Insert dummy data into ESTABLISHMENT_REVIEWS table
INSERT INTO establishment_reviews (establishment_id, customer_id, date, content, rating) VALUES
(1, 1, '2023-05-01', 'Love the ambiance and food!', 5),
(1, 2, '2023-05-02', 'Great place for family dinners.', 4),
(1, 3, '2023-05-03', 'Nice location and good food.', 4),
(1, 4, '2023-05-04', 'Good service but a bit pricey.', 3),
(1, 5, '2023-05-05', 'Would definitely come back.', 5),
(2, 1, '2023-05-06', 'Best burger place in town.', 5),
(2, 2, '2023-05-07', 'Loved the variety of burgers.', 4),
(2, 3, '2023-05-08', 'Good food but slow service.', 3),
(2, 4, '2023-05-09', 'Great value for money.', 4),
(2, 5, '2023-05-10', 'Would recommend to friends.', 5),
(3, 1, '2023-05-11', 'Good pizza but slow service.', 3),
(3, 2, '2023-05-12', 'Pizza was excellent.', 5),
(3, 3, '2023-05-13', 'Nice atmosphere.', 4),
(3, 4, '2023-05-14', 'Could be better.', 3),
(3, 5, '2023-05-15', 'Would visit again.', 4),
(4, 1, '2023-05-16', 'Taco Town never disappoints.', 4),
(4, 2, '2023-05-17', 'Great tacos and service.', 5),
(4, 3, '2023-05-18', 'Loved the food.', 4),
(4, 4, '2023-05-19', 'Good value for money.', 4),
(4, 5, '2023-05-20', 'A bit crowded but worth it.', 5),
(5, 1, '2023-05-21', 'Best pasta dishes ever.', 5),
(5, 2, '2023-05-22', 'Loved the Italian vibe.', 5),
(5, 3, '2023-05-23', 'Great place for family dinners.', 4),
(5, 4, '2023-05-24', 'Delicious food and good service.', 5),
(5, 5, '2023-05-25', 'Highly recommend this place.', 5);

-- Update average ratings for food items
UPDATE food_item fi
JOIN (
    SELECT item_id, AVG(rating) AS avg_rating
    FROM food_reviews
    GROUP BY item_id
) fr ON fi.item_id = fr.item_id
SET fi.average_rating = fr.avg_rating;

-- Update average ratings for food establishments
UPDATE food_establishment fe
JOIN (
    SELECT establishment_id, AVG(rating) AS avg_rating
    FROM establishment_reviews
    GROUP BY establishment_id
) er ON fe.establishment_id = er.establishment_id
SET fe.average_rating = er.avg_rating;

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