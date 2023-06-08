from flask import Flask, request, jsonify
import aiohttp
import moment
import asyncio

app = Flask(__name__)

async def get_shipment_date(order_id):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://orderstatusapi-dot-organization-project-311520.uc.r.appspot.com/api/getOrderStatus', json={'orderId': order_id}) as response:
                data = await response.json()
                shipment_date = data['shipmentDate']
                return shipment_date
    except Exception as e:
        print(f"Error occurred while retrieving shipment date: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    return "HELLO FROM THE BACKEND"

@app.route('/', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    intent_name = data['queryResult']['intent']['displayName']

    if intent_name == 'fetchShipmentDate':
        order_id = data['queryResult']['parameters']['order-id']

        async def get_shipment_date_async():
            shipment_date = await get_shipment_date(order_id)
            if shipment_date:
                formattedDate = moment.date(shipment_date).format('dddd, DD MMM YYYY')
                fulfillment_text = f"Your order {order_id} will be shipped on {formattedDate}"
            else:
                fulfillment_text = "Sorry, an error occurred while retrieving the shipment date. Please try again later."
            return fulfillment_text

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        fulfillment_text = loop.run_until_complete(get_shipment_date_async())
        loop.close()

        return jsonify({'fulfillmentText': fulfillment_text})
    
    if intent_name == 'thanks':
        audio_url = 'https://drive.google.com/file/d/1jeymQz0b3493E5ohNJtLKp0D2j4ly_4D/view'
        fulfillment_text = "You're welcome."
        #FULFILLMENT MESSAGES WAS MADE TO PLAY THE AUDIO BUT COULDNT DO THAT DUE TO NO CLOUD STORAGE. THEREFORE JUST RETURNING TEXT.
        fulfillment_messages = [
            {
                'platform': 'TELEPHONY',
                'telephonyPlayAudio': {
                    'audioUri': audio_url
                }
            }
        ]
        return jsonify({'fulfillmentText': fulfillment_text})
    



    
if __name__ == '__main__':
    app.run(port=5000,debug=True)
