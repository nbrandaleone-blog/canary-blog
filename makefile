# build a python script, which is uploaded into AWS as a lambda function
#

# makefiles need <tab> to indicate commands.
# Use this command to verify <tabs>: cat -e -t -v makefile
#

# typing 'make' will invoke the first target entry in the file 
# (in this case the default target entry)
# you can name this target entry anything, but "default" or "all"
# are the most commonly used names by convention
#
SOURCE = test_url.py
BASE = $(patsubst %.py,%, $(SOURCE))
TARGET = testURL.zip
LAMBDA = testWebSite
DIR = ${VIRTUAL_ENV}
LIBS = ${DIR}/lib/python3.6/site-packages

default: ${TARGET}
	@echo Executable plus libraries have been zipped up
	@echo Type make deploy to push to AWS as lambda function

# To create the executable file we need to library files
#
testURL.zip:
	(cd ${LIBS} && zip -r9 ${DIR}/${TARGET} *)
	zip -g ${TARGET} ${SOURCE}

# Push the zipped file to AWS
# 
deploy:
	aws lambda create-function \
	--function-name ${LAMBDA} \
	--zip-file fileb://${TARGET} \
	--role arn:aws:iam::991225764181:role/lambda_exec_role \
	--handler ${BASE}.handler \
	--runtime python3.6 \
	--timeout 15 \
	--memory-size 128
# Optional --timeout <in-seconds>
# Optional aws lambda update-function-configuration

# Delete the deployed lambda function
#
delete:
	aws lambda delete-function --function-name ${LAMBDA} \
	--region us-east-1

# Invoke the lambda function on the AWS platform, and receive the results
#
invoke:
	aws lambda invoke \
	--invocation-type RequestResponse \
	--function-name ${LAMBDA} \
	--region us-east-1 \
	--log-type Tail \
	--payload '{"target":"https://www.cisco.com"}' \
	outputfile.txt | base64 -D

#	--invocation-type Event \
#	--payload file://file-path/inputfile.txt \
#	--profile adminuser \
#
# In order to read the outputfile, which is base64 encoded, do the following:
# echo <base64-encoded-file> | base64 -D
#

# Delete the zip file
# 
clean:
	$(RM) ${TARGET} outputfile.txt

