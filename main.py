import tkinter as tk
from tkinter import ttk, messagebox
import mariadb

# Establish database connection
def connect_db():
    try:
        conn = mariadb.connect(
            user="foodreviews",
            password="127project",
            host="localhost",
            database="restaurant"
        )
        return conn
    except mariadb.Error as e:
        messagebox.showerror("Database Connection Error", f"Error connecting to MariaDB: {e}")
        return None

# Fetch all restaurants from the database
def fetch_restaurants():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food_establishment")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all food items of the selected restaurant from the database
def fetch_food_items(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        if establishment_id:
            cursor.execute(
                """
                SELECT fi.item_id, fe.name, fi.name, fit.food_type, fi.price, fi.average_rating
                FROM food_item fi
                NATURAL JOIN food_item_type fit
                JOIN food_establishment fe ON fi.establishment_id = fe.establishment_id
                WHERE fi.establishment_id = ?
                """, (establishment_id,)
            )
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all food items from the database
def fetch_all_food_items():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fe.name, fi.name, fit.food_type, fi.price, fi.average_rating FROM food_item fi NATURAL JOIN food_item_type fit JOIN food_establishment fe ON fi.establishment_id = fe.establishment_id ORDER BY fi.item_id")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch food item types from the database
def fetch_food_item_types():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT food_type FROM food_item_type ORDER BY food_type")
        food_type_options = cursor.fetchall()
        food_type_options = [option[0] for option in food_type_options]
        food_type_options.append("None")
        conn.close()
        return food_type_options
    return []

# Fetch all restaurant reviews for a restaurant from the database
def fetch_restaurant_reviews(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT r.establishment_reviews_id, c.username, r.content, r.rating, r.date FROM customer c NATURAL JOIN establishment_reviews r WHERE r.establishment_id = ?", (establishment_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all restaurant reviews from the database
def fetch_all_restaurant_reviews():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fe.name, c.username, r.content, r.rating, r.date FROM customer c NATURAL JOIN establishment_reviews r JOIN food_establishment fe ON r.establishment_id = fe.establishment_id")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all food reviews for a specific food item from the database
def fetch_food_reviews(item_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT fr.food_reviews_id, fi.name, c.username, fr.content, fr.rating, fr.date
            FROM customer c 
            RIGHT JOIN food_reviews fr 
            ON c.customer_id=fr.customer_id 
            LEFT JOIN food_item fi 
            ON fr.item_id = fi.item_id 
            WHERE fr.item_id=?""", (item_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all food item reviews from the database
def fetch_all_food_reviews():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fi.name, c.username, fr.content, fr.rating, fr.date FROM customer c NATURAL JOIN food_reviews fr JOIN food_item fi ON fr.item_id=fi.item_id ORDER BY c.username")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Initialize main window
def init_main_window():
    # Function to search and sort restaurants
    def search_sort_restaurants():
        # Fetch all inputs from the user
        query = entry_search.get().lower()
        rating_filter = rating_var.get()
        sort_option = sort_var.get()
        sortdir_option = sortdir_var.get()
        
        min_rating = 1
        if rating_filter == "5 Stars":
            min_rating = 5
        elif rating_filter == "4 Stars and Up":
            min_rating = 4
        elif rating_filter == "3 Stars and Up":
            min_rating = 3
        elif rating_filter == "2 Stars and Up":
            min_rating = 2
        elif rating_filter == "None":
            min_rating = 0
        
        # Query for search and sort
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            base_query = ""
            query_params = ()

            if min_rating > 1:
                base_query = "SELECT * FROM food_establishment WHERE average_rating >= ?"
            elif min_rating == 1:
                base_query = "SELECT * FROM food_establishment WHERE average_rating = ?"
            else:
                base_query = "SELECT * FROM food_establishment WHERE"
            
            if min_rating == 0:
                if query:
                    base_query += " LOWER(name) LIKE ?"
                    query_params = (f"%{query}%",)
                else:
                    base_query = "SELECT * FROM food_establishment"
            else:
                if query:
                    base_query += " AND LOWER(name) LIKE ?"
                    query_params = (min_rating, f"%{query}%")
                else:
                    query_params = (min_rating,)
            
            if sort_option == "Name":
                base_query += " ORDER BY name"
            elif sort_option == "Average Rating":
                base_query += " ORDER BY average_rating"
            
            if sortdir_option.lower() == "descending":
                base_query += " DESC"
            
            cursor.execute(base_query, query_params)
            rows = cursor.fetchall()
            conn.close()
            
            update_table(rows)
    
    # Function to add restaurant review (1)
    def add_restaurant_review():
        # Function to handle submission of restaurant details
        def submit_customer_restaurant():
            # Fetch inputs from user
            username = entry_username.get().strip()
            name = entry_name.get().strip()
            
            # Check if the username field is empty
            if not username and not name:
                messagebox.showerror("Error", "Please enter the customer username and name properly")
                return
            
            # Query to add a restaurant review
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT customer_id, name FROM customer WHERE username = ?",
                (username,))
                existing_customer = cursor.fetchone()               
                if existing_customer:
                    if existing_customer[1] == name:
                        customer_id = existing_customer[0]
                        messagebox.showinfo("Success", "Customer found. Welcome back!")
                        conn.close()
                        customer_popup.destroy()
                        open_review_popup(customer_id)
                    else:
                        messagebox.showerror("Error", "Username already in use!")
                        return
                else:
                    cursor.execute("INSERT INTO customer (username, name) VALUES (?, ?)",
                                (username, name))
                    conn.commit()
                    customer_id = cursor.lastrowid
                    messagebox.showinfo("Success", "Customer added successfully")
                    conn.close()
                    customer_popup.destroy()
                    open_review_popup(customer_id)
                
        # Create pop-up window
        customer_popup = tk.Toplevel(root)
        customer_popup.title("Add Customer")
        customer_popup.configure(background="#FFF2DC")

        # Add necessary fields
        ttk.Label(customer_popup, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        entry_username = ttk.Entry(customer_popup)
        entry_username.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(customer_popup, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        entry_name = ttk.Entry(customer_popup)
        entry_name.grid(row=1, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(customer_popup, text="Submit", command=submit_customer_restaurant)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        customer_popup.geometry("300x250")
        customer_popup.mainloop()
        
    # Function to add restaurant
    def add_restaurant():
        # Function to handle submission of restaurant details
        def submit_restaurant():
            # Fetch user inputs
            name = entry_name.get().strip()
            contact_info = entry_contact_info.get().strip()
            website = entry_website.get().strip()
            location = entry_location.get().strip()

            # Check if the name field is empty
            if not name:
                messagebox.showerror("Error", "Please enter the restaurant name")
                return

            # Insert restaurant into the database
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO food_establishment (name, contact_info, website, location, average_rating) VALUES (?, ?, ?, ?, ?)",
                (name, contact_info, website, location, 0))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Restaurant added successfully")
                popup.destroy()

        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("Add Restaurant")
        popup.configure(background="#FFF2DC")

        # Necessary fields
        ttk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        entry_name = ttk.Entry(popup)
        entry_name.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(popup, text="Contact Info:").grid(row=1, column=0, padx=5, pady=5)
        entry_contact_info = ttk.Entry(popup)
        entry_contact_info.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(popup, text="Website:").grid(row=3, column=0, padx=5, pady=5)
        entry_website = ttk.Entry(popup)
        entry_website.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(popup, text="Location:").grid(row=4, column=0, padx=5, pady=5)
        entry_location = ttk.Entry(popup)
        entry_location.grid(row=4, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(popup, text="Submit", command=submit_restaurant)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        popup.geometry("300x250")
        popup.mainloop()
    
    # Function to add restaurant review (2)
    def open_review_popup(customer_id):
        def submit_review():
            if not tree.selection():
                messagebox.showerror("Error", "Please select a restaurant")
                return
            
            # Fetch user inputs
            content = entry_content.get().strip()
            rating = entry_rating.get().strip()
            
            # Check if the username field is empty
            if not content or not rating:
                messagebox.showerror("Error", "Please enter both fields correctly")
                return
            
            establishment_id = tree.item(tree.selection()[0], "values")[0]       
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO establishment_reviews (establishment_id, customer_id, content, rating, date) VALUES (?, ?, ?, ?, CURDATE())",
                (establishment_id, customer_id, content, rating))
                cursor.execute("SELECT AVG(rating) FROM establishment_reviews WHERE establishment_id=?", 
                               (establishment_id,))
                average_rating = cursor.fetchone()[0]
                
                cursor.execute("UPDATE food_establishment SET average_rating=? WHERE establishment_id=?", 
                               (average_rating, establishment_id))
                conn.commit()
                messagebox.showinfo("Success", "Restaurant review added successfully")
                conn.close()
                review_popup.destroy()
                
                reviews = fetch_restaurant_reviews(establishment_id)
                update_restaurant_reviews_table(reviews)
                restaurants = fetch_restaurants()
                update_table(restaurants)
                
        # Create pop-up window
        review_popup = tk.Toplevel(root)
        review_popup.title("Add Review")
        review_popup.configure(background="#FFF2DC")

        # Necessary fields
        ttk.Label(review_popup, text="Content:").grid(row=0, column=0, padx=5, pady=5)
        entry_content = ttk.Entry(review_popup)
        entry_content.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(review_popup, text="Rating:").grid(row=1, column=0, padx=5, pady=5)
        entry_rating = ttk.Entry(review_popup)
        entry_rating.grid(row=1, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(review_popup, text="Submit", command=submit_review)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        review_popup.geometry("300x250")
        review_popup.mainloop()
    
    # Function to edit restaurant
    def edit_restaurant():
        if not selected_restaurant_id:
            messagebox.showerror("Error", "No restaurant selected for editing")
            return
        
        # Function to handle submission of edited restaurant details
        def submit_restaurant():
            # Fetch user inputs
            name = entry_name.get().strip()
            contact_info = entry_contact_info.get().strip()
            website = entry_website.get().strip()
            location = entry_location.get().strip()

            # Check if the name field is empty
            if not name:
                messagebox.showerror("Error", "Please enter the restaurant name")
                return

            # Update restaurant details in the database
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE food_establishment SET name=?, contact_info=?, website=?, location=? WHERE establishment_id=?",
                            (name, contact_info, website, location, selected_restaurant_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Restaurant updated successfully")
                popup.destroy()

                #UPDATE TABLE
                restaurants = fetch_restaurants()
                update_table(restaurants)

        # Function to handle deletion of restaurant
        def delete_restaurant():
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this restaurant?")
            if response:
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()

                    # Delete food reviews of all food items of the restaurant
                    cursor.execute("SELECT item_id FROM food_item WHERE establishment_id=?", (selected_restaurant_id,))
                    food_items = cursor.fetchall()
                    for food_item in food_items:
                        cursor.execute("DELETE FROM food_reviews WHERE item_id=?", (food_item[0],))

                    # Delete food items of the restaurant
                    cursor.execute("DELETE FROM food_item WHERE establishment_id=?", (selected_restaurant_id,))
                    
                    # Delete restaurant reviews
                    cursor.execute("DELETE FROM establishment_reviews WHERE establishment_id=?", (selected_restaurant_id,))
                    
                    # Delete the restaurant
                    cursor.execute("DELETE FROM food_establishment WHERE establishment_id=?", (selected_restaurant_id,))
                    
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Restaurant deleted successfully")
                    popup.destroy()
                    restaurants = fetch_restaurants()
                    update_table(restaurants)

        # Fetch current restaurant details
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, contact_info, website, location FROM food_establishment WHERE establishment_id=?", (selected_restaurant_id,))
            restaurant = cursor.fetchone()
            conn.close()
        if not restaurant:
            messagebox.showerror("Error", "Restaurant not found")
            return

        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("Edit Restaurant")
        popup.configure(background="#FFF2DC")

        # Design the UI
        ttk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        entry_name = ttk.Entry(popup)
        entry_name.grid(row=0, column=1, padx=5, pady=5)
        entry_name.insert(0, restaurant[0])

        ttk.Label(popup, text="Contact Info:").grid(row=1, column=0, padx=5, pady=5)
        entry_contact_info = ttk.Entry(popup)
        entry_contact_info.grid(row=1, column=1, padx=5, pady=5)
        entry_contact_info.insert(0, restaurant[1])

        ttk.Label(popup, text="Website:").grid(row=3, column=0, padx=5, pady=5)
        entry_website = ttk.Entry(popup)
        entry_website.grid(row=3, column=1, padx=5, pady=5)
        entry_website.insert(0, restaurant[2])

        ttk.Label(popup, text="Location:").grid(row=4, column=0, padx=5, pady=5)
        entry_location = ttk.Entry(popup)
        entry_location.grid(row=4, column=1, padx=5, pady=5)
        entry_location.insert(0, restaurant[3])

        # Add submit button
        btn_submit = ttk.Button(popup, text="Submit", command=submit_restaurant)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Add delete button
        btn_delete = ttk.Button(popup, text="Delete", command=delete_restaurant)
        btn_delete.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        popup.geometry("")
        popup.mainloop()

    # Function to search and sort food items of a restaurant
    def search_sort_food_items():
        # Fetch user input
        query = entry_food_item_search.get().lower()
        food_type_filter = food_type_var.get()
        sort_option = sort_food_item_var.get()
        price_range_min = pricerange_min.get()
        price_range_max = pricerange_max.get()
        sortdir_option = sortdir_food_item_var.get()
        
        # Query for search and sort
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            base_query = """
                SELECT fi.item_id, fe.name, fi.name, fi.price, fit.food_type, fi.average_rating
                FROM food_item fi
                NATURAL JOIN food_item_type fit
                JOIN food_establishment fe ON fi.establishment_id = fe.establishment_id
            """            
            query_params = []
            conditions = []

            conditions.append("fi.establishment_id = ?")
            query_params.append(selected_restaurant_id)
                    
            if query:
                conditions.append("LOWER(fi.name) LIKE ?")
                query_params.append(f"%{query}%")
                    
            if food_type_filter != "None":
                conditions.append("fit.food_type LIKE ?")
                query_params.append(f"%{food_type_filter}%")
                    
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            if price_range_min or price_range_max:
                base_query += " AND fi.price BETWEEN ? AND ?"
                query_params.append(int(price_range_min))
                query_params.append(int(price_range_max))
                    
            if sort_option == "Price":
                base_query += " ORDER BY fi.price"
            elif sort_option == "Name":
                base_query += " ORDER BY fi.name"
            else:
                base_query += " ORDER BY fi.item_id"
                    
            if sortdir_option.lower() == "descending":
                base_query += " DESC"

            cursor.execute(base_query, query_params)
            rows = cursor.fetchall()
            conn.close()
            
            update_food_items_table(rows)

    # Function to add a food item to a restaurant
    def add_food_item():
        # Function for the submit button
        def submit_food_item():
            food_item_name = entry_name.get().strip()
            food_item_type = entry_food_type.get().strip()
            food_item_price = entry_price.get().strip()
            food_item_types = fetch_food_item_types()

            conn = connect_db()
            if conn:
                cursor = conn.cursor()

                # Check if the name field is empty
                if not food_item_name:
                    messagebox.showerror("Invalid Input", "Please enter the food item name")
                    conn.close()
                    return

                # Check if the food item already exists in the restaurant
                cursor.execute("SELECT name FROM food_item WHERE establishment_id=?", (selected_restaurant_id,))
                all_food_items = cursor.fetchall()
                existing_food_items = [item[0] for item in all_food_items]
                if food_item_name in existing_food_items:
                    messagebox.showinfo("Warning", "Food item already existing in restaurant")
                    conn.close()
                    return
                
                # If food item type doesn't exist, add it to the database
                if food_item_type not in food_item_types:
                    cursor.execute("INSERT INTO food_item_type(food_type) VALUES (?)", (food_item_type,))
                    conn.commit()

                # Get the food type id
                cursor.execute("SELECT food_type_id FROM food_item_type WHERE food_type=?", (food_item_type,))
                food_type_id = cursor.fetchone()[0]

                # Insert the food item into the database
                cursor.execute("INSERT INTO food_item(name, price, establishment_id, food_type_id, average_rating) VALUES (?, ?, ?, ?, ?)",
                            (food_item_name, food_item_price, selected_restaurant_id, food_type_id, 0))
                
                
            
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Food item added successfully")
                popup.destroy()

        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("Add Food Item to Restaurant")
        popup.configure(background="#FFF2DC")

        # Design the UI
        ttk.Label(popup, text="Food Item Name:").grid(row=0, column=0, padx=5, pady=5)
        entry_name = ttk.Entry(popup)
        entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Food Type:").grid(row=1, column=0, padx=5, pady=5)
        entry_food_type = ttk.Entry(popup)
        entry_food_type.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Price:").grid(row=3, column=0, padx=5, pady=5)
        entry_price = ttk.Entry(popup)
        entry_price.grid(row=3, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(popup, text="Submit", command=submit_food_item)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
    
    # Function to edit a food item of a restaurant
    def edit_food_item(event):
        # Function for the submit button
        def submit_food_item():
            food_item_name = entry_food_name.get().strip()
            food_item_type = entry_food_type.get().strip()
            food_item_price = entry_price.get().strip()
            food_item_types = fetch_food_item_types()

            conn = connect_db()
            if conn:
                cursor = conn.cursor()

                # Check if the name field is empty
                if not food_item_name:
                    messagebox.showerror("Invalid Input", "Please enter the food item name")
                    conn.close()
                    return

                # If food item type doesn't exist, add it to the database
                if food_item_type not in food_item_types:
                    cursor.execute("INSERT INTO food_item_type(food_type) VALUES (?)", (food_item_type,))

                # Get the food type id
                cursor.execute("SELECT food_type_id FROM food_item_type WHERE food_type=?", (food_item_type,))
                food_type_id = cursor.fetchone()[0]

                # Insert the food item into the database
                cursor.execute("UPDATE food_item SET name=?, price=?, food_type_id=? WHERE item_id=?",
                            (food_item_name, food_item_price, food_type_id, selected_food_item_id))
                
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Food item updated successfully")
                popup.destroy()

        # Function to delete a food item
        def delete_food_item():
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this food item?")
            if response:
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM food_reviews WHERE item_id=?", (selected_food_item_id,))
                    cursor.execute("DELETE FROM food_item WHERE item_id=?", (selected_food_item_id,))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Food item successfully deleted")
                    popup.destroy()
    
        food_item = food_items_tree.selection()
        selected_food_item_id = food_items_tree.item(food_item, "values")[0]

        # Fetch current food item details
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fi.name, fi.price, fit.food_type FROM food_item fi NATURAL JOIN food_item_type fit WHERE fi.item_id=? AND fi.establishment_id=?", (selected_food_item_id, selected_restaurant_id))
            food_item = cursor.fetchone()
            conn.close()

        if not selected_food_item_id:
            messagebox.showerror("Error", "Food item not found")
            return

        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("Food Item Details")
        popup.configure(background="#FFF2DC")

        ttk.Label(popup, text="Food Name:").grid(row=0, column=0, padx=5, pady=5)
        entry_food_name = ttk.Entry(popup)
        entry_food_name.grid(row=0, column=1, padx=5, pady=5)
        entry_food_name.insert(0, food_item[0])

        ttk.Label(popup, text="Price:").grid(row=1, column=0, padx=5, pady=5)
        entry_price = ttk.Entry(popup)
        entry_price.grid(row=1, column=1, padx=5, pady=5)
        entry_price.insert(1, food_item[1])

        ttk.Label(popup, text="Food Type:").grid(row=2, column=0, padx=5, pady=5)
        entry_food_type = ttk.Entry(popup)
        entry_food_type.grid(row=2, column=1, padx=5, pady=5)
        entry_food_type.insert(2, food_item[2])

        btn_delete = ttk.Button(popup, text="Delete Food Item", command=delete_food_item)
        btn_delete.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        btn_edit = ttk.Button(popup, text="Submit", command=submit_food_item)
        btn_edit.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        popup.geometry("")
        popup.mainloop()

    # Function to search and sort restaurant reviews
    def search_sort_estreviews():
        month_to_num = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12,
            "None": 0
        }
        
        # Fetch user inputs
        query = reviews_search.get().lower()
        month_filter = review_month_var.get()
        nummonth_filter = 0
        if (month_filter != "None"):
            nummonth_filter = month_to_num.get(month_filter)
        year_filter = reviews_year.get()
        sort_option = sort_reviews_var.get()
        sortdir_option = sortdir_reviews_var.get()
        
        # Query for search and sort
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            base_query = "SELECT rr.establishment_reviews_id, c.username, rr.content, rr.rating, rr.date FROM establishment_reviews rr NATURAL JOIN customer c"
            conditions = []
            query_params = []

            conditions.append(" rr.establishment_id = ?")
            query_params.append(selected_restaurant_id)

            if nummonth_filter != 0:
                conditions.append("MONTH(rr.date) = ?")
                query_params.append(nummonth_filter)
            
            if query:
                conditions.append("LOWER(c.username) LIKE ?")
                query_params.append(f"%{query}%")

            if year_filter:
                conditions.append("YEAR(rr.date) = ?")
                query_params.append(int(year_filter))
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            if sort_option == "Username":
                base_query += " ORDER BY c.username"
            elif sort_option == "Rating":
                base_query += " ORDER BY rr.rating"
            
            if sortdir_option.lower() == "descending":
                base_query += " DESC"
            
            cursor.execute(base_query, query_params)
            rows = cursor.fetchall()
            conn.close()
            
            update_restaurant_reviews_table(rows)
        
    # Function to edit restaurant reviews
    def edit_restaurant_review(event):
        # Function for submit button
        def submit_review():
            review_content = entry_review_content.get().strip()
            review_rating = entry_review_rating.get().strip()

            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE establishment_reviews SET content=?, rating=? WHERE establishment_reviews_id=? AND establishment_id=?",
                            (review_content, review_rating, selected_establishment_review_id, selected_restaurant_id))
                cursor.execute("SELECT AVG(rating) FROM establishment_reviews WHERE establishment_id=?", 
                               (selected_restaurant_id,))
                average_rating = cursor.fetchone()[0]
                
                cursor.execute("UPDATE food_establishment SET average_rating=? WHERE establishment_id=?", 
                               (average_rating, selected_restaurant_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Establishment review updated successfully")
                review_popup.destroy()
                
                restaurant_reviews = fetch_restaurant_reviews(selected_restaurant_id)
                update_restaurant_reviews_table(restaurant_reviews)
                restaurants = fetch_restaurants()
                update_table(restaurants)
        
        # Function to delete a restaurant review
        def delete_establishment_review():
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this establishment review?")
            if response:
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM establishment_reviews WHERE establishment_reviews_id=?", (selected_establishment_review_id,))
                    cursor.execute("SELECT AVG(rating) FROM establishment_reviews WHERE establishment_id=?", 
                               (selected_restaurant_id,))
                    average_rating = cursor.fetchone()[0]
                    
                    cursor.execute("UPDATE food_establishment SET average_rating=? WHERE establishment_id=?", 
                                (average_rating, selected_restaurant_id))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Establishment review successfully deleted")
                    review_popup.destroy()
                    
                    restaurant_reviews = fetch_restaurant_reviews(selected_restaurant_id)
                    update_restaurant_reviews_table(restaurant_reviews)
                    restaurants = fetch_restaurants()
                    update_table(restaurants)

        establishment_review = restaurant_reviews_tree.selection()
        if establishment_review:
            selected_establishment_review_id = restaurant_reviews_tree.item(establishment_review, "values")[0]

            # Fetch current establishment review details
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT establishment_reviews_id, content, rating FROM establishment_reviews WHERE establishment_reviews_id=? AND establishment_id=?",
                            (selected_establishment_review_id, selected_restaurant_id))
                establishment_review = cursor.fetchone()
                conn.close()

            if not selected_establishment_review_id:
                messagebox.showerror("Error", "Establishment review not found")
                return

            # Create pop-up window
            review_popup = tk.Toplevel(root)
            review_popup.title("Establishment Reviews")
            review_popup.configure(background="#FFF2DC")
            
            ttk.Label(review_popup, text="Review Content:").grid(row=0, column=0, padx=5, pady=5)
            entry_review_content = ttk.Entry(review_popup)
            entry_review_content.grid(row=0, column=1, padx=5, pady=5)
            entry_review_content.insert(0, establishment_review[1])

            ttk.Label(review_popup, text="Review Rating:").grid(row=1, column=0, padx=5, pady=5)
            entry_review_rating = ttk.Entry(review_popup)
            entry_review_rating.grid(row=1, column=1, padx=5, pady=5)
            entry_review_rating.insert(0, establishment_review[2])

            btn_delete = ttk.Button(review_popup, text="Delete Review", command=delete_establishment_review)
            btn_delete.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

            btn_edit = ttk.Button(review_popup, text="Submit Review", command=submit_review)
            btn_edit.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

            # Adjust pop-up window dimensions
            review_popup.geometry("")
            review_popup.mainloop()

    # Function to display all food items in a new window
    def show_all_food_items():
        all_food_items = fetch_all_food_items()
        
        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("All Food Items")
        popup.configure(background="#FFF2DC")
        
        # Table for displaying all food items
        all_food_items_columns = ("Restaurant Name", "Food Name", "Food Type", "Price", "Average Rating")
        all_food_items_tree = ttk.Treeview(popup, columns=all_food_items_columns, show="headings", height=10)
        for col in all_food_items_columns:
            all_food_items_tree.heading(col, text=col)
            all_food_items_tree.column(col, anchor="center", width=50)
            
        all_food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
        
        # Populate the table with all food items
        for row in all_food_items:
            all_food_items_tree.insert("", tk.END, values=row)
        
        # Adjust pop-up window dimensions
        popup.geometry("800x400")
        popup.mainloop()
    
    # Function to add food item review (1)
    def add_food_item_review():
        def submit_customer_food_item():
            # Fetch inputs from user
            username = entry_username.get().strip()
            name = entry_name.get().strip()
            
            # Check if the username field is empty
            if not username and not name:
                messagebox.showerror("Error", "Please enter the customer username and name properly")
                return
            
            # Query to add a food item review
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT customer_id, name FROM customer WHERE username = ?",
                (username,))
                existing_customer = cursor.fetchone()               
                if existing_customer:
                    if existing_customer[1] == name:
                        customer_id = existing_customer[0]
                        messagebox.showinfo("Success", "Customer found. Welcome back!")
                        conn.close()
                        customer_popup.destroy()
                        open_foodreview_popup(customer_id)
                    else:
                        messagebox.showerror("Error", "Username already in use!")
                        return
                else:
                    cursor.execute("INSERT INTO customer (username, name) VALUES (?, ?)",
                                (username, name))
                    conn.commit()
                    customer_id = cursor.lastrowid
                    messagebox.showinfo("Success", "Customer added successfully")
                    conn.close()
                    customer_popup.destroy()
                    open_foodreview_popup(customer_id)
                
        # Create pop-up window
        customer_popup = tk.Toplevel(root)
        customer_popup.title("Add Customer")
        customer_popup.configure(background="#FFF2DC")

        # Add necessary fields
        ttk.Label(customer_popup, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        entry_username = ttk.Entry(customer_popup)
        entry_username.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(customer_popup, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        entry_name = ttk.Entry(customer_popup)
        entry_name.grid(row=1, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(customer_popup, text="Submit", command=submit_customer_food_item)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        customer_popup.geometry("300x250")
        customer_popup.mainloop()
        return
    
    # Function to display all food item reviews
    def show_all_food_reviews():
        all_food_reviews = fetch_all_food_reviews()
        
        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("All Food Item Reviews")
        popup.configure(background="#FFF2DC")
        
        # Table for displaying all food items
        all_food_items_columns = ("Food Name", "Username", "Content", "Rating", "Date")
        all_food_items_tree = ttk.Treeview(popup, columns=all_food_items_columns, show="headings", height=10)
        for col in all_food_items_columns:
            all_food_items_tree.heading(col, text=col)
            all_food_items_tree.column(col, anchor="center", width=50)
            
        all_food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
        
        # Populate the table with all food items
        for row in all_food_reviews:
            all_food_items_tree.insert("", tk.END, values=row)
        
        # Adjust pop-up window dimensions
        popup.geometry("800x400")
        popup.mainloop()

    # Function to display all restaurant reviews
    def show_all_restaurant_reviews():
        all_restaurant_reviews = fetch_all_restaurant_reviews()
        
        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("All Restaurant Reviews")
        popup.configure(background="#FFF2DC")
        
        # Table for displaying all restaurant reviews
        all_food_items_columns = ("Restaurant Name", "Username", "Content", "Rating", "Date")
        all_food_items_tree = ttk.Treeview(popup, columns=all_food_items_columns, show="headings", height=10)
        for col in all_food_items_columns:
            all_food_items_tree.heading(col, text=col)
            all_food_items_tree.column(col, anchor="center", width=50)
            
        all_food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
        
        # Populate the table with all restaurant reviews
        for row in all_restaurant_reviews:
            all_food_items_tree.insert("", tk.END, values=row)
        
        # Adjust pop-up window dimensions
        popup.geometry("800x400")
        popup.mainloop()

    # Function to add food item review (2)
    def open_foodreview_popup(customer_id):
        def submit_review():
            if not food_items_tree.selection():
                messagebox.showerror("Error", "Please select a food item")
                return
            
            # Fetch user inputs
            content = entry_content.get().strip()
            rating = entry_rating.get().strip()
            
            # Check if the username field is empty
            if not content or not rating:
                messagebox.showerror("Error", "Please enter both fields correctly")
                return
            
            establishment_id = tree.item(tree.selection()[0], "values")[0]  
            item_id = food_items_tree.item(food_items_tree.selection()[0], "values")[0]  
            
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO food_reviews (item_id, customer_id, date, content, rating) VALUES (?, ?, CURDATE(), ?, ?)",
                (item_id, customer_id, content, rating))
                cursor.execute("SELECT AVG(rating) FROM food_reviews WHERE item_id=?", 
                               (item_id,))
                average_rating = cursor.fetchone()[0]
                
                cursor.execute("UPDATE food_item SET average_rating=? WHERE item_id=?", 
                               (average_rating, item_id))
                conn.commit()
                messagebox.showinfo("Success", "Food item review added successfully")
                conn.close()
                review_popup.destroy()
                
                reviews = fetch_food_reviews(item_id)
                update_food_reviews_table(reviews)
                food_items = fetch_food_items(establishment_id)
                update_food_items_table(food_items)
                
        # Create pop-up window
        review_popup = tk.Toplevel(root)
        review_popup.title("Add Review")
        review_popup.configure(background="#FFF2DC")

        # Necessary fields
        ttk.Label(review_popup, text="Content:").grid(row=0, column=0, padx=5, pady=5)
        entry_content = ttk.Entry(review_popup)
        entry_content.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(review_popup, text="Rating:").grid(row=1, column=0, padx=5, pady=5)
        entry_rating = ttk.Entry(review_popup)
        entry_rating.grid(row=1, column=1, padx=5, pady=5)

        # Add submit button
        btn_submit = ttk.Button(review_popup, text="Submit", command=submit_review)
        btn_submit.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Adjust pop-up window dimensions
        review_popup.geometry("300x250")
        review_popup.mainloop()

    # Function to edit food item review
    def edit_food_item_review(event):
        # Function for submit button
        def submit_button():
            review_content = entry_review_content.get().strip()
            review_rating = entry_review_rating.get().strip()
            
            establishment_id = tree.item(tree.selection()[0], "values")[0]  
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE food_reviews SET content=?, rating=? WHERE food_reviews_id=? AND item_id=?", 
                               (review_content, review_rating, selected_food_review_id, selected_food_item_id))
                cursor.execute("SELECT AVG(rating) FROM food_reviews WHERE item_id=?", (selected_food_item_id,))
                average_rating = cursor.fetchone()[0]
                
                cursor.execute("UPDATE food_item SET average_rating=? WHERE item_id=?", (average_rating, selected_food_item_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Food review updated successfully")
                review_popup.destroy()
                
                reviews = fetch_food_reviews(selected_food_item_id)
                update_food_reviews_table(reviews)
                food_items = fetch_food_items(establishment_id)
                update_food_items_table(food_items)
        
        # Function to delete food item review
        def delete_food_item_review():
            return
    
        food_review = food_reviews_tree.selection()
        if food_review:
            selected_food_review_id = food_reviews_tree.item(food_review, "values")[0]
            
            # Create pop-up window
            review_popup = tk.Toplevel(root)
            review_popup.title("Food Reviews")
            review_popup.configure(background="#FFF2DC")
            
            ttk.Label(review_popup, text="Content:").grid(row=0, column=0, padx=5, pady=5)
            entry_review_content = ttk.Entry(review_popup)
            entry_review_content.grid(row=0, column=1, padx=5, pady=5)
            entry_review_content.insert(0, food_reviews_tree.item(food_review, "values")[3])

            ttk.Label(review_popup, text="Rating:").grid(row=1, column=0, padx=5, pady=5)
            entry_review_rating = ttk.Entry(review_popup)
            entry_review_rating.grid(row=1, column=1, padx=5, pady=5)
            entry_review_rating.insert(0, food_reviews_tree.item(food_review, "values")[4])

            btn_delete = ttk.Button(review_popup, text="Delete Review", command=delete_food_item_review)
            btn_delete.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

            btn_edit = ttk.Button(review_popup, text="Submit Review", command=submit_button)
            btn_edit.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

            # Adjust pop-up window dimensions
            review_popup.geometry("300x150")
            review_popup.mainloop()

    # Function to execute when a restaurant is selected
    def on_restaurant_select(event):
        item = tree.selection()[0]
        
        # Get the data from the selected item
        data = tree.item(item, "values")

        global selected_restaurant_id
        selected_restaurant_id = data[0]

        # Fetch and display food items and reviews associated with selected restaurant
        food_items = fetch_food_items(data[0])
        update_food_items_table(food_items)
        
        restaurant_reviews = fetch_restaurant_reviews(data[0])
        update_restaurant_reviews_table(restaurant_reviews)
        
        clear_food_reviews_table()

        edit_restaurant()
    
    def on_food_item_select(event):
        item = food_items_tree.selection()[0]
        data = food_items_tree.item(item, "values")
        
        global selected_food_item_id
        selected_food_item_id = data[0]
        
        food_reviews = fetch_food_reviews(selected_food_item_id)
        update_food_reviews_table(food_reviews)
        
        edit_food_item(event)

    def clear_food_reviews_table():
        for i in food_reviews_tree.get_children():
            food_reviews_tree.delete(i)
    
    root = tk.Tk()
    root.title("GrubHub")
    root.iconbitmap("src/Icon.ico")
    root.geometry("1980x1020")
    root.configure(background="#FFF2DC")

    # Apply styles
    style = ttk.Style()
    style.configure("TFrame", background="#FFF2DC")
    style.configure("TLabel", font=("Inter", 10), background="#FFF2DC")
    style.configure("TButton", font=("Inter", 10))
    style.configure("TEntry", font=("Inter", 10))
    style.configure("TNotebook", font=("Inter", 10))
    style.configure("TNotebook.Tab", font=("Inter", 10, "bold"))
    style.configure("Treeview.Heading", font=("Inter", 10, "bold"))

    # ===== RESTAURANT TABLE START =====

    lbl_food_items = ttk.Label(root, text="Restaurants", font=("Inter", 14, "bold"), background="#FFF2DC")
    lbl_food_items.pack(side=tk.TOP, padx=5, pady=5)

    search_frame = ttk.Frame(root)
    search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    lbl_search = ttk.Label(search_frame, text="Search", font=("Inter", 10))
    lbl_search.pack(side=tk.LEFT, padx=5)
    
    entry_search = ttk.Entry(search_frame, width=30)
    entry_search.pack(side=tk.LEFT, padx=5)

    rating_var = tk.StringVar()
    rating_options = ["None", "1 Star", "2 Stars and Up", "3 Stars and Up", "4 Stars and Up", "5 Stars"]
    rating_dropdown = ttk.Combobox(search_frame, textvariable=rating_var, values=rating_options, state="readonly")
    rating_dropdown.set("None")
    rating_dropdown.pack(side=tk.LEFT, padx=5)

    lbl_sort = ttk.Label(search_frame, text="Sort", font=("Inter", 10))
    lbl_sort.pack(side=tk.LEFT, padx=5)

    sort_var = tk.StringVar()
    sort_options = ["None", "Name", "Average Rating"]
    sort_dropdown = ttk.Combobox(search_frame, textvariable=sort_var, values=sort_options, state="readonly")
    sort_dropdown.set("None")
    sort_dropdown.pack(side=tk.LEFT, padx=5)

    sortdir_var = tk.StringVar()
    sortdir_options = ["Ascending", "Descending"]
    sortdir_dropdown = ttk.Combobox(search_frame, textvariable=sortdir_var, values=sortdir_options, state="readonly")
    sortdir_dropdown.set("Ascending")
    sortdir_dropdown.pack(side=tk.LEFT, padx=5)

    btn_search_sort = ttk.Button(search_frame, text="Search & Sort", command=search_sort_restaurants)
    btn_search_sort.pack(side=tk.LEFT, padx=5)

    btn_add_restaurant = ttk.Button(search_frame, text="Add Restaurant", command=add_restaurant)
    btn_add_restaurant.pack(side=tk.RIGHT, padx=5)
    
    # Table for displaying restaurants
    columns = ("ID", "Name", "Contact Info", "Average Rating", "Website", "Location")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=50)
    tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)

    # ===== RESTAURANT TABLE END =====
    
    # ===== FOOD ITEM TABLE START =====

    lbl_food_items = ttk.Label(root, text="Food Items", font=("Inter", 14, "bold"), background="#FFF2DC")
    lbl_food_items.pack(side=tk.TOP, padx=5, pady=5)
    
    food_item_frame = ttk.Frame(root)
    food_item_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    btn_add_food_item = ttk.Button(food_item_frame, text="Add Food Item", command=add_food_item)
    btn_add_food_item.pack(side=tk.RIGHT, padx=5)

    show_all_food_frame = ttk.Frame(root)
    show_all_food_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    btn_show_all_food_items = ttk.Button(food_item_frame, text="Show All Food Items", command=show_all_food_items)
    btn_show_all_food_items.pack(side=tk.RIGHT, padx=5)

    lbl_food_item_search = ttk.Label(food_item_frame, text="Search", font=("Inter", 10))
    lbl_food_item_search.pack(side=tk.LEFT, padx=5)
    
    entry_food_item_search = ttk.Entry(food_item_frame, width=30)
    entry_food_item_search.pack(side=tk.LEFT, padx=5)

    food_type_options = fetch_food_item_types()
    food_type_var = tk.StringVar()
    food_type_dropdown = ttk.Combobox(food_item_frame, textvariable=food_type_var, values=food_type_options, state="readonly")
    food_type_dropdown.set("None")
    food_type_dropdown.pack(side=tk.LEFT, padx=5)

    lbl_sort_food_item = ttk.Label(food_item_frame, text="Sort", font=("Inter", 10))
    lbl_sort_food_item.pack(side=tk.LEFT, padx=5)

    sort_food_item_var = tk.StringVar()
    sort_food_item_options = ["None", "Name", "Price"]
    sort_food_item_dropdown = ttk.Combobox(food_item_frame, textvariable=sort_food_item_var, values=sort_food_item_options, state="readonly")
    sort_food_item_dropdown.set("None")
    sort_food_item_dropdown.pack(side=tk.LEFT, padx=5)

    sortdir_food_item_var = tk.StringVar()
    sortdir_food_item_options = ["Ascending", "Descending"]
    sortdir_food_item_dropdown = ttk.Combobox(food_item_frame, textvariable=sortdir_food_item_var, values=sortdir_food_item_options, state="readonly")
    sortdir_food_item_dropdown.set("Ascending")
    sortdir_food_item_dropdown.pack(side=tk.LEFT, padx=5)

    lbl_pricerange = ttk.Label(food_item_frame, text="Price Range", font=("Inter", 10))
    lbl_pricerange.pack(side=tk.LEFT, padx=5)
    
    pricerange_min = ttk.Entry(food_item_frame, width=20)
    pricerange_min.pack(side=tk.LEFT, padx=5)

    lbl_pricerange = ttk.Label(food_item_frame, text="-", font=("Inter", 10))
    lbl_pricerange.pack(side=tk.LEFT, padx=5)

    pricerange_max = ttk.Entry(food_item_frame, width=20)
    pricerange_max.pack(side=tk.LEFT, padx=5)

    btn_search_sort = ttk.Button(food_item_frame, text="Search & Sort", command=search_sort_food_items)
    btn_search_sort.pack(side=tk.LEFT, padx=5)

    food_items_columns = ("Food ID", "Restaurant Name", "Food Name", "Food Type", "Price", "Average Rating")
    food_items_tree = ttk.Treeview(root, columns=food_items_columns, show="headings", height=5)
    for col in food_items_columns:
        food_items_tree.heading(col, text=col)
        food_items_tree.column(col, anchor="center", width=50)

    food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)

    # ===== FOOD ITEM TABLE END =====

    # Create a Notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create frames for each tab
    restaurant_frame = ttk.Frame(notebook)
    food_frame = ttk.Frame(notebook)

    # Add the frames to the Notebook with corresponding tab names
    notebook.add(restaurant_frame, text="Restaurant Reviews")
    notebook.add(food_frame, text="Food Item Reviews")

    # ===== RESTAURANT REVIEW SECTION =====

    # Create a top frame for search and sort fields
    top_frame = ttk.Frame(restaurant_frame)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    lbl_reviews_search = ttk.Label(top_frame, text="Search", font=("Inter", 10))
    lbl_reviews_search.pack(side=tk.LEFT, padx=5)

    reviews_search = ttk.Entry(top_frame, width=30)
    reviews_search.pack(side=tk.LEFT, padx=5)

    review_month_options = ["None", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    review_month_var = tk.StringVar()
    review_month_dropdown = ttk.Combobox(top_frame, textvariable=review_month_var, values=review_month_options, state="readonly")
    review_month_dropdown.set("None")
    review_month_dropdown.pack(side=tk.LEFT, padx=5)

    conn = connect_db()
    curyear = 2024
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT YEAR(CURDATE())")
        year_row = cursor.fetchone()
        if year_row:
            curyear = year_row[0]

    reviews_year = ttk.Entry(top_frame, width=10)
    reviews_year.pack(side=tk.LEFT, padx=5)
    reviews_year.insert(0, curyear)

    lbl_sort_reviews = ttk.Label(top_frame, text="Sort", font=("Inter", 10))
    lbl_sort_reviews.pack(side=tk.LEFT, padx=5)

    sort_reviews_var = tk.StringVar()
    sort_reviews_options = ["None", "Username", "Rating"]
    sort_reviews_dropdown = ttk.Combobox(top_frame, textvariable=sort_reviews_var, values=sort_reviews_options, state="readonly")
    sort_reviews_dropdown.set("None")
    sort_reviews_dropdown.pack(side=tk.LEFT, padx=5)

    sortdir_reviews_var = tk.StringVar()
    sortdir_reviews_options = ["Ascending", "Descending"]
    sortdir_reviews_dropdown = ttk.Combobox(top_frame, textvariable=sortdir_reviews_var, values=sortdir_reviews_options, state="readonly")
    sortdir_reviews_dropdown.set("Ascending")
    sortdir_reviews_dropdown.pack(side=tk.LEFT, padx=5)

    btn_search_sort = ttk.Button(top_frame, text="Search & Sort", command=search_sort_estreviews)
    btn_search_sort.pack(side=tk.LEFT, padx=5)

    btn_add_restaurant_review = ttk.Button(top_frame, text="Add Restaurant Review", command=add_restaurant_review)
    btn_add_restaurant_review.pack(side=tk.RIGHT, padx=5)

    btn_view_all_restaurant_review = ttk.Button(top_frame, text="Show All Restaurant Reviews", command=show_all_restaurant_reviews)
    btn_view_all_restaurant_review.pack(side=tk.RIGHT, padx=5)

    table_frame = ttk.Frame(restaurant_frame)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    restaurant_reviews_columns = ("ID", "Username", "Content", "Rating", "Date")
    restaurant_reviews_tree = ttk.Treeview(table_frame, columns=restaurant_reviews_columns, show="headings", height=5)
    for col in restaurant_reviews_columns:
        restaurant_reviews_tree.heading(col, text=col)
        restaurant_reviews_tree.column(col, anchor="center", width=50)
    restaurant_reviews_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ===== FOOD ITEM REVIEW SECTION =====

    top1_frame = ttk.Frame(food_frame)
    top1_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    lbl_freviews_search = ttk.Label(top1_frame, text="Search", font=("Inter", 10))
    lbl_freviews_search.pack(side=tk.LEFT, padx=5)

    freviews_search = ttk.Entry(top1_frame, width=30)
    freviews_search.pack(side=tk.LEFT, padx=5)

    freview_month_var = tk.StringVar()
    freview_month_dropdown = ttk.Combobox(top1_frame, textvariable=freview_month_var, values=review_month_options, state="readonly")
    freview_month_dropdown.set("None")
    freview_month_dropdown.pack(side=tk.LEFT, padx=5)

    conn = connect_db()
    curyear1 = 2024
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT YEAR(CURDATE())")
        year_row1 = cursor.fetchone()
        if year_row:
            curyear1 = year_row1[0]

    freviews_year = ttk.Entry(top1_frame, width=10)
    freviews_year.pack(side=tk.LEFT, padx=5)
    freviews_year.insert(0, curyear1)

    lbl_sort_freviews = ttk.Label(top1_frame, text="Sort", font=("Inter", 10))
    lbl_sort_freviews.pack(side=tk.LEFT, padx=5)

    sort_freviews_var = tk.StringVar()
    sort_freviews_dropdown = ttk.Combobox(top1_frame, textvariable=sort_freviews_var, values=sort_reviews_options, state="readonly")
    sort_freviews_dropdown.set("None")
    sort_freviews_dropdown.pack(side=tk.LEFT, padx=5)

    sortdir_freviews_var = tk.StringVar()
    sortdir_freviews_dropdown = ttk.Combobox(top1_frame, textvariable=sortdir_freviews_var, values=sortdir_reviews_options, state="readonly")
    sortdir_freviews_dropdown.set("Ascending")
    sortdir_freviews_dropdown.pack(side=tk.LEFT, padx=5)

    btn_fsearch_sort = ttk.Button(top1_frame, text="Search & Sort")
    btn_fsearch_sort.pack(side=tk.LEFT, padx=5)

    btn_add_food_review = ttk.Button(top1_frame, text="Add Food Item Review", command=add_food_item_review)
    btn_add_food_review.pack(side=tk.RIGHT, padx=5)

    btn_view_all_food_review = ttk.Button(top1_frame, text="Show All Food Item Reviews", command=show_all_food_reviews)
    btn_view_all_food_review.pack(side=tk.RIGHT, padx=5)

    table1_frame = ttk.Frame(food_frame)
    table1_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    food_reviews_columns = ("Food ID", "Food Item Name", "Username", "Content", "Rating", "Date")
    food_reviews_tree = ttk.Treeview(table1_frame, columns=food_reviews_columns, show="headings", height=10)
    for col in food_reviews_columns:
        food_reviews_tree.heading(col, text=col)
        food_reviews_tree.column(col, anchor="center", width=50)
    food_reviews_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree.bind("<<TreeviewSelect>>", on_restaurant_select)
    food_items_tree.bind("<<TreeviewSelect>>", edit_food_item)
    
    tree.bind("<<TreeviewSelect>>", on_restaurant_select)
    restaurant_reviews_tree.bind("<<TreeviewSelect>>", edit_restaurant_review)
    
    food_items_tree.bind('<<TreeviewSelect>>', on_food_item_select)
    food_reviews_tree.bind("<<TreeviewSelect>>", edit_food_item_review)
    

    # Update restaurant details table
    def update_table(rows):
        for row in tree.get_children():
            tree.delete(row)
        for row in rows:
            tree.insert("", tk.END, values=row)
    
    # Update restaurant food items table
    def update_food_items_table(rows):
        for row in food_items_tree.get_children():
            food_items_tree.delete(row)
        for row in rows:
            food_items_tree.insert("", tk.END, values=row)
            
    # Update restaurant reviews table
    def update_restaurant_reviews_table(rows):
        for row in restaurant_reviews_tree.get_children():
            restaurant_reviews_tree.delete(row)
        for row in rows:
            restaurant_reviews_tree.insert("", tk.END, values=row)

    # Update food reviews table
    def update_food_reviews_table(rows):
        for row in food_reviews_tree.get_children():
            food_reviews_tree.delete(row)
        for row in rows:
            food_reviews_tree.insert("", tk.END, values=row)

    # Load initial data
    restaurants = fetch_restaurants()
    update_table(restaurants)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    init_main_window()
