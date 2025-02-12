import json
import boto3

# Initialize the EC2 client
ec2 = boto3.client('ec2', region_name='ap-south-1')

# Define the paths for the endpoints
list_instances_path = '/list-instances'
running_instances_path = '/running-instances'
stopped_instances_path = '/stopped-instances'

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
        instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_running_instances():
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def list_stopped_instances():
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
        return build_response(200, instances)
    except Exception as e:
        print('Error:', e)
        return build_response(400, str(e))

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }
