import tkinter as tk
from tkinter import messagebox
from dbConnection import createConnection
import mysql.connector

def signUpUser(firstName, lastName, username, password, email, phoneNo, houseNo, building, street, city, state, pincode):
    connection = createConnection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO credentials (username, pass_word) VALUES (%s, %s)",
                (username, password)
            )
            cursor.execute(
                "INSERT INTO customer (first_name, last_name, username, email, phone_no, house_no, building, street, city, state, pincode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (firstName, lastName, username, email, phoneNo, houseNo, building, street, city, state, pincode)
            )
            connection.commit()
            messagebox.showinfo("Success", "Signup Successful!")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()
    return False

def openSignupWindow(root):
    signUpWindow = tk.Toplevel(root)
    signUpWindow.geometry("800x600")
    signUpWindow.title("Sign Up")
    signUpWindow.configure(bg="#f0f4f7")

    form_frame = tk.Frame(signUpWindow, bg="white", padx=30, pady=20, relief="raised", bd=2)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(form_frame, text="📝 Create Your Qwik Mart Account", font=("Helvetica", 18, "bold"), bg="white", fg="#2c3e50")
    title.grid(row=0, column=0, columnspan=2, pady=(0, 15))

    fields = [
        ("First Name", tk.StringVar()),
        ("Last Name", tk.StringVar()),
        ("Username", tk.StringVar()),
        ("Password", tk.StringVar()),
        ("Email", tk.StringVar()),
        ("Phone No", tk.StringVar()),
        ("House No", tk.StringVar()),
        ("Building", tk.StringVar()),
        ("Street", tk.StringVar()),
        ("City", tk.StringVar()),
        ("State", tk.StringVar()),
        ("Pincode", tk.StringVar()),
    ]

    entries = {}
    for i, (label_text, var) in enumerate(fields, start=1):
        label = tk.Label(form_frame, text=label_text, font=("Helvetica", 11), bg="white", anchor="w")
        label.grid(row=i, column=0, sticky="w", pady=5)
        
        show_char = "*" if label_text == "Password" else ""
        entry = tk.Entry(form_frame, textvariable=var, font=("Helvetica", 11), relief="solid", bd=1, show=show_char, width=30)
        entry.grid(row=i, column=1, pady=5, padx=(10, 0))
        entries[label_text] = var

    def signup():
        if any(not v.get().strip() for v in entries.values()):
            messagebox.showwarning("Validation Error", "All fields are mandatory. Please fill in all fields.")
            return

        if signUpUser(
            entries["First Name"].get(),
            entries["Last Name"].get(),
            entries["Username"].get(),
            entries["Password"].get(),
            entries["Email"].get(),
            entries["Phone No"].get(),
            entries["House No"].get(),
            entries["Building"].get(),
            entries["Street"].get(),
            entries["City"].get(),
            entries["State"].get(),
            entries["Pincode"].get()
        ):
            signUpWindow.destroy()
            root.deiconify()

    signup_btn = tk.Button(form_frame, text="Sign Up", font=("Helvetica", 12, "bold"), bg="#27ae60", fg="white", relief="flat", width=20, command=signup)
    signup_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=15)

    back_btn = tk.Button(form_frame, text="⬅ Back to Main Window", font=("Helvetica", 10), bg="#95a5a6", fg="white", relief="flat", command=lambda: goBackToMainWindow(root, signUpWindow))
    back_btn.grid(row=len(fields)+2, column=0, columnspan=2)

    root.withdraw()

def goBackToMainWindow(root, signUpWindow):
    signUpWindow.destroy()
    root.deiconify()
