import json
import dateutil.parser
import logging
import boto3
import uuid

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dyn_client = boto3.client('dynamodb')
TABLE_NAME = "SoaringArtistArtCommissions"

def validate(slots):
        

    if not slots['TypeOfOrder']:
        return {
        'isValid': False,
        'violatedSlot': 'TypeOfOrder'
    }

    if not slots['Budget']:
        return {
        'isValid': False,
        'violatedSlot': 'Budget'
    }

    if not slots['Timeline']:
        return {
        'isValid': False,
        'violatedSlot': 'Timeline'
    }
    
    if not slots['ColourSchemes']:
        
        return {
        'isValid': False,
        'violatedSlot': 'ColourSchemes'
    }
    
    if not slots['Purpose']:
        return {
        'isValid': False,
        'violatedSlot': 'Purpose'
    }
    
    if not slots['Email']:
        return {
        'isValid': False,
        'violatedSlot': 'Email'
    }

    if not slots['PhoneNumber']:
        return {
        'isValid': False,
        'violatedSlot': 'PhoneNumber'
    }
    
    if not slots['PointOfContact']:
        return {
        'isValid': False,
        'violatedSlot': 'PointOfContact'
    }
    
    if not slots['Name']:
        return {
        'isValid': False,
        'violatedSlot': 'Name'
    }
    
    return {'isValid': True}

def lambda_handler(event,context):
    
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

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
            

    elif event['invocationSource'] == 'FulfillmentCodeHook':
        
         # Add order in Database
        id = str(uuid.uuid4())
        typeOfOrder = str(slots['TypeOfOrder']['value']['interpretedValue'])
        budget = str(slots['Budget']['value']['interpretedValue'])
        timeline = str(slots['Timeline']['value']['interpretedValue'])

        colourSchemes = str(slots['ColourSchemes']['value']['interpretedValue'])
        purpose = str(slots['Purpose']['value']['interpretedValue'])
        email = str(slots['Email']['value']['interpretedValue'])
        phoneNumber = str(slots['PhoneNumber']['value']['interpretedValue'])

        pointOfContact = str(slots['PointOfContact']['value']['interpretedValue'])
        name = str(slots['Name']['value']['interpretedValue'])

        try:
            response = dyn_client.put_item(
                TableName=TABLE_NAME,
                Item={
                    'id': {'S': id},
                    'TypeOfOrder': {'S': typeOfOrder},
                    'Budget': {'S': budget},
                    'Timeline': {'S': timeline},

                    'ColourScheme': {'S': colourSchemes},
                    'Purpose': {'S': purpose},
                    'Email': {'S': email},
                    'PhoneNumber': {'S': phoneNumber},

                    'PointOfContact': {'S': pointOfContact},
                    'Name': {'S': name},              
                    

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
                    "content": "Thanks, I have placed your order, I will get in-contact with you for more information"
                }
            ]
        }
        
    else:
        print("In")
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
                    "content": "Sorry, I didn't understand what you said. Can you please rephrase your question?"
                }
            ]
        }
        
    return response


    
