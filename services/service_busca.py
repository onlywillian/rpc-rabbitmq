from common.rpc_utils import create_channel
import json
import pika

connection, channel = create_channel()

SERVICE_QUEUE = "service_busca"

channel.queue_declare(queue=SERVICE_QUEUE)

MOCK_DB = ["banana", "laranja", "uva", "abacaxi", "morango"]

def process_request(data):
    termo = data.get("termo", "")
    resultados = [item for item in MOCK_DB if termo.lower() in item.lower()]
    return {"resultado": resultados}

def on_request(ch, method, props, body):
    data = json.loads(body.decode())
    response = process_request(data)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=SERVICE_QUEUE, on_message_callback=on_request)

print(" [x] Serviço BUSCA esperando requisições...")
channel.start_consuming()
