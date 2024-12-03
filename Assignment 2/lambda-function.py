import boto3
from datetime import datetime, timezone, timedelta

def lambda_handler(event, context):
    # Define the S3 bucket name
    bucket_name = "old-files-cleanup-bucket"  # Replace with your bucket name
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Calculate the threshold date (30 days ago)
    threshold_date = datetime.now(timezone.utc) - timedelta(days=30)
    
    try:
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        # Check if the bucket contains objects
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key']
                last_modified = obj['LastModified']
                
                # Compare object date with the threshold date
                if last_modified < threshold_date:
                    # Delete the object
                    s3.delete_object(Bucket=bucket_name, Key=file_name)
                    print(f"Deleted: {file_name}")
                else:
                    print(f"Retained: {file_name}")
        else:
            print(f"No objects found in the bucket {bucket_name}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': f"S3 cleanup completed for bucket: {bucket_name}"
    }
