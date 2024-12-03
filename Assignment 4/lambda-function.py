import boto3
import os
from datetime import datetime, timedelta

# Initialize Boto3 clients
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')  # Replace with your region
sns = boto3.client('sns', region_name='us-east-1')

# Environment variables for configuration (optional, for flexibility)
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')  # Replace with your SNS ARN
THRESHOLD = float(os.getenv('BILLING_THRESHOLD', '0.1'))  # Example threshold: $0.1

def lambda_handler(event, context):
    try:
        # Get billing metric from CloudWatch
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/Billing',
            MetricName='EstimatedCharges',
            Dimensions=[{'Name': 'Currency', 'Value': 'USD'}],
            StartTime=datetime.utcnow() - timedelta(hours=24),
            EndTime=datetime.utcnow(),
            Period=86400,
            Statistics=['Maximum']
        )

        # Extract the maximum billing value
        datapoints = response.get('Datapoints', [])
        if not datapoints:
            print("No billing data available.")
            return

        billing_amount = max(dp['Maximum'] for dp in datapoints)
        print(f"Current Billing Amount: ${billing_amount}")

        # Compare with the threshold
        if billing_amount > THRESHOLD:
            print(f"Billing amount exceeds threshold of ${THRESHOLD}. Sending alert...")
            
            # Publish SNS notification
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="AWS Billing Alert",
                Message=f"Your AWS billing has exceeded ${THRESHOLD}. Current amount: ${billing_amount}"
            )
            print("Alert sent successfully.")
        else:
            print("Billing amount is within threshold.")
    except Exception as e:
        print(f"Error occurred: {e}")
