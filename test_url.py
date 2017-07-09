import requests
from time import sleep

# Variables
iterations = 10
delay = 1

# Lambda function
def handler(event, context):
    print('event target is', event['target'])
    boolean = True
    for i in range(iterations):
        r = requests.get(event['target'])
        if r.status_code != requests.codes.ok:
            boolean = False
        sleep(delay)
    print(boolean)
    return boolean

if __name__ == "__main__":
    print('In main()')
    handler({ 'target' : 'http://www.google.com' }, None)

# "{} and {}".format("string", 1)
