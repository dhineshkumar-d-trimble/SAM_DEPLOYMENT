import json
import boto3

def lambda_handler(event, context):
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
        'statusCode': 200,
        'body': json.dumps({
            'AllInstances': all_instances,
            'RunningInstances': running_instances,
            'StoppedInstances': stopped_instances
        })
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
