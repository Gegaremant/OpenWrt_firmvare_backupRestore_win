# Release Notes

## Version 1.0.2 (Apple Glassmorphism UI)
*   **Architecture Overhaul (PyWebView):** Replaced CustomTkinter/Eel with a highly optimized HTML/CSS/JS frontend powered by PyWebView.
*   **Glassmorphism Theme:** Introduced a beautiful, modern macOS-inspired frosted glass interface with dynamic transparency sliders.
*   **Blurred Cyberpunk Background:** Included a high-quality blurred server-room background by default, with optimized static CSS sizing to prevent scaling jumps.
*   **Hardcoded Bilingual Locales:** English and Russian dictionaries are now seamlessly embedded in the main executable. No more `locales/` directory required!
*   **Adaptive Grid Layout:** Input fields and labels use a fixed grid layout, perfectly aligning inputs and eliminating UI jumping when switching languages.
*   **Native Window Mode:** The application is completely detached from browser artifacts—no translation prompts or scrollbars.
*   **OpenWrt Icon Integration:** The application executable and taskbar window now proudly display the OpenWrt logo.
*   **Automated Build Pipeline:** Enhanced `build_app.bat` script automatically builds a single standalone `.exe`, cleans up residual files, and auto-launches the app with a countdown timer.
