import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
import paramiko
import tarfile
import time

# --- Constants & Globals / Константы и глобальные переменные ---
LOCALES_DIR = "locales"
CURRENT_LOCALE = "en"  # Default / По умолчанию
STRINGS = {}

FALLBACK_STRINGS = {
  "window_title": "OpenWRT Backup & Restore Tool",
  "tab_backup": "Backup Configuration",
  "tab_restore": "Restore Firmware",
  "ip_label": "Router IP Address:",
  "user_label": "Username:",
  "pass_label": "Password:",
  "dest_label": "Save Destination (Windows Folder):",
  "firmware_label": "Select Firmware Image (.bin/.img):",
  "browse_btn": "Browse...",
  "extract_checkbox": "Extract downloaded archive automatically (for ImageBuilder files/ overlay)",
  "keep_config_checkbox": "Keep current configuration (-c)",
  "force_flash_checkbox": "Force flash regardless of version mismatch (-F)",
  "backup_btn": "Start Backup",
  "restore_btn": "Start Restore",
  "status_idle": "Status: Ready",
  "status_connecting": "Status: Connecting to router...",
  "status_generating": "Status: Generating backup on router...",
  "status_downloading": "Status: Downloading backup via SFTP...",
  "status_extracting": "Status: Extracting backup files...",
  "status_uploading": "Status: Uploading firmware to router...",
  "status_flashing": "Status: Flashing firmware (Do NOT turn off power!)...",
  "status_success": "Status: Backup successfully saved!",
  "status_restore_success": "Status: Firmware flashed! Router is rebooting.",
  "status_error": "Error: {error}",
  "msg_title_success": "Success",
  "msg_desc_success": "Backup has been successfully downloaded and saved.",
  "msg_desc_restore_success": "Firmware flashing initiated successfully. The router is now rebooting. Please wait a few minutes before reconnecting.",
  "msg_title_error": "Error",
  "msg_error_fields": "Please fill in all credentials (IP, User, Password).",
  "msg_error_dest": "Destination folder does not exist.",
  "msg_error_firmware": "Please select a valid firmware file.",
  "msg_confirm_restore_title": "Confirm Flash",
  "msg_confirm_restore_desc": "Are you sure you want to flash this firmware to the router?\nDO NOT turn off the power during the update."
}

def load_locale(lang_code):
    """
    Load locale strings from JSON file. Fallback to English if not found.
    """
    global STRINGS, CURRENT_LOCALE
    file_path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                STRINGS = json.load(f)
                CURRENT_LOCALE = lang_code
        except Exception as e:
            print(f"Error loading locale {lang_code}: {e}, using fallback.")
            STRINGS = FALLBACK_STRINGS.copy()
            CURRENT_LOCALE = "en"
    else:
        print(f"Locale file {file_path} not found. Using English fallback.")
        STRINGS = FALLBACK_STRINGS.copy()
        CURRENT_LOCALE = "en"

def t(key):
    """
    Translate a string by key.
    Перевод строки по ключу.
    """
    return STRINGS.get(key, f"[{key}]")

