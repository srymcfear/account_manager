import json
import pyperclip
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import ctypes
import base64
import requests
from cryptography.fernet import Fernet
from zipfile import ZipFile
from io import BytesIO
from icecream import ic

ic.disable()        ## debug

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_and_extract_zip(url, destination_folder):
    response = requests.get(url)
    zip_file = ZipFile(BytesIO(response.content))

    zip_file.extractall(destination_folder)
    zip_file.close()


def create_folder_update():
    try:
        appdata_local_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR')
        github_url = 'https://github.com/srymcfear/verify_me/releases/download/config/config.zip'

        create_folder_if_not_exists(appdata_local_path)

        if not os.listdir(appdata_local_path):
            ic("Downloading Updated Files...")
            download_and_extract_zip(github_url, appdata_local_path)
            ic("Done! Thank You For Using",)
            sys.exit()
        else:
            pass
    except Exception as e:
        ic(str(e))
        print("Error Downloading Updated Files, Make Sure To Open As Admin & Try Again!")
        sys.exit()

def create_version_file():
    version_info = {
        "version": "1.0.0",
        "build": "20241215"
    }

    version_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR', 'version.json')
    
    if not os.path.exists(version_file_path):
        with open(version_file_path, 'w') as version_file:
            json.dump(version_info, version_file, indent=4)


############################################## CLASS CHECK UPDATE
THIS_VERSION = "1.2.1"
def checkcode():
    current_version = THIS_VERSION 
    url = 'https://raw.githubusercontent.com/srymcfear/verify_me/refs/heads/main/version/version.json'     
    response = requests.get(url)                    # CHECK FILE JSON 
    if response.status_code == 200:
        file_data = response.json()                 # Tải nội dung file JSON
        if "account_manager-ver" and "account_manager-key" in file_data:
            latest_version = file_data['account_manager-ver']
            key_real = file_data['account_manager-key']
            if key_real == 'active':
                ic(key_real)
                if latest_version > current_version:
                    ic('Vui lòng cập nhật phiên bản mới!',current_version)
                    messagebox.showwarning("Cảnh báo",'Vui lòng cập nhật phiên bản mới! \nPhiên bản mới:' + latest_version)
                else:
                    ic('Chưa có bản update',{latest_version})
                    # messagebox.showwarning("Cảnh báo",'FEAR - Auto_Keyboard: Key hợp lệ')
                    main()  #run 
                    return
            else:
                ic('Key không đúng',key_real)
                messagebox.showwarning("Cảnh báo",'App đang tạm khoá. \nLiên hệ discord: discord.gg/ZbwFeuea6U')

        else:
            ic("Lỗi phiên bản. Liên hệ discord để có bản mới . discord.gg/ZbwFeuea6U")
            messagebox.showwarning("Cảnh báo","Lỗi phiên bản. Liên hệ discord để có bản mới . discord.gg/ZbwFeuea6U")
    else:
        messagebox.showwarning("Cảnh báo",f"Lỗi khi checkkey. Mã lỗi: {response.status_code}")
        ic("Lỗi khi checkkey. Mã lỗi:", {response.status_code})


############################################## CLASS CHECK UPDATE - END ###################################################


# Đường dẫn đến thư mục chứa file JSON
appdata_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR')
KEY_FILE = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR', 'secret.key')
if not os.path.exists(appdata_folder):
    os.makedirs(appdata_folder)

accounts_file = os.path.join(appdata_folder, "accounts.json")
account_types_file = os.path.join(appdata_folder, "account_types.json")

########## ma hoa key ##########
# Tạo khóa mã hóa Fernet (nếu chưa có)
def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    return key

# Tạo một đối tượng Fernet với khóa đã tải
key = load_or_generate_key()
cipher = Fernet(key)

# Hàm mã hóa mật khẩu
def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

# Hàm giải mã mật khẩu
def decrypt_password(encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()
########## ma hoa key - end ##########

# Hàm lưu tài khoản

def save_account(account, password, account_type):
    try:
        # Đọc dữ liệu từ file accounts.json
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)
        else:
            accounts = {}

        if account not in accounts:
            accounts[account] = []

        # Mã hóa mật khẩu trước khi lưu
        encrypted_password = encrypt_password(password)

        accounts[account].append({
            'password': encrypted_password,
            'account_type': account_type
        })

        # Lưu lại dữ liệu vào file accounts.json
        with open(accounts_file, 'w') as f:
            json.dump(accounts, f, indent=4)

        messagebox.showinfo("Thông báo", "Tài khoản đã được lưu thành công!")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi lưu tài khoản: {str(e)}")

