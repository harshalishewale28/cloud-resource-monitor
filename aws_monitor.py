
import boto3
from datetime import datetime, timedelta, timezone


# FUNCTION 1: GET EC2 INSTANCES

def get_ec2_instances(region):

    ec2 = boto3.client(
        "ec2",
        region_name=region
    )

    response = ec2.describe_instances()

    instances = []

    for reservation in response["Reservations"]:

        for instance in reservation["Instances"]:

            # Get instance name
            name = "Unnamed Instance"

            for tag in instance.get("Tags", []):

                if tag["Key"] == "Name":
                    name = tag["Value"]

            # Store instance details
            instances.append({

                "Instance ID": instance["InstanceId"],

                "Name": name,

                "Type": instance["InstanceType"],

                "State": instance["State"]["Name"],

                "Public IP": instance.get(
                    "PublicIpAddress",
                    "Not assigned"
                ),

                "Private IP": instance.get(
                    "PrivateIpAddress",
                    "Not assigned"
                )

            })

    return instances


# FUNCTION 2: GET CPU USAGE

def get_cpu_usage(instance_id, region, hours=1):

    cloudwatch = boto3.client(
        "cloudwatch",
        region_name=region
    )

    # Get current time
    end_time = datetime.now(timezone.utc)

    # Calculate starting time
    start_time = end_time - timedelta(
        hours=hours
    )

    # Request CPU metrics from CloudWatch
    response = cloudwatch.get_metric_statistics(

        Namespace="AWS/EC2",

        MetricName="CPUUtilization",

        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instance_id
            }
        ],

        StartTime=start_time,

        EndTime=end_time,

        Period=300,

        Statistics=["Average"]

    )

    # Sort data by time
    points = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"]
    )

    # Return CPU information
    return [

        {
            "Time": point["Timestamp"],

            "CPU": point["Average"]

        }

        for point in points

    ]