class OpenWRTToolApp:
    def __init__(self, root):
        self.root = root
        
        # Load default locale / Загрузка локали по умолчанию
        load_locale("en")
        
        # Build UI / Создание интерфейса
        self.build_ui()
        self.update_ui_strings()
        
    def build_ui(self):
        """
        Create GUI elements.
        Создание элементов графического интерфейса.
        """
        # Language selection / Выбор языка
        lang_frame = ttk.Frame(self.root)
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Hint about locales / Подсказка о локалях
        hint_text = "Missing locales? Add .json files to the 'locales' folder."
        ttk.Label(lang_frame, text=hint_text, foreground="gray").pack(side=tk.LEFT)
        
        self.lang_var = tk.StringVar(value=CURRENT_LOCALE)
        ttk.Radiobutton(lang_frame, text="English", variable=self.lang_var, value="en", command=self.change_language).pack(side=tk.RIGHT)
        ttk.Radiobutton(lang_frame, text="Русский", variable=self.lang_var, value="ru", command=self.change_language).pack(side=tk.RIGHT, padx=5)

        # Common Credentials Frame / Общий блок ввода данных авторизации
        cred_frame = ttk.LabelFrame(self.root, text="Credentials")
        cred_frame.pack(fill=tk.X, padx=10, pady=5)

        # IP Address / IP-адрес
        self.lbl_ip = ttk.Label(cred_frame)
        self.lbl_ip.grid(column=0, row=0, sticky=tk.W, pady=2, padx=5)
        self.entry_ip = ttk.Entry(cred_frame, width=25)
        self.entry_ip.insert(0, "192.168.1.1")
        self.entry_ip.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Username / Имя пользователя
        self.lbl_user = ttk.Label(cred_frame)
        self.lbl_user.grid(column=2, row=0, sticky=tk.W, pady=2, padx=5)
        self.entry_user = ttk.Entry(cred_frame, width=15)
        self.entry_user.insert(0, "root")
        self.entry_user.grid(column=3, row=0, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Password / Пароль
        self.lbl_pass = ttk.Label(cred_frame)
        self.lbl_pass.grid(column=4, row=0, sticky=tk.W, pady=2, padx=5)
        self.entry_pass = ttk.Entry(cred_frame, width=15, show="*")
        self.entry_pass.grid(column=5, row=0, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        cred_frame.columnconfigure(1, weight=1)

        # Notebook for Tabs / Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ================= TAB 1: BACKUP =================
        self.tab_backup = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.notebook.add(self.tab_backup, text="Backup Configuration")

        self.lbl_dest = ttk.Label(self.tab_backup)
        self.lbl_dest.grid(column=0, row=0, sticky=tk.W, pady=2)
        
        dest_frame = ttk.Frame(self.tab_backup)
        dest_frame.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=2)
        
        self.entry_dest = ttk.Entry(dest_frame)
        self.entry_dest.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_browse_dest = ttk.Button(dest_frame, command=self.browse_dest_folder)
        self.btn_browse_dest.pack(side=tk.LEFT, padx=(5, 0))

        self.extract_var = tk.BooleanVar(value=True)
        self.chk_extract = ttk.Checkbutton(self.tab_backup, variable=self.extract_var)
        self.chk_extract.grid(column=0, row=1, columnspan=2, sticky=tk.W, pady=10)

        self.btn_backup = ttk.Button(self.tab_backup, command=self.start_backup_thread)
        self.btn_backup.grid(column=0, row=2, columnspan=2, pady=10)
        
        self.tab_backup.columnconfigure(1, weight=1)

        # ================= TAB 2: RESTORE =================
        self.tab_restore = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.notebook.add(self.tab_restore, text="Restore Firmware")

        self.lbl_firmware = ttk.Label(self.tab_restore)
        self.lbl_firmware.grid(column=0, row=0, sticky=tk.W, pady=2)

        fw_frame = ttk.Frame(self.tab_restore)
        fw_frame.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=2)

        self.entry_firmware = ttk.Entry(fw_frame)
        self.entry_firmware.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_browse_fw = ttk.Button(fw_frame, command=self.browse_firmware_file)
        self.btn_browse_fw.pack(side=tk.LEFT, padx=(5, 0))

        self.keep_config_var = tk.BooleanVar(value=False)
        self.chk_keep_config = ttk.Checkbutton(self.tab_restore, variable=self.keep_config_var)
        self.chk_keep_config.grid(column=0, row=1, columnspan=2, sticky=tk.W, pady=5)

        self.force_flash_var = tk.BooleanVar(value=True)
        self.chk_force_flash = ttk.Checkbutton(self.tab_restore, variable=self.force_flash_var)
        self.chk_force_flash.grid(column=0, row=2, columnspan=2, sticky=tk.W, pady=5)

        self.btn_restore = ttk.Button(self.tab_restore, command=self.start_restore_thread)
        self.btn_restore.grid(column=0, row=3, columnspan=2, pady=10)

        self.tab_restore.columnconfigure(1, weight=1)

        # Status Label (Global) / Метка статуса (общая)
        self.lbl_status = ttk.Label(self.root, text="", foreground="blue")
        self.lbl_status.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=5)

    def update_ui_strings(self):
        """
        Update UI text based on the current locale.
        Обновление текста интерфейса на основе текущей локали.
        """
        self.root.title(t("window_title"))
        self.lbl_ip.config(text=t("ip_label"))
        self.lbl_user.config(text=t("user_label"))
        self.lbl_pass.config(text=t("pass_label"))
        
        self.notebook.tab(self.tab_backup, text=t("tab_backup"))
        self.lbl_dest.config(text=t("dest_label"))
        self.btn_browse_dest.config(text=t("browse_btn"))
        self.chk_extract.config(text=t("extract_checkbox"))
        self.btn_backup.config(text=t("backup_btn"))

        self.notebook.tab(self.tab_restore, text=t("tab_restore"))
        self.lbl_firmware.config(text=t("firmware_label"))
        self.btn_browse_fw.config(text=t("browse_btn"))
        self.chk_keep_config.config(text=t("keep_config_checkbox"))
        self.chk_force_flash.config(text=t("force_flash_checkbox"))
        self.btn_restore.config(text=t("restore_btn"))

        self.lbl_status.config(text=t("status_idle"))

    def change_language(self):
        """
        Handle language radio button toggle.
        Обработка переключения языка.
        """
        load_locale(self.lang_var.get())
        self.update_ui_strings()

    def browse_dest_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_dest.delete(0, tk.END)
            self.entry_dest.insert(0, folder)

    def browse_firmware_file(self):
        filetypes = (
            ('Firmware files', '*.bin *.img'),
            ('All files', '*.*')
        )
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.entry_firmware.delete(0, tk.END)
            self.entry_firmware.insert(0, filepath)

    def set_status(self, text, is_error=False):
        """
        Update status label safely from any thread.
        Безопасное обновление метки статуса из любого потока.
        """
        def update():
            self.lbl_status.config(text=text, foreground="red" if is_error else "blue")
        self.root.after(0, update)

    def show_message(self, title, message, is_error=False, is_ask=False):
        """
        Show a message box safely. Can be run in main thread.
        """
        if is_error:
            messagebox.showerror(title, message)
        else:
            if is_ask:
                return messagebox.askyesno(title, message)
            else:
                messagebox.showinfo(title, message)

    def get_credentials(self):
        ip = self.entry_ip.get().strip()
        user = self.entry_user.get().strip()
        password = self.entry_pass.get()
        return ip, user, password

    # ================= BACKUP LOGIC =================

    def start_backup_thread(self):
        ip, user, password = self.get_credentials()
        dest = self.entry_dest.get().strip()
        do_extract = self.extract_var.get()

        if not all([ip, user, password, dest]):
            self.show_message(t("msg_title_error"), t("msg_error_fields"), is_error=True)
            return

        if not os.path.isdir(dest):
            self.show_message(t("msg_title_error"), t("msg_error_dest"), is_error=True)
            return

        self.btn_backup.state(['disabled'])
        self.btn_restore.state(['disabled'])
        threading.Thread(target=self.backup_worker, args=(ip, user, password, dest, do_extract), daemon=True).start()

    def backup_worker(self, ip, user, password, dest, do_extract):
        ssh = None
        sftp = None
        remote_file = f"/tmp/backup_{int(time.time())}.tar.gz"
        local_archive = os.path.join(dest, "openwrt_backup.tar.gz")

        try:
            self.set_status(t("status_connecting"))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, username=user, password=password, timeout=10)

            self.set_status(t("status_generating"))
            stdin, stdout, stderr = ssh.exec_command(f"sysupgrade -b {remote_file}")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                err_msg = stderr.read().decode('utf-8').strip()
                raise Exception(f"Command failed: {err_msg}")

            self.set_status(t("status_downloading"))
            sftp = ssh.open_sftp()
            sftp.get(remote_file, local_archive)
            sftp.remove(remote_file)

            if do_extract:
                self.set_status(t("status_extracting"))
                extract_dir = os.path.join(dest, "openwrt_config_extracted")
                os.makedirs(extract_dir, exist_ok=True)
                with tarfile.open(local_archive, "r:gz") as tar:
                    tar.extractall(path=extract_dir)

            self.set_status(t("status_success"))
            self.root.after(0, lambda: self.show_message(t("msg_title_success"), t("msg_desc_success")))

        except Exception as e:
            error_str = str(e)
            self.set_status(t("status_error").replace("{error}", error_str), is_error=True)
            self.root.after(0, lambda: self.show_message(t("msg_title_error"), error_str, is_error=True))

        finally:
            if sftp: sftp.close()
            if ssh: ssh.close()
            self.root.after(0, lambda: self.btn_backup.state(['!disabled']))
            self.root.after(0, lambda: self.btn_restore.state(['!disabled']))

    # ================= RESTORE LOGIC =================

    def start_restore_thread(self):
        ip, user, password = self.get_credentials()
        firmware_path = self.entry_firmware.get().strip()
        keep_config = self.keep_config_var.get()
        force_flash = self.force_flash_var.get()

        if not all([ip, user, password]):
            self.show_message(t("msg_title_error"), t("msg_error_fields"), is_error=True)
            return

        if not os.path.isfile(firmware_path):
            self.show_message(t("msg_title_error"), t("msg_error_firmware"), is_error=True)
            return

        # Confirm flash / Подтверждение прошивки
        confirm = self.show_message(t("msg_confirm_restore_title"), t("msg_confirm_restore_desc"), is_ask=True)
        if not confirm:
            return

        self.btn_backup.state(['disabled'])
        self.btn_restore.state(['disabled'])
        threading.Thread(target=self.restore_worker, args=(ip, user, password, firmware_path, keep_config, force_flash), daemon=True).start()

    def restore_worker(self, ip, user, password, firmware_path, keep_config, force_flash):
        ssh = None
        sftp = None
        remote_fw_path = "/tmp/firmware_upload.bin"

        try:
            self.set_status(t("status_connecting"))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, username=user, password=password, timeout=10)

            self.set_status(t("status_uploading"))
            sftp = ssh.open_sftp()
            sftp.put(firmware_path, remote_fw_path)
            sftp.close()
            sftp = None

            self.set_status(t("status_flashing"))
            
            # Construct sysupgrade command
            # Сборка команды sysupgrade
            cmd = "sysupgrade "
            if not keep_config:
                cmd += "-n "
            if force_flash:
                cmd += "-F "
            cmd += remote_fw_path

            stdin, stdout, stderr = ssh.exec_command(cmd)
            # We don't wait for recv_exit_status() on sysupgrade because it will disconnect the SSH session when it reboots.
            # Мы не ждем recv_exit_status, потому что sysupgrade разорвет SSH соединение при перезагрузке.
            
            # Read slightly to ensure it started, but expect a socket drop
            # Читаем немного, чтобы убедиться, что началось, ожидаем разрыв сокета
            try:
                stdout.channel.recv(1024)
            except Exception:
                pass

            self.set_status(t("status_restore_success"))
            self.root.after(0, lambda: self.show_message(t("msg_title_success"), t("msg_desc_restore_success")))

        except Exception as e:
            # If the error is an SSH disconnect, it means sysupgrade succeeded and rebooted the router.
            if isinstance(e, EOFError) or "Socket is closed" in str(e) or "Connection reset" in str(e):
                self.set_status(t("status_restore_success"))
                self.root.after(0, lambda: self.show_message(t("msg_title_success"), t("msg_desc_restore_success")))
            else:
                error_str = str(e)
                self.set_status(t("status_error").replace("{error}", error_str), is_error=True)
                self.root.after(0, lambda: self.show_message(t("msg_title_error"), error_str, is_error=True))

        finally:
            if sftp: sftp.close()
            if ssh: ssh.close()
            self.root.after(0, lambda: self.btn_backup.state(['!disabled']))
            self.root.after(0, lambda: self.btn_restore.state(['!disabled']))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("650x380")
    root.resizable(False, False)
    
    os.makedirs(LOCALES_DIR, exist_ok=True)
    
    app = OpenWRTToolApp(root)
    root.mainloop()
