from datetime import datetime
import boto3
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
table = dynamodb.Table('users2')

def get_all_missed_person():
    data = table.scan()
    item = json.dumps(data['Items'], indent=4, cls=DecimalEncoder)
    return item

def get_missed_person(id, type):
    response = table.get_item(
        Key={
            'id': id,
            'type': type
        }
    )

    item = json.dumps(response['Item'], indent=4, cls=DecimalEncoder)
    return item

def save_missed_person(body):
    # create a id to get the person
    aux_date = datetime.now()
    date = str(aux_date).replace('-', '').replace(':', '').replace('.', '').replace(' ', '')
    id = body['name'][0].upper() + body['name'][1].upper() + date
    body.update({'id' : id})
    body.update({'type' : 'missed'})
    body.update({'date' : str(aux_date)})

    return table.put_item( Item={**body} )