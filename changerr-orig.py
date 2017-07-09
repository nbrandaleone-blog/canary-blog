from __future__ import print_function
import boto3

client = boto3.client('route53')

#blue_weight = 60
#green_weight = 100 - blue_weight

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
    print(event)
    resp = change_weights(50,50)
    print(resp)
    #change_weights(event.weight, 100-event.weight)
    return { resp }

#response = client.get_hosted_zone(
#        Id='ZTXBD7RUFCM9H'
#        )
#
#print (response['HostedZone']['Name'])
