import tkinter as tk
from tkinter import messagebox
import json
import base64
import pyperclip  # Thư viện sao chép vào clipboard
from cryptography.fernet import Fernet

# Hàm tạo khóa mã hóa
def generate_key():
    return Fernet.generate_key()

# Hàm mã hóa mật khẩu
def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

# Hàm giải mã mật khẩu
def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

# Chuyển đổi dữ liệu kiểu bytes thành base64 để lưu vào JSON
def encode_bytes_to_base64(byte_data):
    return base64.b64encode(byte_data).decode('utf-8')

def decode_base64_to_bytes(base64_data):
    return base64.b64decode(base64_data.encode('utf-8'))


def save_account(account, password, filename='accounts.json'):
    try:
        with open(filename, 'r') as f:
            accounts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        accounts = {}

    # Mã hóa mật khẩu trước khi lưu
    key = generate_key()  # Mỗi tài khoản có thể có một khóa mã hóa riêng
    encrypted_password = encrypt_password(password, key)
    
    # Mã hóa base64 cho mật khẩu và khóa trước khi lưu vào JSON
    accounts[account] = {
        'password': encode_bytes_to_base64(encrypted_password),
        'key': encode_bytes_to_base64(key)  # Lưu trữ khóa mã hóa dưới dạng chuỗi base64
    }
    with open(filename, 'w') as f:
        json.dump(accounts, f, indent=4)
    messagebox.showinfo("Thành công", f"Tài khoản {account} đã được lưu thành công!")

def get_account(account, filename='accounts.json'):
    try:
        with open(filename, 'r') as f:
            accounts = json.load(f)
        
        if account not in accounts:
            messagebox.showerror("Lỗi", "Tài khoản không tồn tại!")
            return
        
        encrypted_password_base64 = accounts[account]['password']
        key_base64 = accounts[account]['key']
        
        # Giải mã base64 thành bytes
        encrypted_password = decode_base64_to_bytes(encrypted_password_base64)
        key = decode_base64_to_bytes(key_base64)
        
        password = decrypt_password(encrypted_password, key)
        messagebox.showinfo("Thông tin tài khoản", f"Tài khoản: {account}\nMật khẩu: {password}")
        
        # Sao chép mật khẩu vào clipboard
        pyperclip.copy(password)
        messagebox.showinfo("Sao chép thành công", "Mật khẩu đã được sao chép vào clipboard!")
    
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Lỗi", "Không có dữ liệu tài khoản nào!")

# Tạo giao diện người dùng
def create_gui():
    window = tk.Tk()
    window.title("Quản lý Tài khoản và Mật khẩu")

    # Tạo nhãn và ô nhập liệu cho tài khoản và mật khẩu
    tk.Label(window, text="Tên tài khoản:").grid(row=0, column=0, padx=10, pady=10)
    account_entry = tk.Entry(window, width=30)
    account_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(window, text="Mật khẩu:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Hàm lưu tài khoản
    def save_account_gui():
        account = account_entry.get()
        password = password_entry.get()
        if not account or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin tài khoản và mật khẩu!")
        else:
            save_account(account, password)

    # Hàm lấy tài khoản
    def get_account_gui():
        account = account_entry.get()
        if not account:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên tài khoản để tìm kiếm!")
        else:
            get_account(account)

    # Tạo nút Lưu tài khoản và nút Lấy tài khoản
    save_button = tk.Button(window, text="Lưu tài khoản", command=save_account_gui)
    save_button.grid(row=2, column=0, padx=10, pady=10)

    get_button = tk.Button(window, text="Lấy mật khẩu", command=get_account_gui)
    get_button.grid(row=2, column=1, padx=10, pady=10)

    window.mainloop()

# Chạy GUI
if __name__ == "__main__":
    create_gui()
