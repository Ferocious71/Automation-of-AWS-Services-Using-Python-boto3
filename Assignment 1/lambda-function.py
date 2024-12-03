import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    
    # Describe all EC2 instances
    instances = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Action', 'Values': ['Auto-Stop', 'Auto-Start']}
        ]
    )
    
    auto_stop_instances = []
    auto_start_instances = []
    
    # Debugging: Log all instances and their tags
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            print(f"Instance ID: {instance['InstanceId']}, State: {instance['State']['Name']}, Tags: {instance.get('Tags')}")
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Action' and tag['Value'] == 'Auto-Stop':
                        auto_stop_instances.append(instance['InstanceId'])
                    elif tag['Key'] == 'Action' and tag['Value'] == 'Auto-Start':
                        auto_start_instances.append(instance['InstanceId'])
    
    # Stop Auto-Stop instances
    if auto_stop_instances:
        print(f"Stopping instances: {auto_stop_instances}")
        ec2_client.stop_instances(InstanceIds=auto_stop_instances)
    
    # Start Auto-Start instances
    if auto_start_instances:
        print(f"Starting instances: {auto_start_instances}")
        ec2_client.start_instances(InstanceIds=auto_start_instances)
    
    return {
        'statusCode': 200,
        'body': f"Processed instances: Auto-Stop {auto_stop_instances}, Auto-Start {auto_start_instances}"
    }
