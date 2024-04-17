import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv
from datetime import datetime

class BankingApp(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title("Banking Application")
        self.geometry("400x300")
        self.current_screen = None
        self.history = []
        self.db_conn = sqlite3.connect("banking.db")
        self.create_tables()
        self.create_start_screen()
    def change_screen(self, new_screen):
        if self.current_screen is not None:
            self.current_screen.pack_forget()
        self.current_screen = new_screen
        self.current_screen.pack(expand=True, fill=tk.BOTH)
        print("Screen changed to", new_screen)
    def go_back(self):
        if self.history:
            previous_screen = self.history.pop()
            self.current_screen.pack_forget()
            self.current_screen = previous_screen
            self.current_screen.pack(expand=True, fill=tk.BOTH)
            print("Returned to", previous_screen)

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            account_type TEXT NOT NULL,
                            balance REAL NOT NULL
                            )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                            id INTEGER PRIMARY KEY,
                            account_number TEXT NOT NULL,
                            user_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY,
                            account_number TEXT NOT NULL,
                            transaction_type TEXT NOT NULL,
                            amount REAL NOT NULL,
                            transaction_date TEXT NOT NULL,
                            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
                            )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS services (
                            id INTEGER PRIMARY KEY,
                            service_name TEXT NOT NULL,
                            user_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            )''')
        self.db_conn.commit()

    def update_csv_file(self, data, filename='transactions.csv'):
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

    def change_screen(self, new_screen):
        if self.current_screen:
            self.current_screen.pack_forget()

        self.history.append(self.current_screen)
        self.current_screen = new_screen
        self.current_screen.pack()



    def go_back(self):
        if self.history:
            previous_screen = self.history.pop()
            if self.current_screen:
                    self.current_screen.pack_forget()
            self.current_screen = previous_screen
            self.current_screen.pack()

    def create_start_screen(self):
        self.start_screen = tk.Frame(self)
        tk.Label(self.start_screen, text="Are you a new customer?").pack()
        tk.Button(self.start_screen, text="Yes", command=self.create_new_customer_screen).pack()
        tk.Button(self.start_screen, text="No", command=self.create_login_screen).pack()
        self.change_screen(self.start_screen)

    def create_new_customer_screen(self):
        self.new_customer_screen = tk.Frame(self)
        tk.Label(self.new_customer_screen, text="Enter new username:").pack()
        self.new_username_entry = tk.Entry(self.new_customer_screen)
        self.new_username_entry.pack()
        tk.Label(self.new_customer_screen, text="Enter new password:").pack()
        self.new_password_entry = tk.Entry(self.new_customer_screen, show="*")
        self.new_password_entry.pack()
        tk.Button(self.new_customer_screen, text="Create Account", command=self.create_account).pack()
        self.change_screen(self.new_customer_screen)

    def create_account(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Username Taken", "Username already exists. Please choose a different one.")
            return
        cursor.execute("INSERT INTO users (username, password, account_type, balance) VALUES (?, ?, ?, ?)",
                       (username, password, 'Personal', 0.0))
        user_id = cursor.lastrowid
        account_number = self.generate_account_number()
        cursor.execute("INSERT INTO accounts (account_number, user_id) VALUES (?, ?)",
                       (account_number, user_id))
        self.db_conn.commit()
        self.update_csv_file([user_id, username, account_number, 0.0, 'New Account'], 'accounts_log.csv')
        messagebox.showinfo("Account Created", f"Your account has been created successfully. Your account number is: {account_number}")
        self.create_login_screen()

    def generate_account_number(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        return f"ACC{count + 1:06d}"

    def create_login_screen(self):
        self.login_screen = tk.Frame(self)
        tk.Label(self.login_screen, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_screen)
        self.username_entry.pack()
        tk.Label(self.login_screen, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_screen, show="*")
        self.password_entry.pack()
        tk.Button(self.login_screen, text="Login", command=self.login).pack()
        self.change_screen(self.login_screen)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            self.create_main_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def create_main_menu(self):
        self.main_menu_screen = tk.Frame(self)
        tk.Label(self.main_menu_screen, text="Main Menu").pack()

        tk.Button(self.main_menu_screen, text="Account Management", command=self.create_account_management_screen).pack()
        tk.Button(self.main_menu_screen, text="Financial Transactions", command=self.create_financial_transactions_screen).pack()
        tk.Button(self.main_menu_screen, text="Account Services", command=self.create_account_services_screen).pack()
        tk.Button(self.main_menu_screen, text="Security and Compliance", command=self.create_security_screen).pack()

        tk.Button(self.main_menu_screen, text="Logout", command=self.logout).pack()
        self.change_screen(self.main_menu_screen)


    def create_account_management_screen(self):
        self.account_management_screen = tk.Frame(self)
        tk.Label(self.account_management_screen, text="Account Management").pack()
        tk.Button(self.account_management_screen, text="View Account Information", command=self.view_account_info_screen).pack()
        tk.Button(self.account_management_screen, text="Request Checkbook", command=self.request_checkbook).pack()
        tk.Button(self.account_management_screen, text="Request Card", command=self.request_card).pack()
        tk.Button(self.account_management_screen, text="Two-Factor Authentication", command=self.two_factor_auth_screen).pack()
        tk.Button(self.account_management_screen, text="Data Encryption", command=self.data_encryption_screen).pack()
        tk.Button(self.account_management_screen, text="Transaction History", command=self.transaction_history_screen).pack()
        tk.Button(self.account_management_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.account_management_screen)
    def create_financial_transactions_screen(self):
        self.financial_transactions_screen = tk.Frame(self)
        tk.Label(self.financial_transactions_screen, text="Financial Transactions").pack()

        tk.Button(self.financial_transactions_screen, text="Deposit Cash", command=self.deposit_cash_screen).pack()
        tk.Button(self.financial_transactions_screen, text="Withdraw Cash", command=self.withdraw_cash_screen).pack()

        tk.Button(self.financial_transactions_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.financial_transactions_screen)


    def create_account_services_screen(self):
        self.account_services_screen = tk.Frame(self)
        tk.Label(self.account_services_screen, text="Account Services").pack()
        tk.Button(self.account_services_screen, text="Service 1", command=self.service_1).pack()
        tk.Button(self.account_services_screen, text="Service 2", command=self.service_2).pack()
        tk.Button(self.account_services_screen, text="Service 3", command=self.service_3).pack()
        tk.Button(self.account_services_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.account_services_screen)
    def service_1(self):
    # This message box is for additional confirmation, can be removed if not needed
        response = messagebox.askyesno("Delete Account", "Are you sure you want to proceed with account deletion?")
        if response:
            self.delete_account()  # Call the delete_account method when the user confirms
        else:
            messagebox.showinfo("Operation Cancelled", "Account deletion cancelled.")

    def service_2(self):
        messagebox.showinfo("Service 2", "Service 2 is under construction.")
    def service_3(self):
        messagebox.showinfo("Service 3", "Service 3 is under construction.")
    def delete_account(self):
        response = messagebox.askyesno("Delete Account", "Are you sure you want to delete your account permanently?")
        if not response:
            messagebox.showinfo("Operation Cancelled", "Account deletion cancelled.")
            return

        account_number = self.generate_account_number()
        if not account_number:
            messagebox.showerror("Error", "Account number not found.")
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE account_number=?", (account_number,))
            cursor.execute("DELETE FROM accounts WHERE account_number=?", (account_number,))
            cursor.execute("SELECT user_id FROM accounts WHERE account_number=?", (account_number,))
            user_id = cursor.fetchone()
            if user_id:
                cursor.execute("DELETE FROM users WHERE id=?", (user_id[0],))
            self.db_conn.commit()
            self.update_csv_file(['Account Deletion', account_number, datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 'deletions_log.csv')
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
            self.logout()
        except Exception as e:
            messagebox.showerror("Deletion Failed", f"An error occurred: {str(e)}")
            self.db_conn.rollback()

    def logout(self):
        if self.current_screen:
            self.current_screen.pack_forget()
        self.create_start_screen()

    def create_security_screen(self):
        self.security_screen = tk.Frame(self)
        tk.Label(self.security_screen, text="Security and Compliance").pack()
        tk.Button(self.security_screen, text="Enable Two-Factor Authentication", command=self.two_factor_auth_screen).pack()
        tk.Button(self.security_screen, text="Data Encryption", command=self.data_encryption_screen).pack()
        tk.Button(self.security_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.security_screen)
    

    def logout(self):
        self.current_screen.destroy()
        self.create_start_screen()
    def deposit_cash_screen(self):
        self.deposit_cash_screen = tk.Frame(self)
        tk.Label(self.deposit_cash_screen, text="Enter amount to deposit:").pack()
        self.deposit_amount_entry = tk.Entry(self.deposit_cash_screen)
        self.deposit_amount_entry.pack()
        tk.Button(self.deposit_cash_screen, text="Deposit", command=self.deposit_cash).pack()
        tk.Button(self.deposit_cash_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.deposit_cash_screen)
    def withdraw_cash_screen(self):
        self.withdraw_cash_screen = tk.Frame(self)
        tk.Label(self.withdraw_cash_screen, text="Enter amount to withdraw:").pack()
        self.withdraw_amount_entry = tk.Entry(self.withdraw_cash_screen)
        self.withdraw_amount_entry.pack()
        tk.Button(self.withdraw_cash_screen, text="Withdraw", command=self.withdraw_cash).pack()
        tk.Button(self.withdraw_cash_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.withdraw_cash_screen)

    def withdraw_cash(self):
        amount_str = self.withdraw_amount_entry.get()
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive amount.")
            return

    # Retrieve the account number from the current logged-in session (assuming you store it upon login)
        if not hasattr(self, 'current_account_number'):
            messagebox.showerror("Session Error", "No active session found.")
            return

    # Use the existing account number
        account_number = self.current_account_number
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
        result = cursor.fetchone()
        if result is None:
            messagebox.showerror("Account Error", "Account not found.")
            return

        balance = result[0]
        if amount > balance:
            messagebox.showerror("Insufficient Funds", "Your account balance is too low.")
            return

    # Proceed with the withdrawal
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_number = ?", (amount, account_number))
        cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, transaction_date) VALUES (?, 'Withdraw', ?, ?)",
                   (account_number, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.db_conn.commit()
        self.update_csv_file([account_number, 'Withdraw', amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        messagebox.showinfo("Withdrawal", f"Amount ${amount} withdrawn successfully.")



    def deposit_cash(self):
        amount = self.deposit_amount_entry.get()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive amount.")
            return

        account_number = self.generate_account_number()
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = (SELECT user_id FROM accounts WHERE account_number = ?)", (amount, account_number))
        cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, transaction_date) VALUES (?, 'Deposit', ?, ?)",
                   (account_number, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.db_conn.commit()
        self.update_csv_file([account_number, 'Deposit', amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        messagebox.showinfo("Deposit", f"Amount ${amount} deposited successfully.")
    def view_account_info_screen(self):
    # This method assumes you have a way to identify the currently logged-in user's ID or account number
    # Let's assume you store the logged-in user's ID or account number when they log in
        if not hasattr(self, 'current_user_id'):
            messagebox.showerror("Account Error", "No user is currently logged in.")
            return

        cursor = self.db_conn.cursor()
    # Adjust this query to match your database schema:
        cursor.execute("SELECT username, balance, account_number FROM users JOIN accounts ON users.id = accounts.user_id WHERE users.id = ?", (self.current_user_id,))
        user_info = cursor.fetchone()
        if user_info:
            username, balance, account_number = user_info
            message = f"Username: {username}\nAccount Number: {account_number}\nBalance: ${balance}"
            messagebox.showinfo("Account Information", message)
        else:
            messagebox.showerror("Account Error", "Failed to retrieve account information.")

    def request_checkbook(self):
        messagebox.showinfo("Request Sent", "Your checkbook request has been sent successfully.")
        self.update_csv_file(['Checkbook Request', self.generate_account_number()])

    def request_card(self):
        messagebox.showinfo("Request Sent", "Your debit/credit card request has been sent successfully.")
        self.update_csv_file(['Card Request', self.generate_account_number()])
    def two_factor_auth_screen(self):
        self.two_factor_auth_screen = tk.Frame(self)
        tk.Label(self.two_factor_auth_screen, text="Enter the code sent to your email:").pack()
        self.auth_code_entry = tk.Entry(self.two_factor_auth_screen)
        self.auth_code_entry.pack()
        tk.Button(self.two_factor_auth_screen, text="Verify", command=self.verify_auth_code).pack()
        tk.Button(self.two_factor_auth_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.two_factor_auth_screen)
        self.send_auth_code()  # Sending code to user's email

    def send_auth_code(self):
    # Placeholder for sending authentication code to user's email/SMS
        self.auth_code = "123456"  # Example code
        messagebox.showinfo("Authentication", "A verification code has been sent to your email.")

    def verify_auth_code(self):
        code = self.auth_code_entry.get()
        if code == self.auth_code:
            messagebox.showinfo("Verification Successful", "Authentication successful.")
            self.create_main_menu()
        else:
            messagebox.showerror("Verification Failed", "Incorrect authentication code.")
    def data_encryption_screen(self):
        messagebox.showinfo("Data Encryption", "All sensitive data is encrypted.")
    def transaction_history_screen(self):
        self.transaction_history_screen = tk.Frame(self)
        tk.Label(self.transaction_history_screen, text="Transaction History").pack()
    #   Add elements for filters (e.g., date range, type, etc.)
        self.history_listbox = tk.Listbox(self.transaction_history_screen, height=10, width=50)
        self.history_listbox.pack()
        tk.Button(self.transaction_history_screen, text="Load History", command=self.load_transaction_history).pack()
        tk.Button(self.transaction_history_screen, text="Back", command=self.go_back).pack()
        self.change_screen(self.transaction_history_screen)

    def load_transaction_history(self):
        account_number = self.generate_account_number()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT transaction_type, amount, transaction_date FROM transactions WHERE account_number=?", (account_number,))
        transactions = cursor.fetchall()
        self.history_listbox.delete(0, tk.END)  # Clear existing entries
        for transaction in transactions:
            self.history_listbox.insert(tk.END, f"{transaction[2]}: {transaction[0]} of ${transaction[1]}")



    # Define additional methods for financial transactions, account services, and security features.

if __name__ == "__main__":
    app = BankingApp()
    app.mainloop() 
