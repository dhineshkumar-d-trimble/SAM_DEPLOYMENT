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
        response = ec2.describe_instances()
        instances = extract_instance_details(response)
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_running_instances():
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instances = extract_instance_details(response)
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_stopped_instances():
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        instances = extract_instance_details(response)
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def extract_instance_details(response):
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_details = {
                'InstanceId': instance.get('InstanceId'),
                'InstanceName': get_instance_name(instance),
                'AmiId': instance.get('ImageId'),
                'Region': instance.get('Placement', {}).get('AvailabilityZone')[:-1],
                'AvailabilityZone': instance.get('Placement', {}).get('AvailabilityZone'),
                'VpcId': instance.get('VpcId'),
                'SubnetId': instance.get('SubnetId')
            }
            instances.append(instance_details)
    return instances

def get_instance_name(instance):
    for tag in instance.get('Tags', []):
        if tag['Key'] == 'Name':
            return tag['Value']
    return None

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
