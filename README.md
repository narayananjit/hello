# Resume Parser Lambda Function

A serverless AWS Lambda function that automatically parses resumes using AWS Bedrock Agent (Claude Sonnet 3). The function is triggered by S3 uploads and processes PDF/DOCX files to extract structured resume data.

## 📁 Project Structure

```
resume-parser-lambda/
├── lambda_function.py          # Main Lambda function
├── requirements.txt            # Python dependencies
├── package_lambda.py           # Python packaging script
├── build_lambda.sh             # Shell packaging script
├── DEPLOYMENT_GUIDE.md         # Detailed deployment guide
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Using Shell Script (Recommended)

```bash
# Make the script executable
chmod +x build_lambda.sh

# Run the build script
./build_lambda.sh
```

### Option 2: Using Python Script

```bash
# Run the Python packaging script
python3 package_lambda.py
```

### Option 3: Manual Build

```bash
# Create build directory
mkdir lambda-build
cd lambda-build

# Copy Lambda function
cp ../lambda_function.py .

# Install dependencies
pip install -r ../requirements.txt -t .

# Create ZIP file
zip -r ../resume-parser-lambda.zip .

# Clean up
cd ..
rm -rf lambda-build
```

## 📦 What Gets Created

After running any of the build methods, you'll get:
- `resume-parser-lambda.zip` - Ready-to-deploy Lambda package

## 🔧 Prerequisites

- Python 3.7+ installed
- pip package manager
- zip utility (usually pre-installed on Linux/macOS)
- AWS account with access to:
  - Lambda
  - S3
  - Bedrock
  - CloudWatch

## 📋 Deployment Steps

### 1. Upload to AWS Lambda

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click "Create function"
3. Choose "Author from scratch"
4. Fill in basic information:
   - Function name: `resume-parser`
   - Runtime: `Python 3.9` or `Python 3.10`
   - Architecture: `x86_64`
5. Click "Create function"

### 2. Upload Code

1. In the Lambda function page, scroll to "Code source"
2. Click "Upload from" → ".zip file"
3. Upload `resume-parser-lambda.zip`
4. Click "Save"

### 3. Configure Function Settings

1. **Handler**: `lambda_function.lambda_handler`
2. **Timeout**: 5 minutes (300 seconds)
3. **Memory**: 512 MB (minimum)

### 4. Add Environment Variables

Go to "Configuration" → "Environment variables" and add:
```
AGENT_ID=LG2JNI6Q3W
AGENT_ALIAS_ID=V9THA2P0W6
```

### 5. Configure IAM Permissions

Create or update the Lambda execution role with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeAgent"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:agent/*"
            ]
        }
    ]
}
```

### 6. Configure S3 Trigger

1. Go to "Configuration" → "Triggers"
2. Click "Add trigger"
3. Select "S3" as source
4. Configure:
   - Bucket: Your S3 bucket
   - Event type: `All object create events`
   - Prefix: `resumes/` (optional)
   - Suffix: `.pdf,.docx`

## 🧪 Testing

### Test Event Structure

```json
{
    "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "2023-01-01T12:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "test-config",
                "bucket": {
                    "name": "your-bucket-name",
                    "ownerIdentity": {
                        "principalId": "EXAMPLE"
                    },
                    "arn": "arn:aws:s3:::your-bucket-name"
                },
                "object": {
                    "key": "resumes/test-resume.pdf",
                    "size": 1024,
                    "eTag": "0123456789abcdef0123456789abcdef",
                    "sequencer": "0A1B2C3D4E5F678901"
                }
            }
        }
    ]
}
```

## 📊 Monitoring

- **CloudWatch Logs**: Check function logs for detailed execution information
- **CloudWatch Metrics**: Monitor invocation count, duration, and errors
- **S3**: Check the `parsed/` folder for output JSON files

## 🔍 Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase Lambda timeout to 5 minutes
   - Increase memory allocation

2. **Permission Errors**
   - Verify IAM role permissions
   - Check S3 bucket permissions
   - Verify Bedrock agent access

3. **Import Errors**
   - Ensure all dependencies are included in the ZIP
   - Check Python runtime version

4. **Bedrock Agent Errors**
   - Verify agent ID and alias ID
   - Check agent status in Bedrock console

### Debug Steps

1. Check CloudWatch logs for detailed error messages
2. Verify environment variables are set correctly
3. Test with a simple PDF file first
4. Ensure S3 bucket and file permissions are correct

## 📚 Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Detailed Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🤝 Support

If you encounter issues:
1. Check the CloudWatch logs for detailed error messages
2. Verify all configuration steps are completed
3. Ensure your AWS account has the necessary permissions
4. Test with the provided test event structure

## 📄 License

This project is provided as-is for educational and development purposes.