# Desktop Application Guide for Resume Parser Lambda

## 🖥️ Opening the Lambda Package on Your Desktop

### 📁 **What You Have**
- `resume-parser-lambda.zip` - The main deployment package
- Source code files for reference and modification

## 🚀 **Method 1: Extract and View (Recommended)**

### Step 1: Extract the ZIP File
```bash
# On Windows (Command Prompt)
unzip resume-parser-lambda.zip -d resume-parser-lambda

# On macOS/Linux (Terminal)
unzip resume-parser-lambda.zip -d resume-parser-lambda

# Or use your file explorer:
# Right-click → Extract All → Choose destination folder
```

### Step 2: Open in Your Code Editor
**VS Code:**
```bash
# Open VS Code in the extracted folder
code resume-parser-lambda

# Or from VS Code menu: File → Open Folder → Select resume-parser-lambda
```

**PyCharm:**
```bash
# Open PyCharm → Open → Select resume-parser-lambda folder
```

**Sublime Text:**
```bash
# Open Sublime Text → File → Open Folder → Select resume-parser-lambda
```

## 🔧 **Method 2: Development Environment Setup**

### Step 1: Create a Development Directory
```bash
# Create a new development folder
mkdir resume-parser-development
cd resume-parser-development

# Extract the Lambda package
unzip ../resume-parser-lambda.zip
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies for development
pip install -r requirements.txt
pip install pytest  # for testing
pip install awscli   # for AWS operations
```

### Step 3: Open in Your IDE
```bash
# VS Code
code .

# PyCharm
# File → Open → Select resume-parser-development folder
```

## 📝 **Method 3: Local Testing Setup**

### Step 1: Create Test Environment
```bash
# Create test directory
mkdir resume-parser-test
cd resume-parser-test

# Copy the Lambda function
cp ../lambda_function.py .

# Create test requirements
echo "boto3>=1.26.0" > requirements.txt
echo "docx2txt>=0.8" >> requirements.txt
echo "pdfminer.six>=20221105" >> requirements.txt
echo "pytest>=7.0.0" >> requirements.txt
echo "moto>=4.0.0" >> requirements.txt  # for AWS mocking
```

### Step 2: Create Test Files
Create `test_lambda.py`:
```python
import pytest
import json
from unittest.mock import Mock, patch
from lambda_function import lambda_handler

def test_s3_event_processing():
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

if __name__ == "__main__":
    pytest.main([__file__])
```

### Step 3: Run Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
python -m pytest test_lambda.py -v
```

## 🎯 **Method 4: AWS SAM Local Development**

### Step 1: Install AWS SAM CLI
```bash
# On Windows (using Chocolatey)
choco install aws-sam-cli

# On macOS (using Homebrew)
brew install aws-sam-cli

# On Linux
pip install aws-sam-cli
```

### Step 2: Create SAM Template
Create `template.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ResumeParserFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_function.lambda_handler
      Runtime: python3.9
      Timeout: 300
      MemorySize: 512
      Environment:
        Variables:
          AGENT_ID: LG2JNI6Q3W
          AGENT_ALIAS_ID: V9THA2P0W6
      Policies:
        - S3ReadPolicy:
            BucketName: your-bucket-name
        - BedrockInvokeAgentPolicy: {}

Events:
  S3Event:
    Type: S3
    Properties:
      Bucket: !Ref ResumeBucket
      Events: s3:ObjectCreated:*
      Filter:
        S3Key:
          Rules:
            - Name: suffix
              Value: .pdf
            - Name: suffix
              Value: .docx

  ResumeBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: resume-parser-bucket
```

### Step 3: Run Locally
```bash
# Build the application
sam build

# Run locally
sam local start-api

# Test with a sample event
sam local invoke ResumeParserFunction -e events/s3-event.json
```

## 🔍 **Method 5: IDE-Specific Setup**

### VS Code Setup
1. **Install Extensions:**
   - Python
   - AWS Toolkit
   - YAML
   - Docker

2. **Create VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "."
    ]
}
```

3. **Create Launch Configuration** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Lambda Test",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test_lambda.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

### PyCharm Setup
1. **Configure Project:**
   - File → Settings → Project → Python Interpreter
   - Add your virtual environment

2. **Create Run Configuration:**
   - Run → Edit Configurations
   - Add Python configuration
   - Set script path to `test_lambda.py`

## 📊 **Method 6: Monitoring and Debugging**

### Create Debug Script
Create `debug_lambda.py`:
```python
import logging
import json
from lambda_function import lambda_handler

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_lambda():
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
```

## 🎯 **Quick Start Commands**

```bash
# 1. Extract the package
unzip resume-parser-lambda.zip -d resume-parser

# 2. Open in VS Code
code resume-parser

# 3. Set up virtual environment
cd resume-parser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run tests
python test_lambda.py
```

## 📞 **Need Help?**

1. **Check the logs** in your IDE's console
2. **Verify Python version** (3.7+ required)
3. **Ensure all dependencies** are installed
4. **Check AWS credentials** if testing with real AWS services
5. **Use the debug script** to isolate issues

## 🎉 **You're Ready!**

Your Lambda function is now ready for:
- ✅ Local development and testing
- ✅ IDE integration and debugging
- ✅ AWS deployment
- ✅ Continuous integration

Choose the method that best fits your workflow and start developing!