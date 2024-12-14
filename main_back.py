import customtkinter as ctk
import json
import base64
import requests
import pyperclip
from cryptography.fernet import Fernet
from tkinter import messagebox
from icecream import ic

# ic.disable()        ## debug

############################################## CLASS CHECK UPDATE
THIS_VERSION = "1.2.1"

def checkcode():
    current_version = THIS_VERSION 
    url = 'https://raw.githubusercontent.com/srymcfear/verify_me/refs/heads/main/version/version.json'     
    response = requests.get(url)                    # CHECK FILE JSON 
    if response.status_code == 200:
        file_data = response.json()                 # Tải nội dung file JSON
        if "autokboard-ver" and "autokboard-key" in file_data:
            latest_version = file_data['autokboard-ver']
            key_real = file_data['autokboard-key']
            if key_real == 'active':
                ic(key_real)
                if latest_version > current_version:
                    ic('Vui lòng cập nhật phiên bản mới!',current_version)
                    show_popup('Vui lòng cập nhật phiên bản mới! \nPhiên bản mới:' + latest_version)
                else:
                    ic('Chưa có bản update',{latest_version})
                    # show_popup('FEAR - Auto_Keyboard: Key hợp lệ')
                    main()  #run 
                    return
            else:
                ic('Key không đúng',key_real)
                show_popup('App đang tạm khoá. \nLiên hệ discord: discord.gg/ZbwFeuea6U')

        else:
            ic("Lỗi phiên bản. Liên hệ discord để có bản mới . discord.gg/ZbwFeuea6U")
            show_popup("Lỗi phiên bản. Liên hệ discord để có bản mới . discord.gg/ZbwFeuea6U")
    else:
        show_popup("Lỗi khi checkkey. Mã lỗi:", {response.status_code})
        ic("Lỗi khi checkkey. Mã lỗi:", {response.status_code})
### thongbao
def show_popup(text_danhap):
    entered_text = text_danhap  # Lấy văn bản từ trường nhập liệu
    messagebox.showinfo("FEAR - SEVMEK", f"FEAR - Sevmek: {entered_text}")  # Hiển thị popup với thông tin

############################################## CLASS CHECK UPDATE - END ###################################################


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

# Chuyển đổi dữ liệu base64 trở lại thành bytes
def decode_base64_to_bytes(base64_data):
    return base64.b64decode(base64_data.encode('utf-8'))

# Lưu thông tin tài khoản và mật khẩu vào file JSON
def save_account(account, password, account_type, filename='accounts.json'):
    try:
        with open(filename, 'r') as f:
            accounts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        accounts = {}

    # Mã hóa mật khẩu trước khi lưu
    key = generate_key()  # Mỗi tài khoản có thể có một khóa mã hóa riêng
    encrypted_password = encrypt_password(password, key)
    
    # Mã hóa base64 cho mật khẩu và khóa trước khi lưu vào JSON
    account_data = {
        'password': encode_bytes_to_base64(encrypted_password),
        'key': encode_bytes_to_base64(key),  # Lưu trữ khóa mã hóa dưới dạng chuỗi base64
        'account_type': account_type  # Lưu loại tài khoản
    }

    # Nếu tài khoản đã có trong dữ liệu, thêm loại tài khoản mới vào danh sách
    if account in accounts:
        accounts[account].append(account_data)
    else:
        accounts[account] = [account_data]
    
    # Lưu lại vào file
    with open(filename, 'w') as f:
        json.dump(accounts, f, indent=4)
    messagebox.showinfo("Thành công", f"Tài khoản {account} đã được lưu thành công!")

# Lấy thông tin tài khoản và mật khẩu từ file JSON
def get_account(account, account_type, filename='accounts.json'):
    try:
        with open(filename, 'r') as f:
            accounts = json.load(f)
        
        if account not in accounts:
            messagebox.showerror("Lỗi", "Tài khoản không tồn tại!")
            return None
        
        account_info = accounts[account]
        
        # Tìm thông tin tài khoản với loại tài khoản tương ứng
        for item in account_info:
            if item['account_type'] == account_type:
                encrypted_password_base64 = item['password']
                key_base64 = item['key']
                
                # Giải mã base64 thành bytes
                encrypted_password = decode_base64_to_bytes(encrypted_password_base64)
                key = decode_base64_to_bytes(key_base64)
                
                # Giải mã mật khẩu
                password = decrypt_password(encrypted_password, key)
                
                # Trả lại mật khẩu nguyên bản
                return password
        
        messagebox.showinfo("Lỗi", f"Không tìm thấy loại tài khoản '{account_type}' cho tài khoản '{account}'!")
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Lỗi", "Không có dữ liệu tài khoản nào!")

