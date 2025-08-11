import tkinter as tk
from tkinter import messagebox, ttk, font
from dbConnection import createConnection
import mysql.connector
from datetime import datetime


def addProductToCart(customerWindow, customerId):

    def fetchProductInfo():
        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM product WHERE quantity > 0")
                products = cursor.fetchall()
                return products
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
                return []
            finally:
                cursor.close()
                connection.close()
        return []

    def addProducts(products, productIdEntry, quantityEntry, selectedProducts, uniqueProductIds, tree):
        productId = productIdEntry.get().strip()
        quantity = quantityEntry.get().strip()

        try:
            productId_int = int(productId)
        except ValueError:
            messagebox.showerror("Invalid Product ID", "Please enter a valid Product ID.")
            return

        if productId_int not in uniqueProductIds:
            messagebox.showerror("Invalid Product ID", "Please enter a valid Product ID.")
            return

        try:
            quantity_int = int(quantity)
            availableStock = 0
            for product in products:
                if product[0] == productId_int:
                    availableStock = product[4]
            if quantity_int <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0.")
                return
            elif quantity_int > availableStock:
                messagebox.showerror("Invalid Quantity", f"Quantity exceeds available stock ({availableStock}).")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer quantity.")
            return

        for product in products:
            if product[0] == productId_int:
                newProdTuple = (product[0], product[1], product[2], product[3], product[4] - quantity_int)
                products.remove(product)
                products.append(newProdTuple)
                break

        if productId_int in selectedProducts:
            selectedProducts[productId_int][2] += quantity_int
        else:
            selectedProducts[productId_int] = [product[1], product[2], quantity_int]

        for item in tree.get_children():
            tree.delete(item)
        for i, product in enumerate(products):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(product[0], product[1], product[2], product[4]), tags=(tag,))

        productIdEntry.delete(0, tk.END)
        quantityEntry.delete(0, tk.END)

    def submitProducts(selectedProducts):
        if len(selectedProducts) == 0:
            messagebox.showwarning("No products", "No products added to cart.")
            return False

        transactionAmtInfo = [(p[1], p[2]) for p in selectedProducts.values()]
        totalTransactionAmt = sum(price * quantity for price, quantity in transactionAmtInfo)

        transactionDate = datetime.today().strftime('%Y-%m-%d')

        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO transaction_details (transaction_date, amount) VALUES (%s, %s)",
                    (transactionDate, totalTransactionAmt)
                )
                lastTransactionId = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO cust_order (customer_id, transaction_id, order_date, order_status) VALUES (%s, %s, %s, %s)",
                    (customerId, lastTransactionId, transactionDate, "pending")
                )
                lastOrderId = cursor.lastrowid

                for prodId, prodData in selectedProducts.items():
                    cursor.execute(
                        "INSERT INTO order_item (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (lastOrderId, prodId, prodData[2], prodData[1])
                    )

                for prodId, prodData in selectedProducts.items():
                    cursor.execute("SELECT quantity FROM product WHERE product_id = %s", (prodId,))
                    result = cursor.fetchone()
                    updatedQty = result[0] - prodData[2]
                    cursor.execute("UPDATE product SET quantity = %s WHERE product_id = %s", (updatedQty, prodId))

                connection.commit()
                messagebox.showinfo("Success", "Customer Purchase done!")
                addProductToCartWindow.destroy()
                customerWindow.deiconify()
                return True

            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        return False

    def cancel():
        addProductToCartWindow.destroy()
        customerWindow.deiconify()

    addProductToCartWindow = tk.Toplevel(customerWindow)
    addProductToCartWindow.title("Add Product To Cart")
    addProductToCartWindow.geometry("950x650")
    addProductToCartWindow.resizable(True, True)

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=11)

    titleLabel = tk.Label(addProductToCartWindow, text="Add Products to Cart", font=("Helvetica", 18, "bold"), fg="#333")
    titleLabel.pack(pady=15)

    tableFrame = tk.Frame(addProductToCartWindow, bd=2, relief="groove")
    tableFrame.pack(padx=15, pady=(0, 15), fill="both", expand=True)

    columns = ("ID", "Name", "Price", "Available Quantity")
    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", selectmode="browse")

    tree.heading("ID", text="Product ID")
    tree.heading("Name", text="Product Name")
    tree.heading("Price", text="Price")
    tree.heading("Available Quantity", text="Available Quantity")

    tree.column("ID", width=100, anchor="center")
    tree.column("Name", width=250, anchor="w")
    tree.column("Price", width=120, anchor="center")
    tree.column("Available Quantity", width=180, anchor="center")

    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tableFrame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    style = ttk.Style()
    style.configure("Treeview", rowheight=26, font=("Helvetica", 11))
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    tree.tag_configure('oddrow', background='#f9f9f9')
    tree.tag_configure('evenrow', background='#e0e0e0')

    products = fetchProductInfo()
    productsReqFields = []
    uniqueProductIds = {}
    for product in products:
        productsReqFields.append((product[0], product[1], product[2], product[4]))
        uniqueProductIds[product[0]] = 1

    for i, product in enumerate(productsReqFields):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=product, tags=(tag,))

    inputFrame = tk.LabelFrame(addProductToCartWindow, text="Add Product to Cart", font=("Helvetica", 14, "bold"), padx=15, pady=15)
    inputFrame.pack(padx=15, pady=10, fill="x")

    tk.Label(inputFrame, text="Product ID:", font=("Helvetica", 12)).grid(row=0, column=0, padx=8, pady=8, sticky="e")
    productIdEntry = tk.Entry(inputFrame, font=("Helvetica", 12), width=30)
    productIdEntry.grid(row=0, column=1, padx=8, pady=8, sticky="w")

    tk.Label(inputFrame, text="Quantity:", font=("Helvetica", 12)).grid(row=1, column=0, padx=8, pady=8, sticky="e")
    quantityEntry = tk.Entry(inputFrame, font=("Helvetica", 12), width=30)
    quantityEntry.grid(row=1, column=1, padx=8, pady=8, sticky="w")

    selectedProducts = {}

    addButton = tk.Button(inputFrame, text="Add Product", bg="#28a745", fg="white", font=("Helvetica", 12, "bold"),
                          command=lambda: addProducts(products, productIdEntry, quantityEntry, selectedProducts, uniqueProductIds, tree))
    addButton.grid(row=2, column=0, columnspan=2, pady=15, sticky="ew")

    buttonsFrame = tk.Frame(addProductToCartWindow)
    buttonsFrame.pack(pady=15, padx=15, fill="x")

    submitButton = tk.Button(buttonsFrame, text="Submit", bg="#007bff", fg="white", font=("Helvetica", 13, "bold"),
                             command=lambda: submitProducts(selectedProducts))
    submitButton.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))

    cancelButton = tk.Button(buttonsFrame, text="Cancel", bg="#dc3545", fg="white", font=("Helvetica", 13, "bold"), command=cancel)
    cancelButton.pack(side=tk.LEFT, fill="x", expand=True, padx=(10, 0))

    customerWindow.withdraw()


