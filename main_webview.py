# ==========================================
# OpenWRT Backup & Restore Tool - Backend
# EN: Core Python backend using PyWebView for the UI. Handles SSH connections, Sysupgrade commands, and SCP file transfers.
# RU: Основной Python-бэкенд с использованием PyWebView для UI. Обрабатывает SSH подключения, команды Sysupgrade и передачу файлов через SCP.
# ==========================================
import os
import sys
import time
import socket
import tarfile
import threading
import subprocess
import webbrowser
import paramiko
from scp import SCPClient
import webview

# In pywebview, to open native dialogs without an extra Tk window, we can use webview.windows[0].create_file_dialog

# --- LOCALES (HARDCODED) ---
LOCALES = {
    "en": {
        "window_title": "OpenWRT Backup & Restore",
        "ip_label": "Router IP:",
        "user_label": "User:",
        "pass_label": "Password:",
        "tab_backup": "Backup Config",
        "tab_restore": "Restore Firmware",
        "dest_label": "Destination Folder:",
        "browse_btn": "Browse...",
        "extract_checkbox": "Extract downloaded archive",
        "backup_btn": "Start Backup",
        "firmware_label": "Firmware Image (.bin/.img):",
        "keep_config_checkbox": "Keep current configuration (-c)",
        "force_flash_checkbox": "Force flash regardless of version mismatch (-F)",
        "restore_btn": "Start Restore",
        "status_idle": "Status: Ready",
        "btn_show_logs": "Show Logs",
        "btn_hide_logs": "Hide Logs",
        "log_window_title": "Action Log",
        "btn_clear_logs": "Clear",
        "settings_title": "Settings",
        "appearance": "Appearance:",
        "theme_system": "System",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "transparency": "Transparency:",
        "github_repo": "GitHub Repository",
        "openwrt_forum": "OpenWrt Forum"
    },
    "ru": {
        "window_title": "OpenWRT Backup & Restore",
        "ip_label": "IP Роутера:",
        "user_label": "Логин:",
        "pass_label": "Пароль:",
        "tab_backup": "Резервное копирование",
        "tab_restore": "Восстановление",
        "dest_label": "Куда сохранить:",
        "browse_btn": "Обзор...",
        "extract_checkbox": "Распаковать скачанный архив",
        "backup_btn": "Начать бэкап",
        "firmware_label": "Файл прошивки (.bin/.img):",
        "keep_config_checkbox": "Сохранить текущие настройки (-c)",
        "force_flash_checkbox": "Принудительная прошивка (-F)",
        "restore_btn": "Начать прошивку",
        "status_idle": "Статус: Ожидание",
        "btn_show_logs": "Показать лог",
        "btn_hide_logs": "Скрыть лог",
        "log_window_title": "Журнал событий",
        "btn_clear_logs": "Очистить",
        "settings_title": "Настройки",
        "appearance": "Оформление:",
        "theme_system": "Системная",
        "theme_light": "Светлая",
        "theme_dark": "Темная",
        "transparency": "Прозрачность фона:",
        "github_repo": "Репозиторий GitHub",
        "openwrt_forum": "Форум OpenWrt"
    }
}

CURRENT_LOCALE = "en"
window = None

