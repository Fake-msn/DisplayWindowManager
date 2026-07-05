@echo off
chcp 65001 >nul
echo ========================================
echo   鏄剧ず鍣ㄧ獥鍙ｇ鐞嗗櫒 - 鎵撳寘宸ュ叿
echo ========================================
echo.

REM 妫€鏌?Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [閿欒] 鏈壘鍒?Python锛岃鍏堝畨瑁?Python 3.8+
    pause
    exit /b 1
)

REM 妫€鏌?瀹夎 pyinstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [淇℃伅] 姝ｅ湪瀹夎 pyinstaller...
    pip install pyinstaller
)

echo [淇℃伅] 寮€濮嬫墦鍖?..
echo.

REM 鎵撳寘涓哄崟涓?exe 鏂囦欢 (绾?Win32 API锛屾棤 tkinter 渚濊禆)
pyinstaller --onefile --windowed --name "DisplayWindowManager" ^
    --clean ^
    --noconfirm ^
    display_window_manager.py

echo.
echo ========================================
echo   鎵撳寘瀹屾垚锛?echo   杈撳嚭鏂囦欢: dist\DisplayWindowManager.exe
echo ========================================
pause