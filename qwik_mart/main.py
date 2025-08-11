import tkinter as tk
from signup import openSignupWindow
from login import openLoginWindow

def on_enter(e):
    e.widget.config(bg="#3E8E7E", fg="white")
def on_leave(e):
    e.widget.config(bg="#4CAF50", fg="white")

def openMainWindow():
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Qwik Mart")
    root.configure(bg="#f0f4f7")

    title_label = tk.Label(
        root,
        text="QWIK MART",
        font=("Helvetica", 48, "bold"),
        fg="#2c3e50",
        bg="#f0f4f7"
    )
    title_label.pack(pady=(60, 10))

    subtitle_label = tk.Label(
        root,
        text="Shop Smart. Shop Qwikly.",
        font=("Helvetica", 16, "italic"),
        fg="#7f8c8d",
        bg="#f0f4f7"
    )
    subtitle_label.pack(pady=(0, 40))

    signUpButton = tk.Button(
        root,
        text="🛒 New User? Sign Up",
        command=lambda: openSignupWindow(root),
        height=2,
        width=25,
        font=("Helvetica", 14, "bold"),
        bg="#4CAF50",
        fg="white",
        bd=0,
        relief="flat",
        cursor="hand2"
    )
    signUpButton.pack(pady=15)
    signUpButton.bind("<Enter>", on_enter)
    signUpButton.bind("<Leave>", on_leave)

    loginButton = tk.Button(
        root,
        text="🔑 Login",
        command=lambda: openLoginWindow(root),
        height=2,
        width=25,
        font=("Helvetica", 14, "bold"),
        bg="#2980b9",
        fg="white",
        bd=0,
        relief="flat",
        cursor="hand2"
    )
    loginButton.pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    openMainWindow()
