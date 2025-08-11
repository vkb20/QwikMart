import tkinter as tk
from tkinter import messagebox
from dbConnection import createConnection
import mysql.connector
from adminUI import adminInterface
from driverUI import driverInterface
from customerUI import customerInterface


def loginUser(username, password, root, loginWindow):
    connection = createConnection()
    if connection:
        cursor = connection.cursor()
        try:
            queryCredentials = "SELECT * FROM credentials WHERE username = %s AND pass_word = %s"
            cursor.execute(queryCredentials, (username, password))
            exists = cursor.fetchone()
            if exists:
                queryAdmin = "SELECT * FROM admin_user WHERE admin_username = %s"
                cursor.execute(queryAdmin, (username,))
                existsInAdmin = cursor.fetchone()
                if existsInAdmin:
                    adminInterface(root, loginWindow)
                else:
                    queryCustomer = "SELECT * FROM customer WHERE username = %s"
                    cursor.execute(queryCustomer, (username,))
                    existsInCustomer = cursor.fetchone()
                    if existsInCustomer:
                        customerId = existsInCustomer[0]
                        customerInterface(root, loginWindow, customerId)
                    else:
                        queryDriver = "SELECT * FROM driver WHERE username = %s"
                        cursor.execute(queryDriver, (username,))
                        existsInDriver = cursor.fetchone()
                        if existsInDriver:
                            driverInterface(root, loginWindow, existsInDriver[0])
                        else:
                            messagebox.showinfo("Info", "Credentials exist in credentials but not in DB")
            else:
                messagebox.showerror("Login Failed", "User doesn't exist or incorrect credentials!")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()
    return False


def openLoginWindow(root):
    loginWindow = tk.Toplevel(root)
    loginWindow.geometry("800x600")
    loginWindow.title("Login")
    loginWindow.configure(bg="#f0f4f7")

    frame = tk.Frame(loginWindow, bg="white", padx=40, pady=40, relief="raised", bd=2)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    title_label = tk.Label(frame, text="🔑 Login to Qwik Mart", font=("Helvetica", 20, "bold"), fg="#2c3e50", bg="white")
    title_label.pack(pady=(0, 20))

    tk.Label(frame, text="Username", font=("Helvetica", 12), bg="white").pack(anchor="w")
    username = tk.Entry(frame, font=("Helvetica", 12), width=30, relief="solid", bd=1)
    username.pack(pady=(0, 15))

    tk.Label(frame, text="Password", font=("Helvetica", 12), bg="white").pack(anchor="w")
    password_var = tk.StringVar()
    password_entry = tk.Entry(frame, textvariable=password_var, show="*", font=("Helvetica", 12), width=30, relief="solid", bd=1)
    password_entry.pack(pady=(0, 5))

    def toggle_password():
        if password_entry.cget("show") == "":
            password_entry.config(show="*")
            toggle_btn.config(text="Show")
        else:
            password_entry.config(show="")
            toggle_btn.config(text="Hide")

    toggle_btn = tk.Button(frame, text="Show", command=toggle_password, font=("Helvetica", 8), bg="#bdc3c7", relief="flat", width=5)
    toggle_btn.pack(pady=(0, 15))

    login_btn = tk.Button(
        frame,
        text="Login",
        font=("Helvetica", 12, "bold"),
        bg="#2980b9",
        fg="white",
        width=20,
        height=1,
        relief="flat",
        command=lambda: login()
    )
    login_btn.pack(pady=10)

    back_btn = tk.Button(
        frame,
        text="⬅ Back to Main Window",
        font=("Helvetica", 10),
        bg="#95a5a6",
        fg="white",
        relief="flat",
        command=lambda: goBackToMainWindow(root, loginWindow)
    )
    back_btn.pack(pady=5)

    def login():
        if not (username.get() and password_var.get()):
            messagebox.showwarning("Validation Error", "All fields are mandatory. Please fill in all fields.")
            return
        loginUser(username.get(), password_var.get(), root, loginWindow)

    root.withdraw()


def goBackToMainWindow(root, loginWindow):
    loginWindow.destroy()
    root.deiconify()
