#!/bin/bash

# NCB KYC Document Processing - Setup Script
echo "🚀 Setting up NCB KYC Document Processing System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your Google Cloud credentials"
fi

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit .env file with your Google Cloud credentials"
echo "2. Run backend: python -m src.api.main"
echo "3. Run frontend: cd frontend && npm run dev"
echo ""
echo "📚 For deployment instructions, see DEPLOYMENT.md"
