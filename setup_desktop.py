#!/usr/bin/env python3
"""
Desktop Setup Script for Resume Parser Lambda
This script helps you set up the Lambda package for desktop development.
"""

import os
import sys
import zipfile
import subprocess
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
        return None

def create_directory(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"📁 Created directory: {path}")

def main():
    print("🚀 Setting up Resume Parser Lambda for Desktop Development")
    print("=" * 60)
    
    # Check if ZIP file exists
    zip_file = "resume-parser-lambda.zip"
    if not os.path.exists(zip_file):
        print(f"❌ {zip_file} not found!")
        print("Please make sure the ZIP file is in the current directory.")
        return
    
    # Create development directory
    dev_dir = "resume-parser-desktop"
    if os.path.exists(dev_dir):
        print(f"🧹 Cleaning existing directory: {dev_dir}")
        shutil.rmtree(dev_dir)
    
    create_directory(dev_dir)
    
    # Extract ZIP file
    print("📦 Extracting Lambda package...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(dev_dir)
    
    # Copy source files for reference
    source_files = [
        "lambda_function.py",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT_GUIDE.md"
    ]
    
    for file in source_files:
        if os.path.exists(file):
            shutil.copy2(file, dev_dir)
            print(f"📄 Copied {file}")
    
    # Create virtual environment
    print("🐍 Setting up Python virtual environment...")
    os.chdir(dev_dir)
    
    # Check Python version
    python_version = run_command("python --version", "Checking Python version")
    if not python_version:
        print("❌ Python not found! Please install Python 3.7+")
        return
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        print("❌ Failed to create virtual environment")
        return
    
    # Create activation script
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if os.path.exists("requirements.txt"):
        if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
            print("❌ Failed to install requirements")
            return
    
    # Create test file
    test_file = "test_lambda.py"
    test_content = '''import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lambda_function import lambda_handler

def test_s3_event_processing():
    """Test the Lambda function with a mock S3 event"""
    # Mock S3 event
    event = {
        "Records": [{
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "2023-01-01T12:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "test-config",
                "bucket": {
                    "name": "test-bucket",
                    "ownerIdentity": {"principalId": "EXAMPLE"},
                    "arn": "arn:aws:s3:::test-bucket"
                },
                "object": {
                    "key": "resumes/test-resume.pdf",
                    "size": 1024,
                    "eTag": "0123456789abcdef0123456789abcdef",
                    "sequencer": "0A1B2C3D4E5F678901"
                }
            }
        }]
    }
    
    # Mock AWS services
    with patch('boto3.client') as mock_boto3:
        mock_s3 = Mock()
        mock_bedrock = Mock()
        mock_boto3.side_effect = [mock_s3, mock_bedrock]
        
        # Mock S3 response
        mock_s3.get_object.return_value = {
            'Body': Mock(read=lambda: b'Mock PDF content')
        }
        
        # Mock Bedrock response
        mock_bedrock.invoke_agent.return_value = {
            'completion': [{'content': '{"name": "John Doe", "email": "john@example.com"}'}]
        }
        
        # Test the function
        result = lambda_handler(event, {})
        
        assert result['statusCode'] == 200
        assert 'Resume parsed and saved' in result['body']
        print("✅ Test passed!")

if __name__ == "__main__":
    test_s3_event_processing()
'''
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    print(f"📝 Created {test_file}")
    
    # Create debug file
    debug_file = "debug_lambda.py"
    debug_content = '''import logging
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lambda_function import lambda_handler

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_lambda():
    """Debug the Lambda function locally"""
    # Sample event for testing
    test_event = {
        "Records": [{
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "2023-01-01T12:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "test-config",
                "bucket": {
                    "name": "test-bucket",
                    "ownerIdentity": {"principalId": "EXAMPLE"},
                    "arn": "arn:aws:s3:::test-bucket"
                },
                "object": {
                    "key": "resumes/test-resume.pdf",
                    "size": 1024,
                    "eTag": "0123456789abcdef0123456789abcdef",
                    "sequencer": "0A1B2C3D4E5F678901"
                }
            }
        }]
    }
    
    try:
        logger.info("Starting Lambda function test")
        result = lambda_handler(test_event, {})
        logger.info(f"Function completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Function failed: {str(e)}")
        raise

if __name__ == "__main__":
    debug_lambda()
'''
    
    with open(debug_file, 'w') as f:
        f.write(debug_content)
    print(f"🐛 Created {debug_file}")
    
    # Create VS Code settings
    vscode_dir = ".vscode"
    create_directory(vscode_dir)
    
    settings_file = os.path.join(vscode_dir, "settings.json")
    settings_content = '''{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "."
    ]
}'''
    
    with open(settings_file, 'w') as f:
        f.write(settings_content)
    print(f"⚙️ Created VS Code settings")
    
    # Create launch configuration
    launch_file = os.path.join(vscode_dir, "launch.json")
    launch_content = '''{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Lambda Test",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test_lambda.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Debug Lambda",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/debug_lambda.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}'''
    
    with open(launch_file, 'w') as f:
        f.write(launch_content)
    print(f"🚀 Created VS Code launch configuration")
    
    # Create README for the desktop setup
    readme_file = "DESKTOP_README.md"
    readme_content = '''# Resume Parser Lambda - Desktop Development

## 🎉 Setup Complete!

Your Lambda function is now ready for desktop development.

## 📁 What's Been Created

- `lambda_function.py` - Main Lambda function
- `requirements.txt` - Python dependencies
- `test_lambda.py` - Unit tests
- `debug_lambda.py` - Debug script
- `venv/` - Python virtual environment
- `.vscode/` - VS Code configuration

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# On Windows:
venv\\Scripts\\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Run Tests
```bash
python test_lambda.py
```

### 3. Debug the Function
```bash
python debug_lambda.py
```

### 4. Open in VS Code
```bash
code .
```

## 🔧 Development Workflow

1. **Make changes** to `lambda_function.py`
2. **Test locally** with `python test_lambda.py`
3. **Debug issues** with `python debug_lambda.py`
4. **Deploy to AWS** when ready

## 📚 Available Commands

- `python test_lambda.py` - Run unit tests
- `python debug_lambda.py` - Debug the function
- `pip install <package>` - Install new dependencies
- `python -m pytest` - Run pytest (if installed)

## 🎯 Next Steps

1. Open the project in your preferred IDE
2. Start developing and testing
3. Deploy to AWS when ready
4. Monitor with CloudWatch logs

Happy coding! 🚀
'''
    
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"📖 Created {readme_file}")
    
    # Go back to original directory
    os.chdir("..")
    
    print("\n" + "=" * 60)
    print("🎉 Desktop setup completed successfully!")
    print(f"📁 Your development environment is in: {dev_dir}")
    print("\n📋 Next steps:")
    print(f"1. cd {dev_dir}")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run tests: python test_lambda.py")
    print("4. Open in VS Code: code .")
    print("\n🔗 VS Code: https://code.visualstudio.com/")
    print("🔗 PyCharm: https://www.jetbrains.com/pycharm/")

if __name__ == "__main__":
    main()