def get_account(account, account_type):
    try:
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)

            if account in accounts:
                for item in accounts[account]:
                    if item['account_type'] == account_type:
                        # Giải mã mật khẩu
                        return decrypt_password(item['password'])
        return None
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Hàm hiển thị danh sách tài khoản cùng loại tài khoản đã lưu
def show_accounts_by_type_gui(account_type_var):
    account_type = account_type_var.get()  # Lấy loại tài khoản từ menu
    if not account_type:
        show_thongbao("Vui lòng chọn loại tài khoản!")
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn loại tài khoản!")
        return

    try:
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)

            # Lọc ra tất cả các tài khoản có loại tương ứng
            accounts_with_type = []
            for account, account_info in accounts.items():
                for item in account_info:
                    if item['account_type'] == account_type:
                        accounts_with_type.append(account)

            if accounts_with_type:
                messagebox.showinfo("Danh sách tài khoản", f"Các tài khoản có loại '{account_type}':\n" + "\n".join(set(accounts_with_type)))
            else:
                messagebox.showinfo("Không có tài khoản", f"Không có tài khoản nào với loại '{account_type}'!")

        else:
            messagebox.showerror("Lỗi", "Không có dữ liệu tài khoản nào!")
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Lỗi", "Không có dữ liệu tài khoản nào!")

# Cập nhật giao diện người dùng
def create_gui():
    ctk.set_appearance_mode("Dark")  # Cài đặt chế độ giao diện
    ctk.set_default_color_theme("blue")  # Cài đặt màu chủ đề

    window = ctk.CTk()
    window.title("Quản lý Tài khoản và Mật khẩu")
    window.geometry("350x460")
    window.resizable(False, False)
    
    config_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR')
    icon_path = os.path.join(config_folder, "fear_logo.ico")
    if os.path.exists(icon_path):
        window.iconbitmap(icon_path)
    else:
        ic(f"Không tìm thấy biểu tượng tại {icon_path}")


    # Tiêu đề ở đầu cửa sổ
    label_top = ctk.CTkLabel(window, text="FEAR", font=("Game Of Squids", 50))
    label_top.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

    title_label = ctk.CTkLabel(window, text="Quản lý Tài khoản và Mật khẩu", font=("Arial", 20))
    title_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
    
    notify_label = ctk.CTkLabel(window, text="", font=("Arial", 10), text_color="red")
    notify_label.grid(row=2, column=0,columnspan=2, padx=20, pady=2)

    # Gắn sự kiện validate cho entry
    vcmd = (window.register(validate_input), '%S', '%P')  # %S là ký tự mới, %P là toàn bộ giá trị của entry

    # Tạo nhãn và ô nhập liệu cho tài khoản và mật khẩu
    account_label = ctk.CTkLabel(window, text="Tài khoản:")
    account_label.grid(row=3, column=0, padx=10, pady=10)
    account_entry = ctk.CTkEntry(window, width=160)
    account_entry.grid(row=3, column=1, padx=10, pady=10)
    account_entry.configure(validate="key", validatecommand=vcmd)

    password_label = ctk.CTkLabel(window, text="Mật khẩu:")
    password_label.grid(row=4, column=0, padx=10, pady=10)
    password_entry = ctk.CTkEntry(window, width=160, show="*")
    password_entry.grid(row=4, column=1, padx=10, pady=10)
    password_entry.configure(validate="key", validatecommand=vcmd)

    # nhãn và ô nhập liệu cho loại tài khoản (chọn từ danh sách)
    account_type_label = ctk.CTkLabel(window, text="Loại tài khoản:")
    account_type_label.grid(row=5, column=0, padx=10, pady=10)
    
    account_types = load_account_types()  # Tải danh sách loại tài khoản từ file
    
    # Cung cấp giá trị mặc định nếu danh sách loại tài khoản trống
    if not account_types:
        account_types = ["Chưa có loại tài khoản"]

    account_type_var = ctk.StringVar(value=account_types[0])  # Đặt giá trị mặc định

    # Tạo menu trỏ xuống để chọn loại tài khoản
    account_type_menu = ctk.CTkOptionMenu(window, variable=account_type_var, values=account_types)
    account_type_menu.grid(row=5, column=1, padx=10, pady=10)

    ### thongbao
    def show_thongbao(text_danhap):
        notify_label.configure(text=f"{text_danhap}")

    # Hàm lưu tài khoản
    def save_account_gui():
        account = account_entry.get()
        password = password_entry.get()
        account_type = account_type_var.get()  # Lấy loại tài khoản từ menu
        if not account or not password or not account_type:
            show_thongbao("Nhập đầy đủ tài khoản, mật khẩu và loại tài khoản!")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin tài khoản, mật khẩu và loại tài khoản!")
        else:
            save_account(account, password, account_type)

    # Hàm lấy mật khẩu dựa trên tài khoản và loại tài khoản
