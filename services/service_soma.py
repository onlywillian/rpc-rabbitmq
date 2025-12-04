from common.rpc_utils import create_channel
import json
import pika

connection, channel = create_channel()

SERVICE_QUEUE = "service_soma"

channel.queue_declare(queue=SERVICE_QUEUE)

def process_request(data):
    print("Requisição recebida")
    a = data.get("a", 0)
    b = data.get("b", 0)
    return {"resultado": a + b}

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

print(" [x] Serviço SOMA esperando requisições...")
channel.start_consuming()
