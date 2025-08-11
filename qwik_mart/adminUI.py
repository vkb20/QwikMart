import tkinter as tk
from tkinter import messagebox
from dbConnection import createConnection
import mysql.connector

def create_labeled_entry(parent, text, row, show=None):
    label = tk.Label(parent, text=text, font=("Arial", 12))
    label.grid(row=row, column=0, sticky="w", pady=5, padx=10)
    entry = tk.Entry(parent, show=show, font=("Arial", 12), width=30)
    entry.grid(row=row, column=1, pady=5, padx=10)
    return entry

def addProductWindow(adminWindow):
    productWindow = tk.Toplevel(adminWindow)
    productWindow.title("Add Product")
    productWindow.geometry("500x400")
    productWindow.configure(bg="#f4f4f4")

    header = tk.Label(productWindow, text="Add / Update Product", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
    header.pack(pady=15)

    form_frame = tk.Frame(productWindow, bg="#f4f4f4")
    form_frame.pack(pady=10)

    productID = create_labeled_entry(form_frame, "Product ID:", 0)
    productName = create_labeled_entry(form_frame, "Product Name:", 1)
    productPrice = create_labeled_entry(form_frame, "Product Price:", 2)
    productType = create_labeled_entry(form_frame, "Product Type:", 3)
    productQty = create_labeled_entry(form_frame, "Product Quantity:", 4)

    def submitProduct():
        try:
            pid = int(productID.get())
            qty = int(productQty.get())
            price = float(productPrice.get())
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be integer & Price must be numeric")
            return

        if not productName.get() or not productType.get():
            messagebox.showerror("Input Error", "All fields are required")
            return

        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM product WHERE product_id = %s", (pid,))
                result = cursor.fetchone()
                if result:
                    qty += result[4]
                    cursor.execute("""
                        UPDATE product 
                        SET product_name=%s, product_price=%s, product_type=%s, quantity=%s
                        WHERE product_id=%s
                    """, (productName.get(), price, productType.get(), qty, pid))
                    messagebox.showinfo("Success", "Product quantity updated")
                else:
                    cursor.execute("INSERT INTO product VALUES (%s, %s, %s, %s, %s)",
                                   (pid, productName.get(), price, productType.get(), qty))
                    messagebox.showinfo("Success", "Product added successfully")
                connection.commit()
                productWindow.destroy()
                adminWindow.deiconify()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))
            finally:
                cursor.close()
                connection.close()

    tk.Button(productWindow, text="Save Product", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=20, command=submitProduct).pack(pady=15)
    tk.Button(productWindow, text="Back", font=("Arial", 12), command=lambda: goBackToAdminWindow(adminWindow, productWindow)).pack()

    adminWindow.withdraw()

def addDriverWindow(adminWindow):
    driverWindow = tk.Toplevel(adminWindow)
    driverWindow.title("Add Driver")
    driverWindow.geometry("500x650")
    driverWindow.configure(bg="#f4f4f4")

    header = tk.Label(driverWindow, text="Register New Driver", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
    header.pack(pady=15)

    form_frame = tk.Frame(driverWindow, bg="#f4f4f4")
    form_frame.pack(pady=10)

    firstName = create_labeled_entry(form_frame, "First Name:", 0)
    lastName = create_labeled_entry(form_frame, "Last Name:", 1)
    username = create_labeled_entry(form_frame, "Username:", 2)
    password = create_labeled_entry(form_frame, "Password:", 3, show="*")
    email = create_labeled_entry(form_frame, "Email:", 4)
    phoneNo = create_labeled_entry(form_frame, "Phone No:", 5)
    houseNo = create_labeled_entry(form_frame, "House No:", 6)
    building = create_labeled_entry(form_frame, "Building:", 7)
    street = create_labeled_entry(form_frame, "Street:", 8)
    city = create_labeled_entry(form_frame, "City:", 9)
    state = create_labeled_entry(form_frame, "State:", 10)
    pincode = create_labeled_entry(form_frame, "Pincode:", 11)

    def signUpDriver():
        if not all([firstName.get(), lastName.get(), username.get(), password.get(), email.get(), phoneNo.get(),
                    houseNo.get(), building.get(), street.get(), city.get(), state.get(), pincode.get()]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return

        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO credentials VALUES (%s, %s)", (username.get(), password.get()))
                cursor.execute("""
                    INSERT INTO driver (first_name, last_name, username, email, phone_no, house_no, building, street, city, state, pincode)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (firstName.get(), lastName.get(), username.get(), email.get(), phoneNo.get(),
                      houseNo.get(), building.get(), street.get(), city.get(), state.get(), pincode.get()))
                connection.commit()
                messagebox.showinfo("Success", "Driver registered")
                driverWindow.destroy()
                adminWindow.deiconify()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))
            finally:
                cursor.close()
                connection.close()

    tk.Button(driverWindow, text="Register Driver", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=20, command=signUpDriver).pack(pady=15)
    tk.Button(driverWindow, text="Back", font=("Arial", 12), command=lambda: goBackToAdminWindow(adminWindow, driverWindow)).pack()

    adminWindow.withdraw()

def adminInterface(root, loginWindow):
    adminWindow = tk.Toplevel(loginWindow)
    adminWindow.title("Admin Dashboard")
    adminWindow.geometry("400x300")
    adminWindow.configure(bg="#e8f0fe")

    tk.Label(adminWindow, text="Admin Dashboard", font=("Helvetica", 18, "bold"), bg="#e8f0fe").pack(pady=20)

    tk.Button(adminWindow, text="Add Product", font=("Arial", 12), bg="#2196F3", fg="white", width=20, command=lambda: addProductWindow(adminWindow)).pack(pady=10)
    tk.Button(adminWindow, text="Add Driver", font=("Arial", 12), bg="#FF9800", fg="white", width=20, command=lambda: addDriverWindow(adminWindow)).pack(pady=10)
    tk.Button(adminWindow, text="Log Out", font=("Arial", 12), bg="#f44336", fg="white", width=20, command=lambda: goBackToMainWindow(root, adminWindow)).pack(pady=20)

    loginWindow.withdraw()

def goBackToMainWindow(root, adminWindow):
    adminWindow.destroy()
    root.deiconify()

def goBackToAdminWindow(adminWindow, childWindow):
    childWindow.destroy()
    adminWindow.deiconify()