# Hàm lấy mật khẩu dựa trên tài khoản và loại tài khoản
    def get_account_gui():
        account = account_entry.get()
        account_type = account_type_var.get()  # Lấy loại tài khoản từ menu
        if not account or not account_type:
            show_thongbao("Hãy nhập tên tài khoản & chọn loại tài khoản!")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên tài khoản và chọn loại tài khoản!")
            return

        password = get_account(account, account_type)
        
        if password:
            messagebox.showinfo("Mật khẩu", f"Mật khẩu của tài khoản '{account}' với loại '{account_type}' là: {password}")
            # Sao chép mật khẩu nguyên bản vào clipboard
            pyperclip.copy(password)
            show_thongbao("Mật khẩu đã được sao chép vào clipboard!")
        else:
            # Nếu không tìm thấy mật khẩu, hiển thị cảnh báo
            messagebox.showwarning("Cảnh báo", f"Không tìm thấy mật khẩu cho tài khoản '{account}' với loại '{account_type}'!")
            show_thongbao(f"Không tìm thấy mật khẩu cho tài khoản '{account}' với loại '{account_type}'!")

    # Thêm nút để hiển thị tài khoản cùng loại
    show_accounts_button = ctk.CTkButton(window, text="Danh sách tài khoản của Loại tài khoản này", command=lambda: show_accounts_by_type_gui(account_type_var))
    show_accounts_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    # Tạo các nút
    save_button = ctk.CTkButton(window, text="Lưu tài khoản", command=save_account_gui, hover_color="green")
    save_button.grid(row=6, column=0, padx=10, pady=10)

    get_button = ctk.CTkButton(window, text="Lấy mật khẩu", command=get_account_gui, hover_color="green")
    get_button.grid(row=6, column=1, padx=20, pady=10)

    settings_button = ctk.CTkButton(window, text="Cài đặt loại tài khoản", command=lambda: open_settings_window(account_type_var, account_type_menu), hover_color="pink")
    settings_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    window.mainloop()

# Hàm tải danh sách loại tài khoản (giả sử đã lưu trong một file JSON)
def load_account_types():
    try:
        if os.path.exists(account_types_file):
            with open(account_types_file, "r") as f:
                account_types = json.load(f)
                return account_types
        else:
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Hàm xử lý để validate input cho các entry (nếu cần thiết)
def validate_input(char, value):
    return True

# Hàm mở cửa sổ cài đặt loại tài khoản
def open_settings_window(account_type_var, account_type_menu):
    settings_window = ctk.CTkToplevel()
    settings_window.title("Thêm loại tài khoản")
    settings_window.geometry("400x110")
    settings_window.resizable(False, False)

    config_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'FEAR')
    icon_path = os.path.join(config_folder, "fear_logo.ico")
    if os.path.exists(icon_path):
        settings_window.iconbitmap(icon_path)
    else:
        ic(f"Không tìm thấy biểu tượng tại {icon_path}")
    
    # Nhãn và ô nhập liệu cho loại tài khoản mới
    new_account_type_label = ctk.CTkLabel(settings_window, text="Nhập loại tài khoản mới:")
    new_account_type_label.grid(row=0, column=0, padx=10, pady=10)
    
    new_account_type_entry = ctk.CTkEntry(settings_window, width=200)
    new_account_type_entry.grid(row=0, column=1, padx=10, pady=10)
    
    # Hàm thêm loại tài khoản mới
    def add_new_account_type():
        new_account_type = new_account_type_entry.get().strip()
        if new_account_type:
            account_types = load_account_types()
            if new_account_type not in account_types:
                account_types.append(new_account_type)
                with open(account_types_file, 'w') as f:
                    json.dump(account_types, f, indent=4)
                
                # Cập nhật lại menu loại tài khoản
                account_type_menu.configure(values=account_types)
                account_type_var.set(new_account_type)  # Đặt giá trị mặc định mới
                messagebox.showinfo("Thông báo", "Loại tài khoản mới đã được thêm thành công!")
                # settings_window.destroy()  # Đóng cửa sổ cài đặt
            else:
                messagebox.showwarning("Cảnh báo", "Loại tài khoản này đã tồn tại!")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên loại tài khoản!")
    
    add_button = ctk.CTkButton(settings_window, text="Thêm loại tài khoản", command=add_new_account_type)
    add_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)



def main():
    if not is_admin():
        ic('not admin')
        messagebox.showwarning("Cảnh báo",'Vui lòng chạy bằng quyền Admin')
        return True
    try:
        create_folder_update()
        create_gui()
    except Exception as e:
        ic(str(e))
    
if __name__ == "__main__":
    # main()
    create_version_file()
    checkcode()