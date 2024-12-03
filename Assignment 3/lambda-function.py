import boto3
import datetime
import time

def lambda_handler(event, context):
    # Log the full event for debugging
    print("Full Event Received:", event)
    
    # Check for 'detail' and 'responseElements' in the event
    detail = event.get('detail', {})
    response_elements = detail.get('responseElements', {})
    
    if not response_elements:
        print("Missing 'responseElements' in event")
        return {"statusCode": 400, "body": "Invalid event format"}
    
    # Extract instance IDs
    instances = response_elements.get('instancesSet', {}).get('items', [])
    instance_ids = [item.get('instanceId') for item in instances if 'instanceId' in item]
    
    if not instance_ids:
        print("No instance IDs found in event")
        return {"statusCode": 400, "body": "No instance IDs found in event"}
    
    ec2_client = boto3.client('ec2')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    tags = [{'Key': 'LaunchDate', 'Value': current_date}, {'Key': 'CustomTag', 'Value': 'AutoTagged'}]
    
    # Retry logic for tagging
    for instance_id in instance_ids:
        for _ in range(5):  # Retry up to 5 times
            try:
                print(f"Trying to tag instance: {instance_id}")
                ec2_client.create_tags(Resources=[instance_id], Tags=tags)
                print(f"Successfully tagged instance {instance_id} with {tags}")
                break
            except Exception as e:
                print(f"Error tagging instance {instance_id}: {e}")
                time.sleep(5)  # Wait before retrying

    return {"statusCode": 200, "body": f"Processed instance IDs: {instance_ids}"}