def viewOrderHistory(customerWindow, customerId):

    def fetchOrderHistory():
        result = []
        connection = createConnection()
        if connection:
            cursor = connection.cursor()
            try:
                query = """
                SELECT order_id, order_date, order_status, amount, product_name, quantity FROM
                (SELECT temp3.order_id, order_date, order_status, amount, product_id, quantity FROM
                (SELECT order_id, order_date, order_status, amount FROM
                (SELECT * FROM cust_order WHERE customer_id = %s) AS temp
                LEFT JOIN
                (SELECT * FROM transaction_details) AS temp2
                ON temp.transaction_id = temp2.transaction_id) AS temp3
                LEFT JOIN
                (SELECT * FROM order_item) AS temp4
                ON temp3.order_id = temp4.order_id) AS temp5
                LEFT JOIN
                (SELECT product_id, product_name FROM product) AS temp6
                ON temp5.product_id = temp6.product_id;
                """
                cursor.execute(query, (customerId,))
                result = cursor.fetchall()
                messagebox.showinfo("Success", "Order History Visible!")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        return result

    viewOrderHistoryWindow = tk.Toplevel(customerWindow)
    viewOrderHistoryWindow.title("View Order History")
    viewOrderHistoryWindow.geometry("950x650")
    viewOrderHistoryWindow.resizable(True, True)

    titleLabel = tk.Label(viewOrderHistoryWindow, text="Order History", font=("Helvetica", 18, "bold"), fg="#333")
    titleLabel.pack(pady=15)

    tableFrame = tk.Frame(viewOrderHistoryWindow, bd=2, relief="groove")
    tableFrame.pack(padx=15, pady=10, fill="both", expand=True)

    columns = ("Order ID", "Order Date", "Order Status", "Transaction Amount", "Products")
    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", selectmode="browse")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tableFrame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    style = ttk.Style()
    style.configure("Treeview", rowheight=26, font=("Helvetica", 11))
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    tree.tag_configure('oddrow', background='#f9f9f9')
    tree.tag_configure('evenrow', background='#e0e0e0')

    orderHistory = fetchOrderHistory()
    orderHistoryDict = {}

    for order in orderHistory:
        orderId = order[0]
        if orderId in orderHistoryDict:
            orderHistoryDict[orderId][3].append((order[4], order[5]))
        else:
            orderDate = order[1].strftime("%Y-%m-%d")
            orderStatus = order[2]
            orderAmt = f"{order[3]:.2f}"
            orderHistoryDict[orderId] = [orderDate, orderStatus, orderAmt, [(order[4], order[5])]]

    for i, (orderId, (orderDate, orderStatus, orderAmt, products)) in enumerate(orderHistoryDict.items()):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(orderId, orderDate, orderStatus, orderAmt, products), tags=(tag,))

    inputFrame = tk.Frame(viewOrderHistoryWindow)
    inputFrame.pack(pady=15, padx=15, fill="x")

    cancelButton = tk.Button(inputFrame, text="Go Back", bg="#6c757d", fg="white", font=("Helvetica", 12, "bold"),
                             command=lambda: goBackToMainWindow(customerWindow, viewOrderHistoryWindow))
    cancelButton.pack(fill="x")

    customerWindow.withdraw()


