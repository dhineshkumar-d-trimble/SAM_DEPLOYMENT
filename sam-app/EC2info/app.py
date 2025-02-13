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
        response = ec2.describe_instances()

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
                all_instances.append(instance_info)

                if instance_info['State'] == 'running':
                    running_instances.append(instance_info)
                elif instance_info['State'] == 'stopped':
                    stopped_instances.append(instance_info)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'AllInstances': all_instances,
            'RunningInstances': running_instances,
            'StoppedInstances': stopped_instances
        })
    }
