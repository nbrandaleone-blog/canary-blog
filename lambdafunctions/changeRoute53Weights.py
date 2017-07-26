from __future__ import print_function

import boto3
import json
import os

client = boto3.client('route53')

HostedZoneID = os.environ['HostedZoneID']
LBZoneID = os.environ['LBZoneID']
ServiceName = os.environ['Service']
fromDNS = os.environ['BlueLoadBalancer']
toDNS = os.environ['GreenLoadBalancer']

def change_weights(blue_weight, green_weight): 
    global HostedZoneID, LBZoneID, ServiceName, fromDNS, toDNS
    
    response = client.change_resource_record_sets(
  
            HostedZoneId = HostedZoneID,
            ChangeBatch={
                'Comment': 'alter Route53 records sets for canary blue-green deployment',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': ServiceName,
                            'Type': 'A',
                            'SetIdentifier': 'blue',
                            'Weight': blue_weight,
                            'AliasTarget': {
                                'HostedZoneId': LBZoneID,
                                'DNSName': fromDNS,
                                'EvaluateTargetHealth': False
                                }
                            }
                        },
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': ServiceName,
                            'Type': 'A',
                            'SetIdentifier': 'green',
                            'Weight': green_weight,
                            'AliasTarget': {
                                'HostedZoneId': LBZoneID, 
                                'DNSName': toDNS,
                                'EvaluateTargetHealth': False
                                }
                            }
                        },
                    ]
                }
            )
    return response

def lambda_handler(event, context):
    print(event)
    resp = change_weights(event['weight'], 100-event['weight'])
    #resp = change_weights(50,50)
    print(resp)
    return {"message": "Success"}

#response = client.get_hosted_zone(
#        Id='ZTXBD7RUFCM9H'
#        )
#
#print (response['HostedZone']['Name'])
