import tkinter as tk
from tkinter import messagebox, ttk
from dbConnection import createConnection
import mysql.connector


def driverInterface(root, loginWindow, driverId):
    def fetchSameLocationOrders():
        result = []
        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT pincode FROM driver WHERE driver_id = %s", (driverId,))
                pincode = cursor.fetchone()[0]
                cursor.execute("""
                    SELECT first_name, last_name, order_id, order_date
                    FROM customer c
                    JOIN cust_order o ON c.customer_id = o.customer_id
                    WHERE c.pincode = %s AND o.order_status = "pending"
                """, (pincode,))
                result = cursor.fetchall()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        return result

    def selectOrders():
        orderId = orderIdEntry.get().strip()
        if not orderId.isdigit() or int(orderId) not in sameLocationOrdersDict:
            messagebox.showerror("Invalid", "Enter a valid Order ID from the list.")
            return
        if orderId not in selectedOrders:
            selectedOrders.append(orderId)
            selectedOrdersList.insert("", "end", values=(orderId,))
            for item in ordersTree.get_children():
                if str(ordersTree.item(item, "values")[2]) == orderId:
                    ordersTree.delete(item)
        orderIdEntry.delete(0, tk.END)

    def deliverSelectedOrders():
        if not selectedOrders:
            messagebox.showwarning("No Orders", "Please select at least one order.")
            return
        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                for orderId in selectedOrders:
                    cursor.execute("""
                        UPDATE cust_order 
                        SET driver_id = %s, order_status = 'delivered'
                        WHERE order_id = %s
                    """, (driverId, orderId))
                connection.commit()
                messagebox.showinfo("Success", "Orders marked as delivered!")
                selectedOrders.clear()
                selectedOrdersList.delete(*selectedOrdersList.get_children())
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
            finally:
                cursor.close()
                connection.close()

    def changePasswordWindow():
        pwWindow = tk.Toplevel(driverWindow)
        pwWindow.title("Change Password")
        pwWindow.geometry("400x250")
        pwWindow.configure(bg="#f4f4f4")

        tk.Label(pwWindow, text="Enter New Password:", font=("Arial", 12), bg="#f4f4f4").pack(pady=10)
        newPwEntry = tk.Entry(pwWindow, show="*", font=("Arial", 12), width=25)
        newPwEntry.pack(pady=5)

        tk.Label(pwWindow, text="Confirm New Password:", font=("Arial", 12), bg="#f4f4f4").pack(pady=10)
        confirmPwEntry = tk.Entry(pwWindow, show="*", font=("Arial", 12), width=25)
        confirmPwEntry.pack(pady=5)

        def updatePassword():
            new_pw = newPwEntry.get().strip()
            confirm_pw = confirmPwEntry.get().strip()

            if not new_pw:
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            if new_pw != confirm_pw:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            connection = createConnection()
            if connection:
                cursor = connection.cursor()
                try:
                    # First fetch username from driver table
                    cursor.execute("SELECT username FROM driver WHERE driver_id = %s", (driverId,))
                    result = cursor.fetchone()
                    if not result:
                        messagebox.showerror("Error", "Driver not found.")
                        return
                    username = result[0]

                    # Update password in credentials table
                    cursor.execute("""
                        UPDATE credentials 
                        SET pass_word = %s 
                        WHERE username = %s
                    """, (new_pw, username))
                    connection.commit()
                    messagebox.showinfo("Success", "Password updated successfully.")
                    pwWindow.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Error: {err}")
                finally:
                    cursor.close()
                    connection.close()

        tk.Button(pwWindow, text="Update Password", font=("Helvetica", 12, "bold"),
                  bg="#28a745", fg="white", width=18, command=updatePassword).pack(pady=20)

    driverWindow = tk.Toplevel(loginWindow)
    driverWindow.title("Driver Dashboard")
    driverWindow.geometry("900x650")
    driverWindow.configure(bg="#f4f4f4")
    driverWindow.grid_rowconfigure(1, weight=1)
    driverWindow.grid_columnconfigure(0, weight=1)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
    style.configure("Treeview", font=("Arial", 10), rowheight=25)

    headerLabel = tk.Label(driverWindow, text="Driver Dashboard", font=("Arial", 18, "bold"), bg="#f4f4f4")
    headerLabel.grid(row=0, column=0, pady=10)

    tableFrame = ttk.LabelFrame(driverWindow, text="Pending Orders", padding=10)
    tableFrame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
    tableFrame.grid_rowconfigure(0, weight=1)
    tableFrame.grid_columnconfigure(0, weight=1)

    columns = ("First Name", "Last Name", "Order ID", "Order Date")
    ordersTree = ttk.Treeview(tableFrame, columns=columns, show="headings", height=8)
    for col in columns:
        ordersTree.heading(col, text=col)
        ordersTree.column(col, width=150, anchor="center")
    ordersTree.grid(row=0, column=0, sticky="nsew")

    scroll_y = ttk.Scrollbar(tableFrame, orient="vertical", command=ordersTree.yview)
    ordersTree.configure(yscroll=scroll_y.set)
    scroll_y.grid(row=0, column=1, sticky="ns")

    sameLocationOrders = fetchSameLocationOrders()
    sameLocationOrdersDict = {}
    for first, last, oid, date in sameLocationOrders:
        sameLocationOrdersDict[oid] = [first, last, date.strftime("%Y-%m-%d")]
        ordersTree.insert("", "end", values=(first, last, oid, date.strftime("%Y-%m-%d")))

    actionFrame = ttk.LabelFrame(driverWindow, text="Select Orders to Deliver", padding=10)
    actionFrame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    tk.Label(actionFrame, text="Order ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    orderIdEntry = ttk.Entry(actionFrame)
    orderIdEntry.grid(row=0, column=1, padx=5, pady=5)

    addOrderBtn = tk.Button(actionFrame, text="Add Order", bg="#28a745", fg="white",
                            font=("Helvetica", 11, "bold"), padx=12, pady=5, command=selectOrders)
    addOrderBtn.grid(row=0, column=2, padx=10)

    selectedOrders = []
    selectedOrdersList = ttk.Treeview(actionFrame, columns=("Order ID",), show="headings", height=5)
    selectedOrdersList.heading("Order ID", text="Selected Order IDs")
    selectedOrdersList.column("Order ID", anchor="center", width=100)
    selectedOrdersList.grid(row=1, column=0, columnspan=3, pady=10)

    buttonFrame = tk.Frame(driverWindow, bg="#f4f4f4")
    buttonFrame.grid(row=3, column=0, pady=15)

    deliverBtn = tk.Button(buttonFrame, text="Deliver Orders", bg="#007bff", fg="white",
                           font=("Helvetica", 12, "bold"), width=15, pady=8, command=deliverSelectedOrders)
    deliverBtn.pack(side="left", padx=20)

    changePwBtn = tk.Button(buttonFrame, text="Change Password", bg="#ffc107", fg="black",
                            font=("Helvetica", 12, "bold"), width=15, pady=8, command=changePasswordWindow)
    changePwBtn.pack(side="left", padx=20)

    logoutBtn = tk.Button(buttonFrame, text="Log Out", bg="#dc3545", fg="white",
                          font=("Helvetica", 12, "bold"), width=15, pady=8,
                          command=lambda: goBackToMainWindow(root, driverWindow))
    logoutBtn.pack(side="left", padx=20)

    loginWindow.withdraw()


def goBackToMainWindow(root, driverWindow):
    driverWindow.destroy()
    root.deiconify()
