from __future__ import print_function
import boto3

client = boto3.client('route53')

def change_weights(blue_weight, green_weight): 
    response = client.change_resource_record_sets(
            HostedZoneId='ZTXBD7RUFCM9H',
            ChangeBatch={
                'Comment': 'alter Route53 records sets for canary blue-green deployment',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': 'myservice.nickaws.net.',
                            'Type': 'A',
                            'SetIdentifier': 'blue',
                            'Weight': blue_weight,
                            'AliasTarget': {
                                'HostedZoneId': 'Z35SXDOTRQ7X7K',
                                'DNSName': 'ecsalb-802606693.us-east-1.elb.amazonaws.com.',
                                'EvaluateTargetHealth': False
                                }
                            }
                        },
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': 'myservice.nickaws.net.',
                            'Type': 'A',
                            'SetIdentifier': 'green',
                            'Weight': green_weight,
                            'AliasTarget': {
                                'HostedZoneId': 'Z35SXDOTRQ7X7K',
                                'DNSName': 'ecsalbgreen-66710691.us-east-1.elb.amazonaws.com.',
                                'EvaluateTargetHealth': False
                                }
                            }
                        },
                    ]
                }
            )
    return response

def handler(event, context):
    resp = change_weights(event['weight'], 100-event['weight'])
    return { "message": "Success!" }
#print (response['HostedZone']['Name'])
