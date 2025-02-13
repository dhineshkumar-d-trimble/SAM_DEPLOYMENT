import json
import boto3
from datetime import datetime

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Define the paths for the endpoints
list_instances_path = '/list-instances/info'
running_instances_path = '/running-instances/info'
stopped_instances_path = '/stopped-instances/info'

def lambda_handler(event, context):
    print('Request event: ', event)
    response = None

    try:
        http_method = event.get('httpMethod')
        path = event.get('path')

        if http_method == 'GET' and path == list_instances_path:
            response = list_instances()
        elif http_method == 'GET' and path == running_instances_path:
            response = list_running_instances()
        elif http_method == 'GET' and path == stopped_instances_path:
            response = list_stopped_instances()
        else:
            response = build_response(404, '404 Not Found')

    except Exception as e:
        print('Error:', e)
        response = build_response(400, 'Error processing request')

    return response

def list_instances():
    try:
        instances_info = get_instances_info()
        return build_response(200, instances_info['AllInstances'])
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_running_instances():
    try:
        instances_info = get_instances_info()
        return build_response(200, instances_info['RunningInstances'])
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_stopped_instances():
    try:
        instances_info = get_instances_info()
        return build_response(200, instances_info['StoppedInstances'])
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def get_instances_info():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    all_instances = []
    running_instances = []
    stopped_instances = []

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)

        # Get all instances
        response_all = ec2.describe_instances()
        all_instances.extend(parse_instances(response_all, region))

        # Get running instances
        response_running = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        running_instances.extend(parse_instances(response_running, region))

        # Get stopped instances
        response_stopped = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        stopped_instances.extend(parse_instances(response_stopped, region))

    return {
        'AllInstances': all_instances,
        'RunningInstances': running_instances,
        'StoppedInstances': stopped_instances
    }

def parse_instances(response, region):
    instances_info = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_info = {
                'InstanceId': instance.get('InstanceId'),
                'InstanceName': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                'AmiId': instance.get('ImageId'),
                'Region': region,
                'AvailabilityZone': instance.get('Placement', {}).get('AvailabilityZone'),
                'VpcId': instance.get('VpcId'),
                'SubnetId': instance.get('SubnetId'),
                'IpAddressRange': instance.get('PrivateIpAddress'),
                'State': instance.get('State', {}).get('Name')
            }
            instances_info.append(instance_info)
    return instances_info

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=CustomEncoder)
    }
