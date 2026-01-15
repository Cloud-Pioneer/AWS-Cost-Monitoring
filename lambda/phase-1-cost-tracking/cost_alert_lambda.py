Phase 1 – AWS Cost Tracking & Alerts

This Lambda function monitors AWS estimated charges using
CloudWatch billing metrics and sends SNS alerts when
cost thresholds are exceeded.

Services Used:
- CloudWatch (Billing Metrics)
- AWS Lambda
- SNS (Email Notifications)

import boto3
import datetime
import os

# Initialize AWS clients
cloudwatch = boto3.client("cloudwatch")
sns = boto3.client("sns")

# Environment variables 
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
COST_THRESHOLD_USD = float(os.environ.get("COST_THRESHOLD_USD", 5.0))


def get_estimated_charges():
    """
    Fetch estimated AWS charges from CloudWatch billing metrics.
    """
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/Billing",
        MetricName="EstimatedCharges",
        Dimensions=[
            {
                "Name": "Currency",
                "Value": "USD"
            }
        ],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=24),
        EndTime=datetime.datetime.utcnow(),
        Period=21600,
        Statistics=["Maximum"]
    )

    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0

    return max(dp["Maximum"] for dp in datapoints)


def send_sns_alert(cost):
    """
    Send SNS email alert when cost threshold is exceeded.
    """
    message = f"""
AWS Cost Alert 

Estimated AWS charges have exceeded the defined threshold.

Current Estimated Cost: ${cost:.2f}
Threshold: ${COST_THRESHOLD_USD:.2f}

Please review your AWS resources.
"""

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="AWS Cost Alert",
        Message=message
    )


def lambda_handler(event, context):
    """
    Lambda entry point.
    """
    estimated_cost = get_estimated_charges()

    if estimated_cost >= COST_THRESHOLD_USD:
        send_sns_alert(estimated_cost)
        return {
            "status": "alert_sent",
            "estimated_cost": estimated_cost
        }

    return {
        "status": "within_budget",
        "estimated_cost": estimated_cost
    }
