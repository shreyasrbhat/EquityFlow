from confluent_kafka import Consumer
from confluent_kafka import Producer
from time import strftime, localtime
#from consumer_config.config import consumer_config
import sys
import json

consumer_config = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'msft_stock3',
    'auto.offset.reset': 'earliest'
}

producer_config = {
    'bootstrap.servers': 'localhost:29092',
    'client.id': 'market_data_producer',
    'acks': '0'
}

topic = 'postgres.public.market'
consumer = Consumer(consumer_config)
consumer.subscribe([topic])

producer = Producer(producer_config)



import json

def extract_close_price(kafka_data):
    """
    Extracts the close price from a Kafka consumer input.

    :param kafka_data: Kafka consumer data as a byte string.
    :return: The extracted close price or None if the price cannot be extracted.
    """
    try:
        # Decode the byte string
        decoded_input = kafka_data.decode('utf-8')

        # Parse the JSON string
        parsed_json = json.loads(decoded_input)

        close_price = parsed_json.get('after', {}).get('close')
        timestamp = parsed_json.get('after', {}).get('timestamp')
        symbol = parsed_json.get('after', {}).get('symbol')

        return symbol , {'timestamp': timestamp, 'close': close_price}

        # Extract and return the 'close' price
        #return parsed_json.get('after', {}).get('close')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def acked(err, msg):
    """Delivery report handler called on successful or failed delivery of message"""
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message produced: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")



if __name__ == '__main__':
    count = 1
    avg = 0
    while True:
        try:
            event = consumer.poll(1.0)
            if event is None:
                continue
            close_price_info = extract_close_price(event.value())
            if close_price_info is None:
                continue
            close_price = close_price_info[1]['close']
            timestamp = close_price_info[1]['timestamp']
            timestamp_str = strftime("%Y-%m-%d %H:%M:%S", localtime(timestamp))
            symbol = close_price_info[0]
            print(f"closing price: {close_price}, timestamp: {timestamp_str}")
            count += 1

            stock_info = json.dumps({'close': close_price, 'timestamp': timestamp})
            producer.produce('stock_price', key=symbol, value=stock_info, callback=acked)

        except KeyboardInterrupt:
                break

