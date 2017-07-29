#!/bin/bash

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

aws dynamodb put-item --table-name CanaryTable \
--item '{
	"NewContainerName":{"S":"new-container-service"},
	"NewLB":{"S":"dummy"},
	"OldLB":{"S":"dummy"},
	"Triggered":{"BOOL":false},
	"HostedZoneID":{"S":"dummy"},
	"RecordName":{"S":"dummy"},
	"LBZoneID":{"S":"dummy"} }' \
--return-consumed-capacity TOTAL

# aws dynamodb delete-table --table-name CanaryTable
