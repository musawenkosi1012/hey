#!/bin/bash
# Build script for Render deployment

set -e  # Exit on error

echo "🚀 Starting Render build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

echo "✅ Build completed successfully!"
