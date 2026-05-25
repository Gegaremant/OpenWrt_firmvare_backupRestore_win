# OpenWRT Backup & Restore Tool (Windows GUI)

A native Windows graphical application to backup your OpenWRT router's configuration and flash new firmware over SSH. It works entirely on Windows without needing Windows Subsystem for Linux (WSL).

This tool is especially useful if you are working with **OpenWRT ImageBuilder**:
- **Backup**: It can download the current router configuration (`sysupgrade -b`) and automatically extract the files so you can simply place them into the `files/` overlay directory.
- **Restore**: It can upload and flash a new firmware image (`.bin`/`.img`) directly from Windows, with a built-in force-flash (`-F`) option to bypass version mismatch errors.

## Features
- **Native GUI**: Tabbed Tkinter-based interface (Backup / Restore tabs).
- **Multilingual**: Supports English and Russian via external `.json` configuration files.
- **No WSL Required**: Written in Python, relies on Paramiko for direct SSH/SFTP access.
- **ImageBuilder Ready**: Extract backups directly for ImageBuilder's `files/` structure.
- **Force Flash**: Flashes new firmware "regardless of installed version" using `sysupgrade -F`.

## Requirements
- Python 3.8+
- The dependencies in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## How to Use
1. Open a command prompt or PowerShell and navigate to this folder.
2. Run the application:
   ```bash
   python app.py
   ```
3. Enter your router credentials (IP, username, password) in the top section.
4. **To Backup:** Go to the "Backup Configuration" tab, select a destination folder, optionally check the "Extract archive" box, and click "Start Backup".
5. **To Restore/Flash:** Go to the "Restore Firmware" tab, select your firmware `.bin` or `.img` file. Check "Force flash" to bypass version checks, and click "Start Restore". The tool will upload the image and reboot the router.

## Building a Standalone Executable (.exe)
You can compile this Python script into a native Windows executable so you can run it on machines without Python installed.
Use `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile app.py
```
*Note: Make sure to copy the `locales` folder next to the generated `app.exe` so the languages work!*

---

# Инструмент Backup & Restore для OpenWRT (Windows GUI)

Нативное графическое приложение для Windows, предназначенное для резервного копирования конфигурации и прошивки роутера OpenWRT по SSH. Инструмент работает в Windows без необходимости использовать Windows Subsystem for Linux (WSL).

Это приложение особенно полезно при работе с **OpenWRT ImageBuilder**:
- **Бэкап**: Приложение скачивает текущую конфигурацию роутера (`sysupgrade -b`) и автоматически распаковывает архив, чтобы вы могли сразу поместить полученные файлы в папку `files/` (overlay).
- **Прошивка**: Приложение умеет загружать и прошивать новые файлы образов (`.bin`/`.img`) с возможностью принудительной прошивки (`-F`), чтобы избежать ошибок несовпадения версий.

## Особенности
- **Нативный GUI**: Интерфейс с вкладками (Backup / Restore) на базе Tkinter.
- **Мультиязычность**: Поддержка английского и русского языков через внешние конфигурационные файлы `.json`.
- **Без WSL**: Написано на Python, использует Paramiko для прямого доступа по SSH/SFTP.
- **Готовность для ImageBuilder**: Распаковка файлов прямо под структуру ImageBuilder.
- **Принудительная прошивка**: Прошивает образ «независимо от установленной версии» с помощью ключа `sysupgrade -F`.

## Требования
- Python 3.8+
- Зависимости, указанные в `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## Как использовать
1. Откройте командную строку (cmd) или PowerShell и перейдите в эту папку.
2. Запустите приложение:
   ```bash
   python app.py
   ```
3. Введите данные для входа на роутер (IP, пользователь, пароль) в верхней части окна.
4. **Для бэкапа:** Перейдите на вкладку «Резервное копирование», выберите папку, отметьте распаковку (по желанию) и нажмите «Начать копирование».
5. **Для прошивки:** Перейдите на вкладку «Восстановление прошивки», выберите файл `.bin` или `.img`. Отметьте «Принудительная прошивка» для обхода проверки версий и нажмите «Начать прошивку». Утилита загрузит образ и отправит роутер в перезагрузку.

## Сборка в автономный исполняемый файл (.exe)
Вы можете скомпилировать этот Python-скрипт в нативный исполняемый файл Windows, чтобы запускать его на компьютерах без установленного Python.
Для этого используйте `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile app.py
```
*Примечание: Не забудьте скопировать папку `locales` рядом с созданным `app.exe`, иначе локализация не будет работать!*
