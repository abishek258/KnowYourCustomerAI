@echo off
echo 🚀 Setting up NCB KYC Document Processing System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r requirements.txt

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your Google Cloud credentials
)

echo ✅ Setup complete!
echo.
echo 🔧 Next steps:
echo 1. Edit .env file with your Google Cloud credentials
echo 2. Run backend: python -m src.api.main
echo 3. Run frontend: cd frontend ^&^& npm run dev
echo.
echo 📚 For deployment instructions, see DEPLOYMENT.md
pause
