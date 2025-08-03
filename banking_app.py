import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib

# Database Setup
def connect_db():
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            balance REAL DEFAULT 0.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            type TEXT,
            amount REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
connect_db()

def send_cash():
    pass


# Hash Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register User
def register_user():
    username = entry_username.get()
    password = entry_password.get()
    if not username or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    hashed_pw = hash_password(password)
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    conn.close()

def login_user():
    username = entry_username.get()
    password = entry_password.get()
    hashed_pw = hash_password(password)
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    if user:
        open_dashboard(username, user[0])
    else:
        messagebox.showerror("Error", "Invalid credentials!")

def open_dashboard(username, balance):
    root.withdraw()  # Hide login window
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("400x400")
    dashboard.config(bg="pink")
    
    tk.Label(dashboard, text=f"Welcome, {username}", font=("High Tower", 14)).pack()
    balance_label = tk.Label(dashboard, text=f"Balance: ${balance:.2f}", font=("Arial", 12))
    balance_label.pack()
    tk.Button(frame, text = "Send", command=send_cash, bg="#333333", fg="white", width=15).pack(pady=5)


    def deposit():
        amount = float(entry_deposit.get())
        if amount > 0:
            new_balance = balance + amount
            update_balance(username, new_balance)
            record_transaction(username, "Deposit", amount)
            balance_label.config(text=f"Balance: ${new_balance:.2f}")
            messagebox.showinfo("Success", "Deposit successful!")
        else:
            messagebox.showerror("Error", "Enter a valid amount")
    
    tk.Label(dashboard, text="Deposit Amount: ").pack()
    entry_deposit = tk.Entry(dashboard)
    entry_deposit.pack()
    tk.Button(dashboard, text="Deposit", command=deposit).pack()
    
    def withdraw():
        amount = float(entry_withdraw.get())
        if amount > 0 and amount <= balance:
            new_balance = balance - amount
            update_balance(username, new_balance)
            record_transaction(username, "Withdraw", amount)
            balance_label.config(text=f"Balance: ${new_balance:.2f}")
            messagebox.showinfo("Success", "Withdrawal successful!")
        else:
            messagebox.showerror("Error", "Insufficient funds in your account")
    
    tk.Label(dashboard, text="Withdraw Amount: ").pack()
    entry_withdraw = tk.Entry(dashboard)
    entry_withdraw.pack()
    tk.Button(dashboard, text="Withdraw", command=withdraw).pack()
    
    def show_transactions():
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT type, amount, timestamp FROM transactions WHERE username=? ORDER BY timestamp DESC", (username,))
        transactions = cursor.fetchall()
        conn.close()
        
        transaction_window = tk.Toplevel()
        transaction_window.title("Transaction History")
        
        tk.Label(transaction_window, text="Transaction History", font=("Arial", 14)).pack()
        for t in transactions:
            tk.Label(transaction_window, text=f"{t[2]} - {t[0]}: ${t[1]:.2f}").pack()
    
    tk.Button(dashboard, text="View Transaction History", command=show_transactions).pack()

def update_balance(username, new_balance):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
    conn.commit()
    conn.close()

def record_transaction(username, trans_type, amount):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (username, type, amount) VALUES (?, ?, ?)", (username, trans_type, amount))
    conn.commit()
    conn.close()







# Styled Login/Register Window
root = tk.Tk()
root.title("Banking App")
root.geometry("400x300")
root.configure(bg="indigo")

frame = tk.Frame(root, bg="yellow", padx=20, pady=20, relief="ridge", bd=5)
frame.pack(pady=50)

tk.Label(frame, text="Banking App", font=("Arial", 16, "bold"), bg="magenta").pack(pady=10)

tk.Label(frame, text="Username:", bg="white",anchor="w").pack()
entry_username = tk.Entry(frame, width=30)
entry_username.pack(pady=5)

tk.Label(frame, text="Password:", bg="white").pack()
entry_password = tk.Entry(frame, width=30, show="*")
entry_password.pack(pady=5)

tk.Button(frame, text="Register", command=register_user, bg="#4CAF50", fg="white", width=15).pack(pady=5)
tk.Button(frame, text="Login", command=login_user, bg="#008CBA", fg="white", width=15).pack(pady=5)

root.mainloop()
