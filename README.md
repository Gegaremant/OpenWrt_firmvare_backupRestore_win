# OpenWRT Backup & Restore Tool (Windows GUI)

A native Windows graphical application to backup your OpenWRT router's configuration and flash new firmware over SSH. It works entirely on Windows without needing Windows Subsystem for Linux (WSL).

This tool is especially useful if you are working with **OpenWRT ImageBuilder**:
- **Backup**: It can download the current router configuration (`sysupgrade -b`) and automatically extract the files so you can simply place them into the `files/` overlay directory.
- **Restore**: It can upload and flash a new firmware image (`.bin`/`.img`) directly from Windows, with a built-in force-flash (`-F`) option to bypass version mismatch errors.

## Features
- **Native GUI**: Tabbed Tkinter-based interface (Backup / Restore tabs).
- **Multilingual**: Supports English and Russian via external `.json` configuration files.
- **Detailed Logging**: An expandable inline action log panel to track SSH commands, outputs, and errors in real-time.
- **No WSL Required**: Written in Python, relies on Paramiko for direct SSH/SFTP access, with enhanced compatibility for Dropbear servers (fixes "EOF during negotiation" errors).
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
   python "OWrtBackup&RestoreWin.py"
   ```
3. Enter your router credentials (IP, username, password) in the top section.
4. **To Backup:** Go to the "Backup Configuration" tab, select a destination folder, optionally check the "Extract archive" box, and click "Start Backup".
5. **To Restore/Flash:** Go to the "Restore Firmware" tab, select your firmware `.bin` or `.img` file. Check "Force flash" to bypass version checks, and click "Start Restore". The tool will upload the image and reboot the router.

## Building a Standalone Executable (.exe)
An automated batch script is provided to compile this Python script into a native Windows executable, allowing you to run it on machines without Python installed.
1. Simply double-click `build_app.bat`.
2. Allow Administrator privileges if prompted (required for automatic Python installation).
3. The script will automatically download and install Python (if missing), setup a virtual environment, install dependencies, compile the application into `OWrtBackup&RestoreWin.exe`, and clean up all temporary files.

*Note: Make sure to copy the `locales` folder next to the generated executable so the languages work!*

---

# Инструмент Backup & Restore для OpenWRT (Windows GUI)

Нативное графическое приложение для Windows, предназначенное для резервного копирования конфигурации и прошивки роутера OpenWRT по SSH. Инструмент работает в Windows без необходимости использовать Windows Subsystem for Linux (WSL).

Это приложение особенно полезно при работе с **OpenWRT ImageBuilder**:
- **Бэкап**: Приложение скачивает текущую конфигурацию роутера (`sysupgrade -b`) и автоматически распаковывает архив, чтобы вы могли сразу поместить полученные файлы в папку `files/` (overlay).
- **Прошивка**: Приложение умеет загружать и прошивать новые файлы образов (`.bin`/`.img`) с возможностью принудительной прошивки (`-F`), чтобы избежать ошибок несовпадения версий.

## Особенности
- **Нативный GUI**: Интерфейс с вкладками (Backup / Restore) на базе Tkinter.
- **Мультиязычность**: Поддержка английского и русского языков через внешние конфигурационные файлы `.json`.
- **Подробное логирование**: Раскрывающаяся встроенная панель журнала действий для отслеживания SSH-команд, их вывода и ошибок в реальном времени.
- **Без WSL**: Написано на Python, использует Paramiko для прямого доступа по SSH/SFTP. Улучшена совместимость с серверами Dropbear (исправлена ошибка "EOF during negotiation").
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
   python "OWrtBackup&RestoreWin.py"
   ```
3. Введите данные для входа на роутер (IP, пользователь, пароль) в верхней части окна.
4. **Для бэкапа:** Перейдите на вкладку «Резервное копирование», выберите папку, отметьте распаковку (по желанию) и нажмите «Начать копирование».
5. **Для прошивки:** Перейдите на вкладку «Восстановление прошивки», выберите файл `.bin` или `.img`. Отметьте «Принудительная прошивка» для обхода проверки версий и нажмите «Начать прошивку». Утилита загрузит образ и отправит роутер в перезагрузку.

## Сборка в автономный исполняемый файл (.exe)
Для автоматической компиляции скрипта в нативный исполняемый файл Windows предусмотрен специальный скрипт.
1. Просто запустите двойным кликом файл `build_app.bat`.
2. Разрешите права администратора при запросе (они нужны для автоматической установки Python, если он отсутствует).
3. Скрипт сам скачает и установит Python, создаст виртуальное окружение, установит зависимости, соберет приложение в файл `OWrtBackup&RestoreWin.exe` и очистит временные файлы.

*Примечание: Не забудьте скопировать папку `locales` рядом с созданным файлом, иначе локализация не будет работать!*
