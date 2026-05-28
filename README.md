# OpenWRT Backup & Restore Tool (Windows GUI)

A native Windows graphical application to backup your OpenWRT router's configuration and flash new firmware over SSH. It works entirely on Windows without needing Windows Subsystem for Linux (WSL).

This tool is especially useful if you are working with **OpenWRT ImageBuilder**:
- **Backup**: It can download the current router configuration (`sysupgrade -b`) and automatically extract the files so you can simply place them into the `files/` overlay directory.
- **Restore**: It can upload and flash a new firmware image (`.bin`/`.img`) directly from Windows, with a built-in force-flash (`-F`) option to bypass version mismatch errors.

## New Features in Version 2.0 (Apple Glassmorphism UI)
*   **True Native App (PyWebView):** The UI now runs in a standalone, hardware-accelerated WebView2 window. No browser artifacts, no scrollbars, no translation prompts.
*   **Glassmorphism UI:** Complete visual overhaul imitating macOS Big Sur/Sonoma aesthetic with frosted glass, dynamic transparency, and beautiful blurred backgrounds.
*   **Built-in Bilingual Support:** English and Russian locales are now hardcoded natively into the application. No external `locales/` folder required. Instant switching!
*   **Adaptive Resizing:** Window can be stretched or compressed freely without breaking the layout.
*   **Single Executable:** `OWrtBackup&RestoreWin.exe` is now fully standalone.

## Core Features
*   **Fast Configuration Backup:** Download a full `sysupgrade` backup (`.tar.gz`) from your router via SCP.
*   **Automatic Archive Extraction:** Optionally auto-extract the downloaded backup for immediate viewing.
- **Dynamic Window Resizing**: The application intelligently scales its height depending on whether the Action Log is visible, keeping the UI compact.
- **Multilingual**: Supports English and Russian via external `.json` configuration files.
- **Detailed Logging**: An expandable inline action log panel to track SSH commands, outputs, and errors in real-time.
- **No WSL Required**: Written in Python, relies on Paramiko for SSH access and `scp` for robust file transfers, with enhanced compatibility for Dropbear servers.
- **ImageBuilder Ready**: Extract backups directly for ImageBuilder's `files/` structure.
- **Force Flash**: Flashes new firmware "regardless of installed version" using `sysupgrade -F`.

## Requirements
- Python 3.8+
- The dependencies in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## How to Use
1. Run the application: `OWrtBackup&RestoreWin.exe`
2. Enter your router credentials (IP, username, password) in the top section.
3. **To Backup:** Go to the "Backup Configuration" tab, select a destination folder, optionally check the "Extract archive" box, and click "Start Backup".
4. **To Restore/Flash:** Go to the "Restore Firmware" tab, select your firmware `.bin` or `.img` file. Check "Force flash" to bypass version checks, and click "Start Restore". The tool will upload the image and reboot the router.

## Building a Standalone Executable (.exe)
An automated batch script is provided to compile this Python script into a native Windows executable.
1. Simply double-click `build_app.bat`.
2. Allow Administrator privileges if prompted (required for automatic Python installation).
3. The script will automatically download and install Python (if missing), setup a virtual environment, install dependencies, compile the application into `OWrtBackup&RestoreWin.exe`, and clean up all temporary files.

---

# Инструмент Backup & Restore для OpenWRT (Windows GUI)

Нативное графическое приложение для Windows, предназначенное для резервного копирования конфигурации и прошивки роутера OpenWRT по SSH. Инструмент работает в Windows без необходимости использовать Windows Subsystem for Linux (WSL).

Это приложение особенно полезно при работе с **OpenWRT ImageBuilder**:
- **Бэкап**: Приложение скачивает текущую конфигурацию роутера (`sysupgrade -b`) и автоматически распаковывает архив, чтобы вы могли сразу поместить полученные файлы в папку `files/` (overlay).
- **Прошивка**: Приложение умеет загружать и прошивать новые файлы образов (`.bin`/`.img`) с возможностью принудительной прошивки (`-F`), чтобы избежать ошибок несовпадения версий.

## Особенности
- **Современный нативный GUI**: Интерфейс с вкладками на базе CustomTkinter, поддерживающий системную темную/светлую темы.
- **Меню настроек**: Интерактивное меню для смены темы (светлая/темная/системная), регулировки прозрачности окна и быстрых ссылок на GitHub и форум OpenWrt.
- **Умное определение IP**: Приложение автоматически подставляет IP-адрес шлюза по умолчанию вашей системы.
- **Живая проверка OpenWrt**: Фоновый процесс проверяет IP на принадлежность к OpenWrt (через баннеры SSH и LuCI) и выводит статусный значок ✅.
- **Динамический размер окна**: Приложение автоматически обрезает пустую нижнюю область, когда окно логов скрыто, для большей компактности.
- **Мультиязычность**: Поддержка английского и русского языков через внешние конфигурационные файлы `.json`.
- **Подробное логирование**: Раскрывающаяся встроенная панель журнала действий для отслеживания SSH-команд, их вывода и ошибок в реальном времени.
- **Без WSL**: Написано на Python, использует Paramiko для SSH и `scp` для надежной передачи файлов. Улучшена совместимость с серверами Dropbear.
- **Готовность для ImageBuilder**: Распаковка файлов прямо под структуру ImageBuilder.
- **Принудительная прошивка**: Прошивает образ «независимо от установленной версии» с помощью ключа `sysupgrade -F`.

## Требования
- Python 3.8+
- Зависимости, указанные в `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## Как использовать
1. Запустите приложение: `OWrtBackup&RestoreWin.exe`
2. Введите данные для входа на роутер (IP, пользователь, пароль) в верхней части окна.
3. **Для бэкапа:** Перейдите на вкладку «Резервное копирование», выберите папку, отметьте распаковку (по желанию) и нажмите «Начать копирование».
4. **Для прошивки:** Перейдите на вкладку «Восстановление прошивки», выберите файл `.bin` или `.img`. Отметьте «Принудительная прошивка» для обхода проверки версий и нажмите «Начать прошивку». Утилита загрузит образ и отправит роутер в перезагрузку.

## Сборка в автономный исполняемый файл (.exe)
Для автоматической компиляции скрипта в нативный исполняемый файл Windows предусмотрен специальный скрипт.
1. Просто запустите двойным кликом файл `build_app.bat`.
2. Разрешите права администратора при запросе (они нужны для автоматической установки Python, если он отсутствует).
3. Скрипт сам скачает и установит Python, создаст виртуальное окружение, установит зависимости, соберет приложение в файл `OWrtBackup&RestoreWin.exe` и очистит временные файлы.
