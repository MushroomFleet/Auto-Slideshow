@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Auto-Slideshow Generator
echo ========================================
echo.

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Virtual environment not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)
echo Done!
echo.

:: Ask user for the folder path
set /p FOLDER_PATH="Enter the path to your images folder: "

:: Validate folder path
if not exist "%FOLDER_PATH%" (
    echo Error: The folder "%FOLDER_PATH%" does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

:: Ask if user wants to specify a custom output file
set OUTPUT_OPTION=
set /p CUSTOM_OUTPUT="Do you want to specify a custom output filename? (y/n): "
if /i "%CUSTOM_OUTPUT%" == "y" (
    set /p OUTPUT_FILE="Enter the output filename (e.g., my_slideshow.mp4): "
    set OUTPUT_OPTION=-o "!OUTPUT_FILE!"
)

:: Ask if user wants to use a custom config file
set CONFIG_OPTION=
set /p CUSTOM_CONFIG="Do you want to use a custom config file? (y/n): "
if /i "%CUSTOM_CONFIG%" == "y" (
    set /p CONFIG_FILE="Enter the path to your config file: "
    if not exist "!CONFIG_FILE!" (
        echo Warning: The config file "!CONFIG_FILE!" does not exist.
        echo The default config will be used instead.
    ) else (
        set CONFIG_OPTION=-c "!CONFIG_FILE!"
    )
)

:: Confirm settings
echo.
echo ========================================
echo SETTINGS SUMMARY:
echo.
echo Images folder: %FOLDER_PATH%
if defined OUTPUT_FILE (
    echo Output file: !OUTPUT_FILE!
) else (
    echo Output file: slideshow.mp4 ^(default^)
)
if defined CONFIG_FILE (
    if exist "!CONFIG_FILE!" (
        echo Config file: !CONFIG_FILE!
    ) else (
        echo Config file: Default ^(custom file not found^)
    )
) else (
    echo Config file: Default
)
echo.
echo ========================================
echo.

:: Ask for confirmation
set /p CONFIRM="Do you want to proceed with these settings? (y/n): "
if /i not "%CONFIRM%" == "y" (
    echo Operation cancelled by user.
    echo.
    pause
    exit /b 0
)

:: Run the script with collected parameters
echo.
echo Running Auto-Slideshow Generator...
echo.

python auto_slideshow.py "%FOLDER_PATH%" %OUTPUT_OPTION% %CONFIG_OPTION%

:: Check if the script ran successfully
if %errorlevel% neq 0 (
    echo.
    echo The script encountered an error.
) else (
    echo.
    echo Slideshow created successfully!
)

echo.
echo ========================================
echo.

pause
endlocal
