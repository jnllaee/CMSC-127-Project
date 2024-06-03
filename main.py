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

# Fetch all food items from the database
def fetch_all_food_items():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT fi.item_id, fi.name, fi.price, fit.food_type, fe.name, fi.average_rating
            FROM food_item fi
            NATURAL JOIN food_item_type fit
            JOIN food_establishment fe ON fi.establishment_id = fe.establishment_id
            WHERE fi.establishment_id = ?
            """, 
            (establishment_id,)
        )

        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all food items of the selected item (based on the restaurant selected) from the database
def fetch_food_items(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT fe.name, fi.item_id, fi.name, fi.price, fit.food_type, fi.average_rating
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

# Fetch all restaurants from the database
def fetch_restaurant_reviews(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.username, r.content, r.rating, r.date
            FROM customer c
            NATURAL JOIN establishment_reviews r
            WHERE r.establishment_id = ?
            """, (establishment_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Initialize main window
def init_main_window():
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

    # Header
    header_frame = ttk.Frame(root)
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    icon = tk.PhotoImage(file="src/Icon.png")
    icon_scaled = icon.subsample(3,3)
    lbl_header = ttk.Label(header_frame, image=icon_scaled, justify="center")
    lbl_header.pack(side=tk.LEFT, padx=5)
    lbl_header2 = ttk.Label(header_frame, text="GrubHub", justify="center", font=("Inter", 14, "bold"))
    lbl_header2.pack(side=tk.LEFT, padx=5)

    lbl_Restaurant = ttk.Label(root, text="Restaurants", font=("Inter", 14, "bold"), background="#FFF2DC")
    lbl_Restaurant.pack(side=tk.TOP, padx=5, pady=5)

    # Search bar
    search_frame = ttk.Frame(root)
    search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    lbl_search = ttk.Label(search_frame, text="Search", font=("Inter", 10))
    lbl_search.pack(side=tk.LEFT, padx=5)
    
    entry_search = ttk.Entry(search_frame, width=30)
    entry_search.pack(side=tk.LEFT, padx=5)
    
    # Function to search and sort restaurants
    def search_sort_restaurants():
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
    
    # Function to add restaurant review
    def add_restaurant_review():
        # Function to handle submission of restaurant details
        def submit_customer_restaurant():
            # Get values from entry fields
            username = entry_username.get().strip()
            name = entry_name.get().strip()
            
            # Check if the username field is empty
            if not username:
                messagebox.showerror("Error", "Please enter the customer username")
                return
            
            # Check if the name field is empty
            if not name:
                messagebox.showerror("Error", "Please enter the customer name")
                return
            
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
                    customer_id = cursor.lastrowid()
                    conn.close()
                    messagebox.showinfo("Success", "Customer added successfully")
                    customer_popup.destroy()
                    open_review_popup(customer_id)
                
        # Create pop-up window
        customer_popup = tk.Toplevel(root)
        customer_popup.title("Add Customer")
        customer_popup.configure(background="#FFF2DC")

        # Design the UI
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

        # Design the UI
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
        
    def open_review_popup(customer_id):
        def submit_review():
            # Get values from entry fields
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
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Restaurant review added successfully")
                review_popup.destroy()
                
                reviews = fetch_restaurant_reviews(establishment_id)
                update_restaurant_reviews_table(reviews)
                
        # Create pop-up window
        review_popup = tk.Toplevel(root)
        review_popup.title("Add Review")
        review_popup.configure(background="#FFF2DC")

        # Design the UI
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
    
    def edit_restaurant():
        if not selected_restaurant_id:
            messagebox.showerror("Error", "No restaurant selected for editing")
            return
        
        # Function to handle submission of edited restaurant details
        def submit_restaurant():
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
        
        # Function to handle deletion of restaurant
        def delete_restaurant():
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this restaurant?")
            if response:
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM food_establishment WHERE establishment_id=?", (selected_restaurant_id,))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Restaurant deleted successfully")
                    popup.destroy()

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

    def search_sort_food_items():
        query = entry_food_item_search.get().lower()
        food_type_filter = food_type_var.get()
        sort_option = sort_food_item_var.get()
        price_range_min = pricerange_min.get()
        price_range_max = pricerange_max.get()
        sortdir_option = sortdir_food_item_var.get()
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            base_query = "SELECT fi.item_id, fi.name, fi.price, fit.food_type FROM food_item fi NATURAL JOIN food_item_type fit"
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

    def add_food_item():
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
                cursor.execute("INSERT INTO food_item(name, price, establishment_id, food_type_id) VALUES (?, ?, ?, ?)",
                            (food_item_name, food_item_price, selected_restaurant_id, food_type_id))
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
    
    def edit_food_item(event):
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

                # Check if the food item already exists in the restaurant
                cursor.execute("SELECT name FROM food_item WHERE establishment_id=?", (selected_restaurant_id,))
                all_food_items = cursor.fetchall()
                existing_food_items = [item[0] for item in all_food_items]
                if food_item_name in existing_food_items:
                    messagebox.showinfo("Warning", "Food item already existing in restaurant")
                    conn.close()

                # If food item type doesn't exist, add it to the database
                if food_item_type not in food_item_types:
                    cursor.execute("INSERT INTO food_item_type(food_type) VALUES (?)", (food_item_type,))
                    conn.commit()

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

        def delete_food_item():
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this food item?")
            if response:
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
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
        
    def on_treeview_select(event):
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

        edit_restaurant()

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

    # Search bar
    search_frame = ttk.Frame(root)
    search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    lbl_search = ttk.Label(search_frame, text="Search", font=("Inter", 10))
    lbl_search.pack(side=tk.LEFT, padx=5)
    
    entry_search = ttk.Entry(search_frame, width=30)
    entry_search.pack(side=tk.LEFT, padx=5)

    # Dropdown for rating filter
    rating_var = tk.StringVar()
    rating_options = ["None", "1 Star", "2 Stars and Up", "3 Stars and Up", "4 Stars and Up", "5 Stars"]
    rating_dropdown = ttk.Combobox(search_frame, textvariable=rating_var, values=rating_options, state="readonly")
    rating_dropdown.set("None")
    rating_dropdown.pack(side=tk.LEFT, padx=5)

    # Sorting
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

    # Add restaurant review
    btn_add_restaurant_review = ttk.Button(search_frame, text="Add Restaurant Review", command=add_restaurant_review)
    btn_add_restaurant_review.pack(side=tk.RIGHT, padx=5)

    # Add restaurant
    btn_add_restaurant = ttk.Button(search_frame, text="Add Restaurant", command=add_restaurant)
    btn_add_restaurant.pack(side=tk.RIGHT, padx=5)

    # Table for displaying restaurants
    columns = ("ID", "Name", "Contact Info", "Average Rating", "Website", "Location")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=50)
    tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
    
    food_item_frame = ttk.Frame(root)
    food_item_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    # Add food item
    btn_add_food_item = ttk.Button(food_item_frame, text="Add Food Item", command=add_food_item)
    btn_add_food_item.pack(side=tk.RIGHT, padx=5)

    lbl_food_item_search = ttk.Label(food_item_frame, text="Search", font=("Inter", 10))
    lbl_food_item_search.pack(side=tk.LEFT, padx=5)
    
    entry_food_item_search = ttk.Entry(food_item_frame, width=30)
    entry_food_item_search.pack(side=tk.LEFT, padx=5)

    food_type_options = fetch_food_item_types()

    # Dropdown for rating filter
    food_type_var = tk.StringVar()
    food_type_dropdown = ttk.Combobox(food_item_frame, textvariable=food_type_var, values=food_type_options, state="readonly")
    food_type_dropdown.set("None")
    food_type_dropdown.pack(side=tk.LEFT, padx=5)

    # Sorting
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
    
    # Title for food items table
    lbl_food_items = ttk.Label(root, text="Food Items", font=("Inter", 14, "bold"), background="#FFF2DC")
    lbl_food_items.pack(side=tk.TOP, padx=5, pady=5)
    
    # Table for displaying food items

    food_items_columns = ("Restaurant Name", "Food ID", "Food", "Price", "Food Type")
    food_items_tree = ttk.Treeview(root, columns=food_items_columns, show="headings", height=10)
    for col in food_items_columns:
        food_items_tree.heading(col, text=col)
        food_items_tree.column(col, anchor="center", width=50)
    food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
    
    lbl_Reviews = ttk.Label(root, text="Reviews", font=("Inter", 14, "bold"), background="#FFF2DC")
    lbl_Reviews.pack(side=tk.TOP, padx=5, pady=5)

    # Table for displaying restaurant reviews
    restaurant_reviews_columns = ("Username", "Content", "Rating", "Date")
    restaurant_reviews_tree = ttk.Treeview(root, columns=restaurant_reviews_columns, show="headings", height=10)
    for col in restaurant_reviews_columns:
        restaurant_reviews_tree.heading(col, text=col)
        restaurant_reviews_tree.column(col, anchor="center", width=50)
    restaurant_reviews_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
    
    def on_treeview_select(event):
        # Get the selected item
        item = tree.selection()[0]
        
        # Get the data from the selected item
        data = tree.item(item, "values")
        
        # Fetch and display food items and reviews associated with selected restaurant
        food_items = fetch_food_items(data[0])
        update_food_items_table(food_items)
        restaurant_reviews = fetch_restaurant_reviews(data[0])
        update_restaurant_reviews_table(restaurant_reviews)
        
    tree.bind("<<TreeviewSelect>>", on_treeview_select)
    food_items_tree.bind("<<TreeviewSelect>>", edit_food_item)

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

    # Function to display all food items in a new window
    def show_all_food_items():
        all_food_items = fetch_all_food_items()
        
        # Create pop-up window
        popup = tk.Toplevel(root)
        popup.title("All Food Items")
        popup.configure(background="#FFF2DC")
        
        # Table for displaying all food items
        all_food_items_columns = ("Restaurant Name", "Food Name", "Price", "Food Type", "Average Rating")
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
    
    # Button to show all food items
    btn_show_all_food_items = ttk.Button(search_frame, text="Show All Food Items", command=show_all_food_items)
    btn_show_all_food_items.pack(side=tk.RIGHT, padx=5)
    
    # Load initial data
    restaurants = fetch_restaurants()
    update_table(restaurants)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    init_main_window()
