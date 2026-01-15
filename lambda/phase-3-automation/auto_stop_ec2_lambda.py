Phase 3 – Automated EC2 Auto-Stop for Cost Optimization

This Lambda function automatically stops running EC2 instances
on a scheduled basis using Amazon EventBridge.

Services Used:
- AWS Lambda
- Amazon EC2
- Amazon EventBridge
- Amazon SNS

import boto3
import os

# AWS clients
ec2 = boto3.client("ec2")
sns = boto3.client("sns")

# Environment variable
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")


def get_running_instances():
    
    Retrieve all running EC2 instances.
    
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["running"]
            }
        ]
    )

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance["InstanceId"])

    return instances


def stop_instances(instance_ids):
    
    Stop EC2 instances safely.
    
    if not instance_ids:
        return []

    ec2.stop_instances(InstanceIds=instance_ids)
    return instance_ids


def send_notification(stopped_instances):
    
    Send SNS notification with stopped instances.
    
    if not stopped_instances:
        message = "No running EC2 instances found. Nothing to stop."
    else:
        message = "The following EC2 instances were automatically stopped:\n\n"
        for instance_id in stopped_instances:
            message += f"- {instance_id}\n"

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="EC2 Auto-Stop Execution Report",
        Message=message
    )


def lambda_handler(event, context):
    
    Lambda entry point.
    
    running_instances = get_running_instances()
    stopped_instances = stop_instances(running_instances)
    send_notification(stopped_instances)

    return {
        "status": "completed",
        "instances_stopped": stopped_instances
    }
