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
    
    # Function for searching restaurants
    def search_restaurants():
        query = entry_search.get().lower()
        rating_filter = rating_var.get()
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
            if query:
                if min_rating == 1:
                    cursor.execute("SELECT * FROM food_establishment WHERE LOWER(name) LIKE ? AND average_rating = ?", (f"%{query}%", min_rating))
                elif min_rating == 0:
                    cursor.execute("SELECT * FROM food_establishment WHERE LOWER(name) LIKE ?", (f"%{query}%",))
                else: 
                    cursor.execute("SELECT * FROM food_establishment WHERE LOWER(name) LIKE ? AND average_rating >= ?", (f"%{query}%", min_rating))
            else:
                if min_rating == 1:
                    cursor.execute("SELECT * FROM food_establishment WHERE average_rating = ?", (min_rating,))
                elif min_rating == 0:
                    cursor.execute("SELECT * FROM food_establishment", (min_rating,))
                else: 
                    cursor.execute("SELECT * FROM food_establishment WHERE average_rating >= ?", (min_rating,))
        rows = cursor.fetchall()
        
        filtered_rows = []
        for row in rows:
            if row[3] >= min_rating:
                filtered_rows.append(row)
        
        update_table(filtered_rows)
        conn.close()
    
    # Dropdown for rating filter
    rating_var = tk.StringVar()
    rating_options = ["None", "1 Star", "2 Stars and Up", "3 Stars and Up", "4 Stars and Up", "5 Stars"]
    rating_dropdown = ttk.Combobox(search_frame, textvariable=rating_var, values=rating_options, state="readonly")
    rating_dropdown.set("None")
    rating_dropdown.pack(side=tk.LEFT, padx=5)

    # Search button
    btn_search = ttk.Button(search_frame, text="Search", command=search_restaurants)
    btn_search.pack(side=tk.LEFT, padx=5)

    # Function to sort the table
    def sort_restaurants():
        sort_option = sort_var.get()
        sortdir_option = sortdir_var.get()

        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            if sortdir_option.lower() == "ascending":
                if sort_option == "Name":
                    query = "SELECT * FROM food_establishment ORDER BY name"
                elif sort_option == "Average Rating":
                    query = "SELECT * FROM food_establishment ORDER BY average_rating"
                else:
                    query = "SELECT * FROM food_establishment"
            else:
                if sort_option == "Name":
                    query = "SELECT * FROM food_establishment ORDER BY name DESC"
                elif sort_option == "Average Rating":
                    query = "SELECT * FROM food_establishment ORDER BY average_rating DESC"
                else:
                    query = "SELECT * FROM food_establishment"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            update_table(rows)

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

    # Sort button
    btn_sort = ttk.Button(search_frame, text="Sort", command=sort_restaurants)
    btn_sort.pack(side=tk.LEFT, padx=5)

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
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def on_treeview_select(event):
        # Get the selected item
        item = tree.selection()[0]
        
        # Get the data from the selected item
        data = tree.item(item, "values")
        
        # Create a popup window to display the data
        popup = tk.Toplevel(root)
        popup.title("Restaurant Details")
        popup.configure(background="#FFF2DC")
        
        # Display the restaurant details
        for i, col in enumerate(columns):
            ttk.Label(popup, text=col).grid(row=i, column=0, padx=5, pady=2)
            ttk.Label(popup, text=data[i]).grid(row=i, column=1, padx=5, pady=2)
        
        # Fetch food items associated with the selected restaurant
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fi.name, fi.price, fit.food_type FROM food_item fi NATURAL JOIN food_item_type fit WHERE establishment_id = ?", (data[0],))
            food_items = cursor.fetchall()
            
            # Display the food items in the popup window
            ttk.Label(popup, text="Food Items", font=("Inter", 10, "bold")).grid(row=len(columns), column=0, columnspan=2, padx=5, pady=2)
            for i, (name, price, food_type) in enumerate(food_items, start=len(columns) + 1):
                ttk.Label(popup, text=f"{name} ({food_type}) - ₱{price}").grid(row=i, column=0, columnspan=2, padx=5, pady=2)
            
            cursor.execute("SELECT c.username, r.content, r.rating, r.date FROM customer c NATURAL JOIN establishment_reviews r WHERE r.establishment_id = ?", (data[0],))
            reviews = cursor.fetchall()
            conn.close()

            # Display the restaurant reviews in the popup window
            ttk.Label(popup, text="Restaurant Reviews", font=("Inter", 10, "bold")).grid(row=len(food_items) + len(columns) + 1, column=0, columnspan=2, padx=5, pady=2)
            
            # Create a frame to hold the reviews
            review_frame = ttk.Frame(popup)
            review_frame.grid(row=len(food_items) + len(columns) + 2, column=0, columnspan=2, padx=5, pady=2)
            
            # Populate the review frame with review information
            for j, (username, content, rating, date) in enumerate(reviews, start=1):
                ttk.Label(review_frame, text=f"User: {username} | Rating: {rating} | Date: {date}", font=("Inter", 10)).grid(row=j, column=0, columnspan=2, padx=5, pady=2)
                ttk.Label(review_frame, text=f"Review: {content}", wraplength=400, justify="left").grid(row=j+1, column=0, columnspan=2, padx=5, pady=2)
        
        # Adjust pop-up window dimensions
        popup.geometry("")
        
    tree.bind("<<TreeviewSelect>>", on_treeview_select)

    def update_table(rows):
        for row in tree.get_children():
            tree.delete(row)
        for row in rows:
            tree.insert("", tk.END, values=row)
    
    # Load initial data
    restaurants = fetch_restaurants()
    update_table(restaurants)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    init_main_window()
