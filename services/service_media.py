from common.rpc_utils import create_channel
import json
import pika

connection, channel = create_channel()

SERVICE_QUEUE = "service_media"

channel.queue_declare(queue=SERVICE_QUEUE)

def process_request(data):
    print("Requisição recebida")
    valores = data.get("valores", [])
    if not valores:
        return {"resultado": 0}
    return {"resultado": sum(valores) / len(valores)}

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

print(" [x] Serviço MÉDIA esperando requisições...")
channel.start_consuming()
