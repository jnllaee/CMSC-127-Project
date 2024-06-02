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

# Fetch all food items of the selected item (based on the restaurant selected) from the database
def fetch_food_items(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fi.name, fi.price, fit.food_type FROM food_item fi NATURAL JOIN food_item_type fit WHERE establishment_id = ?", (establishment_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# Fetch all restaurants from the database
def fetch_restaurant_reviews(establishment_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT c.username, r.content, r.rating, r.date FROM customer c NATURAL JOIN establishment_reviews r WHERE r.establishment_id = ?", (establishment_id,))
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

    # Function to add restaurant
    def add_restaurant():
        # Function to handle submission of restaurant details
        def submit_restaurant():
                        # Get values from entry fields
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
    
    # Table for displaying food items
    food_items_columns = ("Name", "Price", "Food Type")
    food_items_tree = ttk.Treeview(root, columns=food_items_columns, show="headings", height=10)
    for col in food_items_columns:
        food_items_tree.heading(col, text=col)
        food_items_tree.column(col, anchor="center", width=50)

    food_items_tree.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=10)
    
    # Table for displaying restaurant reviews
    restaurant_reviews_columns = ("Username", "Content", "Rating")
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
            
    def update_restaurant_reviews_table(rows):
        for row in restaurant_reviews_tree.get_children():
            restaurant_reviews_tree.delete(row)
        for row in rows:
            restaurant_reviews_tree.insert("", tk.END, values=row)
    

    
    # Load initial data
    restaurants = fetch_restaurants()
    update_table(restaurants)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    init_main_window()

