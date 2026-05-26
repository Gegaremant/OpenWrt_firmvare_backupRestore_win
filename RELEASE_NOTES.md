# Release Notes

## Changes since last commit (Release 1.0.0)

### 🚀 New Features
- **Expandable Action Log**: Added a Windows-style expandable logging panel directly at the bottom of the GUI. You can now monitor the progress of SSH commands, view standard outputs (`stdout`) and errors (`stderr`), and easily debug connection or execution issues without separate popup windows.
- **Log Localization**: The new logging panel is fully translated and supports both English and Russian locales.
- **Automated Build Script**: Replaced manual compilation steps with a fully automated `build_app.bat` script. It automatically requests admin rights, downloads and installs Python if missing, sets up a virtual environment, builds the executable, and cleans up temporary files.

### 🐛 Bug Fixes
- **Paramiko Connection Fix**: Addressed the "EOF during negotiation" error that occurred when connecting to some OpenWrt routers running Dropbear. The `ssh.connect` function now uses `look_for_keys=False` and `allow_agent=False` with a specific `banner_timeout`, which reliably stabilizes the initial SSH handshake.
- **Error Handling**: Dramatically improved exception handling to capture and display full Python stacktraces directly inside the application's Action Log, removing the need to check the console.

---

# Описание обновления

## Изменения с прошлого коммита (Релиз 1.0.0)

### 🚀 Новые возможности
- **Раскрывающаяся панель журнала действий**: В графический интерфейс добавлена встроенная раскладывающаяся панель логов (в стиле Windows). Теперь можно в реальном времени отслеживать ход выполнения SSH-команд, просматривать стандартный вывод (`stdout`) и ошибки (`stderr`), что значительно упрощает отладку без лишних всплывающих окон.
- **Локализация журнала**: Панель логов полностью переведена и поддерживает переключение между английским и русским языками.
- **Автоматизированный скрипт сборки**: Добавлен скрипт `build_app.bat`, который полностью автоматизирует процесс создания `.exe` файла. Он сам запрашивает права администратора, скачивает и устанавливает Python при его отсутствии, собирает проект и очищает за собой временные файлы.

### 🐛 Исправления ошибок
- **Исправление подключения Paramiko**: Исправлена ошибка "EOF during negotiation", возникавшая при подключении к некоторым роутерам OpenWrt с сервером Dropbear. Теперь функция `ssh.connect` вызывается с параметрами `look_for_keys=False` и `allow_agent=False`, что делает первичный обмен ключами по SSH стабильным.
- **Обработка ошибок**: Значительно улучшен перехват исключений — теперь полные трассировки стека (stacktraces) выводятся прямо в журнал действий приложения, избавляя от необходимости искать их в консоли.