class Api:
    def get_translation(self, key):
        return LOCALES[CURRENT_LOCALE].get(key, f"[{key}]")

    def change_language(self, lang_code):
        global CURRENT_LOCALE
        if lang_code in LOCALES:
            CURRENT_LOCALE = lang_code

    def open_url(self, target):
        if target == 'github':
            webbrowser.open("https://github.com/Gegaremant/OpenWrt_firmvare_backupRestore_win")
        else:
            webbrowser.open("https://forum.openwrt.org/")

    def browse_dest_folder(self):
        try:
            result = window.create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                return result[0]
        except Exception as e:
            print("Dialog error:", e)
        return ""

    def browse_firmware_file(self):
        try:
            file_types = ('Firmware files (*.bin;*.img)', 'All files (*.*)')
            result = window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types)
            if result and len(result) > 0:
                return result[0]
        except Exception as e:
            print("Dialog error:", e)
        return ""

    def get_default_ip(self):
        try:
            output = subprocess.check_output("route print 0.0.0.0", shell=True).decode('cp866', errors='ignore')
            for line in output.split('\n'):
                if '0.0.0.0' in line and not line.strip().startswith('='):
                    parts = line.split()
                    if len(parts) >= 3 and parts[0] == '0.0.0.0':
                        if parts[2].lower() not in ['on-link']:
                            return parts[2]
        except:
            pass
        return "192.168.1.1"

    def check_router_status(self, ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect((ip, 22))
            banner = s.recv(1024).decode('utf-8', errors='ignore')
            s.close()
            if 'dropbear' in banner.lower() or 'openwrt' in banner.lower():
                return True
        except:
            pass
        return False

    def resize_window(self, width, height):
        window.resize(width, height)

    def _log(self, msg):
        print(msg)
        safe_msg = msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        window.evaluate_js(f'window.update_log("{safe_msg}")')

    def _set_status(self, tab, msg, is_error=False):
        safe_msg = msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        err_flag = "true" if is_error else "false"
        window.evaluate_js(f'window.set_status("{tab}", "{safe_msg}", {err_flag})')
        self._log(msg)

    def _connect_ssh(self, ip, user, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._log(f"Connecting to {ip} via SSH...")
        ssh.connect(ip, username=user, password=password, timeout=5, look_for_keys=False, allow_agent=False, banner_timeout=10)
        return ssh

    def start_backup(self, ip, user, password, dest, extract):
        def run():
            self._set_status("backup", "Connecting to router...", False)
            ssh = None
            try:
                if not ip or not dest:
                    raise ValueError("IP and Destination must be provided.")
                    
                ssh = self._connect_ssh(ip, user, password)
                self._set_status("backup", "Generating backup archive on router...", False)
                
                cmd = "sysupgrade -b /tmp/backup_fw.tar.gz"
                stdin, stdout, stderr = ssh.exec_command(cmd)
                out = stdout.read().decode().strip()
                err = stderr.read().decode().strip()
                
                if out: self._log(f"sysupgrade output: {out}")
                if err: self._log(f"sysupgrade error: {err}")
                
                self._set_status("backup", "Downloading backup archive...", False)
                local_tar = os.path.join(dest, "backup_fw.tar.gz")
                
                with SCPClient(ssh.get_transport()) as scp:
                    scp.get("/tmp/backup_fw.tar.gz", local_tar)
                    
                self._log(f"Archive downloaded to {local_tar}")
                
                if extract:
                    self._set_status("backup", "Extracting archive...", False)
                    with tarfile.open(local_tar, "r:gz") as tar:
                        tar.extractall(path=dest)
                    self._log(f"Archive extracted to {dest}")
                    
                self._set_status("backup", "Backup completed successfully!", False)
            except Exception as e:
                import traceback
                self._log(traceback.format_exc())
                self._set_status("backup", f"Error: {str(e)}", True)
            finally:
                if ssh:
                    try:
                        ssh.exec_command("rm -f /tmp/backup_fw.tar.gz")
                        ssh.close()
                    except: pass
        threading.Thread(target=run, daemon=True).start()

    def start_restore(self, ip, user, password, fw_path, keep_config, force_flash):
        def run():
            self._set_status("restore", "Connecting to router...", False)
            ssh = None
            try:
                if not ip or not fw_path:
                    raise ValueError("IP and Firmware path must be provided.")
                    
                ssh = self._connect_ssh(ip, user, password)
                self._set_status("restore", "Uploading firmware...", False)
                
                remote_fw = "/tmp/firmware.bin"
                with SCPClient(ssh.get_transport()) as scp:
                    scp.put(fw_path, remote_fw)
                    
                self._log(f"Uploaded {os.path.basename(fw_path)} to {remote_fw}")
                self._set_status("restore", "Flashing firmware...", False)
                
                flags = ""
                if not keep_config: flags += " -n"
                if force_flash: flags += " -F"
                
                cmd = f"sysupgrade {flags} {remote_fw}"
                self._log(f"Executing: {cmd}")
                
                stdin, stdout, stderr = ssh.exec_command(cmd)
                try:
                    out = stdout.read().decode().strip()
                    err = stderr.read().decode().strip()
                    if out: self._log(out)
                    if err: self._log(err)
                except:
                    self._log("Connection dropped (expected during reboot).")
                    
                self._set_status("restore", "Flash initiated! Router is rebooting.", False)
            except Exception as e:
                import traceback
                self._log(traceback.format_exc())
                self._set_status("restore", f"Error: {str(e)}", True)
            finally:
                if ssh:
                    ssh.close()
        threading.Thread(target=run, daemon=True).start()

if __name__ == '__main__':
    api = Api()
    
    def get_resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
        
    html_file = get_resource_path(os.path.join("web", "index.html"))
    
    window = webview.create_window(
        'OpenWRT Backup & Restore', 
        url=f'file://{html_file}', 
        js_api=api,
        width=780, 
        height=520,
        min_size=(780, 520),
        resizable=True, # User requested adaptive stretching
        frameless=False
    )
    
    webview.start()
