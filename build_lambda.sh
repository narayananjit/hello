#!/bin/bash

# Resume Parser Lambda Builder Script
# This script creates a deployment package for AWS Lambda

set -e  # Exit on any error

echo "🚀 Starting Lambda build process..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "lambda_function.py" ]; then
    echo "❌ lambda_function.py not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Create build directory
BUILD_DIR="lambda-build"
if [ -d "$BUILD_DIR" ]; then
    echo "🧹 Cleaning previous build directory..."
    rm -rf "$BUILD_DIR"
fi

echo "📁 Creating build directory..."
mkdir -p "$BUILD_DIR"

# Copy Lambda function
echo "📄 Copying Lambda function..."
cp lambda_function.py "$BUILD_DIR/"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -t "$BUILD_DIR"

# Create ZIP file
echo "🗜️ Creating deployment package..."
ZIP_FILE="resume-parser-lambda.zip"

# Remove existing ZIP if it exists
if [ -f "$ZIP_FILE" ]; then
    rm "$ZIP_FILE"
fi

# Create ZIP with all contents
cd "$BUILD_DIR"
zip -r "../$ZIP_FILE" .
cd ..

# Get file size
FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)

echo "✅ Build completed successfully!"
echo "📦 Deployment package: $ZIP_FILE"
echo "📊 Package size: $FILE_SIZE"

# Clean up build directory
echo "🧹 Cleaning up build files..."
rm -rf "$BUILD_DIR"

echo ""
echo "🎉 Lambda package ready for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Upload $ZIP_FILE to AWS Lambda Console"
echo "2. Set handler to: lambda_function.lambda_handler"
echo "3. Configure runtime: Python 3.9 or 3.10"
echo "4. Set timeout: 5 minutes (300 seconds)"
echo "5. Set memory: 512 MB or higher"
echo "6. Add environment variables:"
echo "   - AGENT_ID=LG2JNI6Q3W"
echo "   - AGENT_ALIAS_ID=V9THA2P0W6"
echo "7. Configure IAM permissions (see DEPLOYMENT_GUIDE.md)"
echo ""
echo "🔗 AWS Lambda Console: https://console.aws.amazon.com/lambda/"