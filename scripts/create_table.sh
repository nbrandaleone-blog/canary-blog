#!/bin/bash

aws dynamodb create-table \
--table-name CanaryTable \
--attribute-definitions AttributeName=NewContainerName,AttributeType=S \
--key-schema AttributeName=NewContainerName,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

sleep 10 

aws dynamodb put-item --table-name CanaryTable \
--item '{
	"NewContainerName":{"S":"green-app"},
	"NewLB":{"S":"dummy"},
	"OldLB":{"S":"dummy"},
	"Triggered":{"BOOL":false},
	"HostedZoneID":{"S":"dummy"},
	"RecordName":{"S":"dummy"},
	"LBZoneID":{"S":"dummy"} }' \
--return-consumed-capacity TOTAL

# aws dynamodb delete-table --table-name CanaryTable
