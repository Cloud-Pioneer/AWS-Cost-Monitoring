Phase 2 – AWS Cost Breakdown & Reporting

This Lambda function retrieves AWS cost data grouped by service
using AWS Cost Explorer and sends a summarized cost report via SNS.

Services Used:
- AWS Cost Explorer
- AWS Lambda
- SNS (Email Notifications)

import boto3
import datetime
import os

# Initialize AWS clients
ce = boto3.client("ce")
sns = boto3.client("sns")

# Environment variables
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")


def get_cost_breakdown():
    
    Fetch AWS cost grouped by service for the last 7 days.
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d")
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "DIMENSION",
                "Key": "SERVICE"
            }
        ]
    )

    services = response["ResultsByTime"][0]["Groups"]

    cost_data = []
    for service in services:
        service_name = service["Keys"][0]
        amount = float(service["Metrics"]["UnblendedCost"]["Amount"])
        cost_data.append((service_name, amount))

    return sorted(cost_data, key=lambda x: x[1], reverse=True)


def send_cost_report(cost_data):
  
    Send summarized cost breakdown report via SNS.
    
    message = "AWS Cost Breakdown Report (Last 7 Days)\n\n"

    for service, amount in cost_data:
        message += f"{service}: ${amount:.2f}\n"

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="AWS Cost Breakdown Report",
        Message=message
    )


def lambda_handler(event, context):
    """
    Lambda entry point.
    """
    cost_data = get_cost_breakdown()
    send_cost_report(cost_data)

    return {
        "status": "report_sent",
        "services_reported": len(cost_data)
    }