def customerInterface(root, loginWindow, customerId):
    customerWindow = tk.Toplevel(loginWindow)
    customerWindow.title("Customer UI")
    customerWindow.geometry("400x320")
    customerWindow.resizable(False, False)

    titleLabel = tk.Label(customerWindow, text="Customer Dashboard", font=("Helvetica", 16, "bold"), fg="#333")
    titleLabel.pack(pady=20)

    btnAdd = tk.Button(customerWindow, text="Add Product", bg="#007bff", fg="white", font=("Helvetica", 12, "bold"),
                       width=25, height=2, command=lambda: addProductToCart(customerWindow, customerId))
    btnAdd.pack(pady=10)

    btnView = tk.Button(customerWindow, text="View Order History", bg="#17a2b8", fg="white", font=("Helvetica", 12, "bold"),
                        width=25, height=2, command=lambda: viewOrderHistory(customerWindow, customerId))
    btnView.pack(pady=10)

    btnLogout = tk.Button(customerWindow, text="Log out", bg="#dc3545", fg="white", font=("Helvetica", 12, "bold"),
                          width=25, height=2, command=lambda: goBackToMainWindow(root, customerWindow))
    btnLogout.pack(pady=10)

    loginWindow.withdraw()


def goBackToMainWindow(root, customerWindow):
    customerWindow.destroy()
    root.deiconify()
