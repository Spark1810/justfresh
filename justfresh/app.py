import streamlit as st
import sqlite3
from PIL import Image
import pandas as pd
import hashlib



# Initialize an empty product list
products = []
shopping_cart = []

# Create a new SQLite database for products
products_conn = sqlite3.connect('products_data.db')
products_cursor = products_conn.cursor()
products_cursor.execute('CREATE TABLE IF NOT EXISTS productstable(name TEXT, price REAL, seller TEXT, image_url TEXT)')
products_conn.commit()

def add_product_screen():
    st.subheader("Add Product")
    name = st.text_input("Product Name:")
    price = st.number_input("Product Price ($):", min_value=0.01, value=1.0)
    seller = st.text_input("Seller:")
    image_url = st.text_input("Image URL:")

    if st.button("Add Product"):
        # Add the product to the SQLite database
        products_cursor.execute('INSERT INTO productstable(name, price, seller, image_url) VALUES (?, ?, ?, ?)', (name, price, seller, image_url))
        products_conn.commit()

        new_product = {"name": name, "price": price, "seller": seller, "image": image_url}
        products.append(new_product)
        st.success(f"Product '{name}' added successfully!")


def purchase_screen():
    st.subheader("Purchase Products")

    # Retrieve products from the SQLite database
    products_cursor.execute('SELECT * FROM productstable')
    stored_products = products_cursor.fetchall()

    if not stored_products:
        st.warning("No products available. Please add products in the 'Add Product' screen.")
    else:
        selected_product = st.selectbox("Select Product:", [product[0] for product in stored_products])
        quantity = st.number_input("Quantity:", min_value=1, value=1)

        if st.button("Add to Cart"):
            # Find the selected product in the stored products
            selected_product_info = next((product for product in stored_products if product[0] == selected_product), None)
            
            if selected_product_info:
                name, price, seller, image_url = selected_product_info
                product = {"name": name, "price": price, "seller": seller, "image": image_url}
                
                for _ in range(quantity):
                    shopping_cart.append(product)
                st.success(f"{quantity} {product['name']}(s) added to the cart!")

def cart_screen():
    st.subheader("Shopping Cart")
    total_price = sum(item['price'] for item in shopping_cart)
    st.write(f"Total Items in Cart: {len(shopping_cart)}")
    st.write(f"Total Price: ${total_price:.2f}")

    if st.button("Checkout"):
        st.success("Checkout successful! Thank you for shopping with JustFresh.")




def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def create_usertable():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

def view_all_users():
    try:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM userstable')
        data = c.fetchall()
        return data
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        conn.close()

def main():
    st.markdown("<h1 style='text-align: center; color: green;'>Just-Fresh</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: green;'>Tagline</h4>", unsafe_allow_html=True)

    menu = ["HOME", "ADMIN LOGIN", "USER LOGIN", "SIGN UP", "ABOUT US"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "HOME":
        st.markdown("<h1 style='text-align: center;'>HOMEPAGE</h1>", unsafe_allow_html=True)
        image = Image.open(r"image.jfif")
        st.image(image, caption='', use_column_width=True)
        st.subheader("Description")
        st.warning("Go to Menu Section To Login!")

    elif choice == "ADMIN LOGIN":
        st.markdown("<h1 style='text-align: center;'>Admin Login Section</h1>", unsafe_allow_html=True)
        admin_user = st.sidebar.text_input('Admin Username')
        admin_passwd = st.sidebar.text_input('Admin Password', type='password')
        
        if st.sidebar.checkbox("LOGIN"):
            if admin_user == "Admin" and admin_passwd == 'admin123':
                st.success(f"Logged In as {admin_user}")
                admin_task = st.selectbox("Admin Task", ["Shop", "View User Profiles"])
                
                if admin_task == "Shop":
                    add_products()
                elif admin_task == "View User Profiles":
                    st.subheader("User Profiles")
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result, columns=["Username", "Password"])
                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Admin Username/Password")

    elif choice == "USER LOGIN":
        st.markdown("<h1 style='text-align: center;'>User Login Section</h1>", unsafe_allow_html=True)
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        
        if st.sidebar.checkbox("LOGIN"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username, check_hashes(password, hashed_pswd))
            
            if result:
                st.success(f"Logged In as {username}")
            else:
                st.warning("Incorrect Username/Password. Please Create an Account if not Created")

    elif choice == "SIGN UP":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("SIGN UP"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to User Login Menu to login")

    elif choice == "ABOUT US":
        st.header("CREATED BY _**NirubhaSri**_")

def add_products():
    st.subheader("Shop Section")
    st.title("JustFresh - Online Fresh Produce Marketplace")

    # Sidebar navigation
    menu = ["Add Product", "Purchase", "Cart"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # Render selected screen
    if choice == "Add Product":
        add_product_screen()
    elif choice == "Purchase":
        purchase_screen()
    elif choice == "Cart":
        cart_screen()

    # Display product catalog
    st.subheader("Product Catalog:")
    for product in products:
        st.write(f"**{product['name']}**")
        st.image(product['image'], caption=product['name'], use_column_width=True)
        st.write(f"Price: ${product['price']:.2f} - Seller: {product['seller']}")
        st.write("---")


if __name__ == '__main__':
    main()
