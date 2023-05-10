import json
import dateutil.parser
import logging
import boto3
import uuid


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dyn_client = boto3.client('dynamodb')
TABLE_NAME = "HotelBookings"

def validate(slots):

    valid_cities = ['Toronto','Ottawa','Montreal','Calgary']

   #If the location key isn’t present (not set yet), return false 
#will also tell the slot which violated the dictionary 
    if not slots['Location']:
        print("Inside Empty Location")
        return {
        'isValid': False,
        'violatedSlot': 'Location'
        }        
        
      #If the location key isn’t present (not set yet), return false 
#will also tell the slot which violated the dictionary 
    if not slots['CheckInDate']:
        return {
        'isValid': False,
        'violatedSlot': 'CheckInDate'
    }
     #If the location key isn’t present (not set yet), return false 
#will also tell the slot which violated the dictionary       
    if not slots['Nights']:
        return {
        'isValid': False,
        'violatedSlot': 'Nights'
    }
           #If the location key isn’t present (not set yet), return false 
#will also tell the slot which violated the dictionary 
    if not slots['RoomType']:
        return {
        'isValid': False,
        'violatedSlot': 'RoomType'
    }

    return {'isValid': True}


def lambda_handler(event, context):

    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print("Start")

    validation_result = validate(slots)

    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit': validation_result['violatedSlot'],
                        "type":"ElicitSlot"
                    },
                    "intent": {
                        'name': intent,
                        'slots' : slots
                    }
                }
            }
        else:
            response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    'name':intent,
                    'slots': slots
                    }
            
             }
            }
        
    if event['invocationSource'] == 'FulfillmentCodeHook':
        
        # Add order in Database
        id = str(uuid.uuid4())
        location = str(slots['Location']['value'])
        checkInDate = str(slots['CheckInDate']['value'])
        nights = str(slots['Nights']['value'])
        roomType = str(slots['RoomType']['value'])

        print(type(location))
        print(type(checkInDate))
        print(type(nights))
        print(type(roomType))


        try:
            response = dyn_client.put_item(
                TableName=TABLE_NAME,
                Item={
                    'id': {'S': id},
                    'Location': {'S': location},
                    'CheckinDate': {'S': checkInDate},
                    'Nights': {'S': nights},
                    'RoomType': {'S': roomType},

                }
            )
        except Exception as e:
            logger.error("Error occurred while adding order to DynamoDB: {}".format(str(e)))
            raise e

        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    'name': intent,
                    'slots': slots,
                    'state':'Fulfilled'
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Thanks, I have placed your reservation"
                }
            ]
        }


    return response