# Lưu các loại tài khoản vào file JSON
def save_account_types(account_types, filename='account_types.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(account_types, f, indent=4)
        messagebox.showinfo("Thành công", "Các loại tài khoản đã được lưu thành công!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi lưu loại tài khoản: {e}")

# Lấy các loại tài khoản từ file JSON
def load_account_types(filename='account_types.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Hàm kiểm tra xem ký tự có phải là dấu câu trong tiếng Việt hay không
def is_valid_char(char):
    # Danh sách các dấu câu trong tiếng Việt
    viet_diacritics = "áàảãạâấầẩẫậéêèẻẽẹíìỉĩịóòỏõọốồổỗộúùủũụ"
    viet_diacritics += "ưừửữựôồổỗộơờởỡợđ"
    return char not in viet_diacritics

# Hàm validate cho CTkEntry
def validate_input(char, value):
    # Kiểm tra nếu ký tự mới không phải dấu câu thì cho phép nhập
    if is_valid_char(char):
        return True
    return False


# Tạo giao diện người dùng
def create_gui():
    ctk.set_appearance_mode("Dark")  # Cài đặt chế độ giao diện
    ctk.set_default_color_theme("blue")  # Cài đặt màu chủ đề

    window = ctk.CTk()
    window.title("Quản lý Tài khoản và Mật khẩu")
    window.geometry("350x410")
    window.resizable(False, False)
    
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

    # Tạo nhãn và ô nhập liệu cho loại tài khoản (chọn từ danh sách)
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
        # messagebox.showinfo("FEAR - SEVMEK", f"FEAR - AutoKeyboard: {text_danhap}")  # Hiển thị popup với thông tin

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
    def get_account_gui():
        account = account_entry.get()
        account_type = account_type_var.get()
        if not account or not account_type:
            show_thongbao("Hãy nhập tên tài khoản & chọn loại tài khoản!")
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên tài khoản và chọn loại tài khoản!")
        else:
            password = get_account(account, account_type)
            if password:
                messagebox.showinfo("Mật khẩu", f"Mật khẩu của tài khoản '{account}' với loại '{account_type}' là: {password}")
                # Sao chép mật khẩu nguyên bản vào clipboard
                pyperclip.copy(password)
                show_thongbao("Mật khẩu đã được sao chép vào clipboard!")
                # messagebox.showinfo("Sao chép thành công", "Mật khẩu đã được sao chép vào clipboard!")

    # Hàm hiển thị danh sách loại tài khoản có cùng tên tài khoản
    def show_account_types_gui():
        account = account_entry.get()
        if not account:
            show_thongbao("Vui lòng nhập tên tài khoản!")
            # messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên tài khoản!")
            return

        try:
            with open('accounts.json', 'r') as f:
                accounts = json.load(f)

            if account not in accounts:
                show_thongbao(f"Tài khoản '{account}' không tồn tại!")
                messagebox.showerror("Lỗi", f"Tài khoản '{account}' không tồn tại!")
                return

            account_info = accounts[account]
            account_types_list = [item['account_type'] for item in account_info]
            if account_types_list:
                messagebox.showinfo("Danh sách loại tài khoản", f"Loại tài khoản của '{account}':\n" + "\n".join(account_types_list))
            else:
                messagebox.showinfo("Không có loại tài khoản", f"Không có loại tài khoản nào cho tài khoản '{account}'!")
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Lỗi", "Không có dữ liệu tài khoản nào!")

    # Tạo cửa sổ Cài đặt loại tài khoản
    def open_settings_window():
        settings_window = ctk.CTkToplevel(window)
        settings_window.title("Cài đặt Loại Tài Khoản")

        new_account_type_label = ctk.CTkLabel(settings_window, text="Nhập loại tài khoản mới:")
        new_account_type_label.grid(row=0, column=0, padx=10, pady=10)
        new_account_type_entry = ctk.CTkEntry(settings_window, width=180)
        new_account_type_entry.grid(row=0, column=1, padx=10, pady=10)

        def add_account_type():
            new_type = new_account_type_entry.get()
            if new_type:
                account_types = load_account_types()
                if new_type not in account_types:
                    account_types.append(new_type)
                    save_account_types(account_types)
                    # Cập nhật lại menu trỏ xuống với loại tài khoản mới
                    account_type_var.set(new_type)
                    account_type_menu.configure(values=account_types)
                    messagebox.showinfo("Thành công", f"Loại tài khoản '{new_type}' đã được thêm!")
                else:
                    messagebox.showwarning("Cảnh báo", "Loại tài khoản này đã tồn tại!")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập loại tài khoản!")

        # Thêm nút để lưu loại tài khoản mới
        add_button = ctk.CTkButton(settings_window, text="Thêm loại tài khoản", command=add_account_type)
        add_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # Tạo các nút
    save_button = ctk.CTkButton(window, text="Lưu tài khoản", command=save_account_gui, hover_color="green")
    save_button.grid(row=6, column=0, padx=10, pady=10)

    get_button = ctk.CTkButton(window, text="Lấy mật khẩu", command=get_account_gui, hover_color="green")
    get_button.grid(row=6, column=1, padx=20, pady=10)

    show_types_button = ctk.CTkButton(window, text="Hiển thị loại tài khoản", command=show_account_types_gui)
    show_types_button.grid(row=7, column=0, columnspan=1, padx=10, pady=10)

    settings_button = ctk.CTkButton(window, text="Cài đặt loại tài khoản", command=open_settings_window, hover_color="pink")
    settings_button.grid(row=7, column=1, columnspan=2, padx=20, pady=10)

    window.mainloop()


def main():
    # Gọi hàm tạo GUI
    create_gui()
    
if __name__ == "__main__":
    checkcode()
