#!/usr/bin/env python3
"""
Lambda Packaging Script for Resume Parser
This script creates a deployment package for AWS Lambda with all dependencies.
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def create_directory(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"📁 Created directory: {path}")

def main():
    print("🚀 Starting Lambda packaging process...")
    
    # Create deployment directory
    deployment_dir = "lambda-deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    create_directory(deployment_dir)
    
    # Create Python package directory
    python_dir = os.path.join(deployment_dir, "python")
    create_directory(python_dir)
    
    # Copy the main Lambda function
    print("📄 Copying Lambda function...")
    shutil.copy("lambda_function.py", os.path.join(deployment_dir, "lambda_function.py"))
    
    # Install dependencies
    print("📦 Installing dependencies...")
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    install_cmd = f"pip install -r {requirements_file} -t {python_dir}"
    run_command(install_cmd, "Installing Python dependencies")
    
    # Create deployment ZIP
    print("🗜️ Creating deployment package...")
    zip_filename = "resume-parser-lambda.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the main function
        zipf.write(os.path.join(deployment_dir, "lambda_function.py"), "lambda_function.py")
        
        # Add all Python packages
        for root, dirs, files in os.walk(python_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arc_name)
    
    # Get file size
    file_size = os.path.getsize(zip_filename) / (1024 * 1024)  # Convert to MB
    
    print(f"✅ Deployment package created: {zip_filename}")
    print(f"📊 Package size: {file_size:.2f} MB")
    
    # Clean up
    shutil.rmtree(deployment_dir)
    print("🧹 Cleaned up temporary files")
    
    print("\n🎉 Packaging completed successfully!")
    print(f"📦 Your Lambda deployment package: {zip_filename}")
    print("\n📋 Next steps:")
    print("1. Upload the ZIP file to AWS Lambda")
    print("2. Set the handler to: lambda_function.lambda_handler")
    print("3. Configure runtime as Python 3.9 or 3.10")
    print("4. Set timeout to 5 minutes (300 seconds)")
    print("5. Set memory to 512 MB or higher")
    print("6. Configure environment variables (AGENT_ID, AGENT_ALIAS_ID)")
    print("7. Set up proper IAM permissions")

if __name__ == "__main__":
    main()