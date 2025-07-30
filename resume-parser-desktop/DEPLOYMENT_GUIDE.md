# Resume Parser Lambda Deployment Guide

## Issues Fixed in the Updated Code

### 1. **Unhandled Exceptions**
- Added comprehensive try-catch blocks around all major operations
- Added proper error handling for S3 operations, text extraction, and Bedrock agent calls
- Added input validation for S3 event structure

### 2. **File Stream Handling**
- Fixed file stream reading issues by properly handling BytesIO objects
- Added proper cleanup of temporary files
- Added validation for extracted text content

### 3. **Bedrock Agent Response Handling**
- Improved response chunk processing with proper null checks
- Added fallback handling for non-JSON responses
- Added unique session ID generation

### 4. **JSON Serialization**
- Added `default=str` parameter to handle non-serializable objects
- Added proper error handling for JSON parsing

## Required AWS Permissions

### Lambda Execution Role Permissions
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

## Lambda Configuration

### Runtime Settings
- **Runtime**: Python 3.9 or 3.10
- **Memory**: 512 MB (minimum recommended)
- **Timeout**: 5 minutes (300 seconds)
- **Architecture**: x86_64

### Environment Variables
```
AGENT_ID=LG2JNI6Q3W
AGENT_ALIAS_ID=V9THA2P0W6
```

### Layer Dependencies
Since `docx2txt` and `pdfminer.six` are not available in the Lambda runtime, you need to create a Lambda layer:

1. **Create a deployment package:**
```bash
# Create a directory for the layer
mkdir -p lambda-layer/python

# Install dependencies
pip install -r requirements.txt -t lambda-layer/python

# Create ZIP file
cd lambda-layer
zip -r ../lambda-layer.zip .
cd ..
```

2. **Upload as Lambda Layer:**
   - Go to AWS Lambda Console
   - Create a new layer
   - Upload the `lambda-layer.zip`
   - Attach the layer to your Lambda function

## S3 Event Notification Configuration

### Bucket Policy
Ensure your S3 bucket has the following notification configuration:

```json
{
    "LambdaConfigurations": [
        {
            "Id": "resume-parser-trigger",
            "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT:function:FUNCTION-NAME",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {
                            "Name": "suffix",
                            "Value": ".pdf"
                        },
                        {
                            "Name": "suffix", 
                            "Value": ".docx"
                        }
                    ]
                }
            }
        }
    ]
}
```

## Testing the Function

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

## Monitoring and Troubleshooting

### CloudWatch Logs
The function now includes comprehensive logging:
- File processing status
- Text extraction results
- Bedrock agent responses
- S3 upload confirmations
- Detailed error messages

### Common Issues and Solutions

1. **Timeout Errors**
   - Increase Lambda timeout to 5 minutes
   - Increase memory allocation to 1024 MB

2. **Permission Errors**
   - Verify Lambda execution role has all required permissions
   - Check S3 bucket permissions
   - Verify Bedrock agent access

3. **Memory Errors**
   - Increase Lambda memory allocation
   - Check for large PDF files (consider file size limits)

4. **Bedrock Agent Errors**
   - Verify agent ID and alias ID are correct
   - Check agent status in Bedrock console
   - Verify agent has proper instructions configured

## Security Considerations

1. **IAM Roles**: Use least privilege principle
2. **S3 Bucket**: Enable encryption at rest
3. **Lambda**: Enable VPC if needed for additional security
4. **Bedrock**: Ensure agent instructions don't expose sensitive data

## Cost Optimization

1. **Memory**: Start with 512 MB, adjust based on performance
2. **Timeout**: Set appropriate timeout to avoid unnecessary charges
3. **S3 Lifecycle**: Implement lifecycle policies for parsed files
4. **Bedrock**: Monitor agent usage and costs