import json
import dateutil.parser
import logging
import boto3
import uuid


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dyn_client = boto3.client('dynamodb')
TABLE_NAME = "HotelBookings"

def safe_int(n):
    
    if n is not None:
        return int(n)
    return n
    
def try_ex(func):
    try:
        return func()
    except KeyError:
        return None
        
def elicit_slot(session_attributes, intent_name, slots, slots_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction' : {
            'type': 'ElicitSlot',
            'intentName':intent_name,
            'slots': slots,
            'slotToElicit': slots_elicit,
            'message': message
        }
    }
    


def confirm_intent (session_attributes, intent_name, slots, message): 
    return {
        'sessionAttributes': session_attributes, 
        'dialogAction': {
            'type': 'ConfirmIntent', 
            'intentName': intent_name, 
            'slots': slots,
            'message': message
        }
    }

def close (session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes, 
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
def delegate (session_attributes, slots):
    return {
        'sessionAttributes': session_attributes, 
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
    
def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot' : violated_slot,
        'message': {'contentType' : 'PlainText', 'content': message_content}
    }



#Returns if all the slots are validated and have inputs 
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

#This function is called 4 times
def lambda_handler(event, context):
    
#Come back
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print(event['invocationSource'])
    print(slots)
    print(intent)
    
    #returns a dic which contain the isValid key and maybe violated Slot
    validation_result = validate(slots)
    print(validation_result)
	#The bot needs to ask for more slots 
    if event['invocationSource'] == 'DialogCodeHook':
        #Missing Slot Value
        if not validation_result['isValid']:
	#response is a dictionary and has 2 keys, sessionState and intent 
            response = {
                "sessionState": {
                    "dialogAction": {
                        #slottoElicit meaning the slot that needs to asked from the user 
                        'slotToElicit': validation_result['violatedSlot'],
		#chatbot is asking for data from the user 
                        "type":"ElicitSlot"
                    },
                    "intent": {
		#name of the intent which is being executed rn 
                        'name': intent,
		#all slots values 
                        'slots' : slots
                    }
                }
            }
       #When all userinput is valid 
        else:
            response = {
            "sessionState": {
                "dialogAction": {
	#The data provided by the user will be used to complete the intent 
                    "type": "Delegate"
                },
                "intent": {
		#name of the intent which is being executed rn 
                    'Name':intent,
		#all slots values 
                    'slots': slots
                        
                    }
            
             }
            }
        
    #All slots are filled 
    if event['invocationSource'] == 'FulfillmentCodeHook':
        
        # Add order in Database
        
        print("Hello")
        
        response = {
        "sessionState": {
            "dialogAction": {
	#convo is finished
                "type": "Close"
            },
            "intent": {
                'name':intent,
                'slots': slots,
	#The intent was fully processed and all slots were validated 
                'state':'Fulfilled'
                
                }
    
        },
#Other texts could be used 
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Thanks, I have placed your reservation"
            }
        ]
    }

    return response
