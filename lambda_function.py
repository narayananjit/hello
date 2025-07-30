import boto3
import os
import io
import json
from datetime import datetime
import docx2txt
from pdfminer.high_level import extract_text

# === CONFIGURATION ===
# Bedrock Agent Details
AGENT_ID = "LG2JNI6Q3W"
AGENT_ALIAS_ID = "V9THA2P0W6"

# === UTILITIES ===
def extract_text_from_pdf(file_stream):
    """Extract text from PDF file stream"""
    try:
        temp_path = "/tmp/temp.pdf"
        with open(temp_path, "wb") as f:
            f.write(file_stream.read())
        text = extract_text(temp_path).strip()
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return text
    except Exception as e:
        raise Exception(f"PDF text extraction failed: {str(e)}")

def extract_text_from_docx(file_stream):
    """Extract text from DOCX file stream"""
    try:
        temp_path = "/tmp/temp.docx"
        with open(temp_path, "wb") as f:
            f.write(file_stream.read())
        text = docx2txt.process(temp_path).strip()
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return text
    except Exception as e:
        raise Exception(f"DOCX text extraction failed: {str(e)}")

def call_bedrock_agent(text):
    """Call Bedrock agent to parse resume text"""
    try:
        client = boto3.client('bedrock-agent-runtime')
        
        # Create a unique session ID
        session_id = f"session_{int(datetime.utcnow().timestamp())}"
        
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            input={"inputText": text}
        )
        
        # Collect and combine response chunks
        chunks = []
        for chunk in response.get('completion', []):
            if 'content' in chunk:
                chunks.append(chunk['content'])
        
        combined_response = "".join(chunks)
        
        # Try to parse as JSON
        try:
            return json.loads(combined_response)
        except json.JSONDecodeError:
            # If not valid JSON, return as structured text
            return {
                "parsed_text": combined_response,
                "status": "parsed_as_text"
            }
            
    except Exception as e:
        raise Exception(f"Bedrock agent call failed: {str(e)}")

# === LAMBDA HANDLER ===
def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        s3 = boto3.client('s3')
        
        # Step 1: Extract file info from S3 trigger
        if 'Records' not in event or not event['Records']:
            raise Exception("No S3 records found in event")
            
        record = event['Records'][0]
        if 's3' not in record:
            raise Exception("Invalid S3 event record")
            
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        file_name = os.path.basename(object_key)
        
        print(f"Processing file: {file_name} from bucket: {bucket_name}")
        
        # Step 2: Download the file from S3
        try:
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            file_stream = io.BytesIO(response['Body'].read())
        except Exception as e:
            raise Exception(f"Failed to download file from S3: {str(e)}")
        
        # Step 3: Extract text from resume
        try:
            if file_name.lower().endswith('.pdf'):
                raw_text = extract_text_from_pdf(file_stream)
            elif file_name.lower().endswith('.docx'):
                raw_text = extract_text_from_docx(file_stream)
            else:
                raise Exception(f"Unsupported file format: {file_name}")
                
            if not raw_text or len(raw_text.strip()) == 0:
                raise Exception("No text extracted from file")
                
            print(f"Extracted {len(raw_text)} characters from {file_name}")
            
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
        
        # Step 4: Parse using Bedrock agent
        try:
            structured_resume = call_bedrock_agent(raw_text)
            print("Successfully parsed resume with Bedrock agent")
        except Exception as e:
            raise Exception(f"Bedrock Agent Error: {str(e)}")
        
        # Step 5: Save the parsed output as JSON to S3
        try:
            output_key = f"parsed/{file_name.rsplit('.', 1)[0]}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=output_key,
                Body=json.dumps(structured_resume, indent=2, default=str),
                ContentType='application/json'
            )
            print(f"Successfully saved parsed resume to s3://{bucket_name}/{output_key}")
        except Exception as e:
            raise Exception(f"Failed to save parsed resume to S3: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"✅ Resume parsed and saved to s3://{bucket_name}/{output_key}",
                'input_file': file_name,
                'output_file': output_key,
                'text_length': len(raw_text)
            })
        }
        
    except Exception as e:
        error_message = f"Lambda execution failed: {str(e)}"
        print(f"ERROR: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            })
        }