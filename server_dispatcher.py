from common.rpc_utils import create_channel
import pika, json, uuid

connection, channel = create_channel()

DISPATCHER_QUEUE = "rpc_dispatcher"

SERVICES = {
    "soma": "service_soma",
    "media": "service_media",
    "busca": "service_busca"
}

channel.queue_declare(queue=DISPATCHER_QUEUE)

def on_request(ch, method, props, body):
    msg = json.loads(body.decode())

    service = msg.get("service")
    payload = msg.get("payload", {})

    if service not in SERVICES:
        response = {"erro": "Serviço inválido"}
    else:
        service_queue = SERVICES[service]

        result = forward_to_service(service_queue, payload)

        response = result

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=json.dumps(response)
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)

def forward_to_service(queue, payload):
    service_conn = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    service_ch = service_conn.channel()

    callback_queue = service_ch.queue_declare(queue='', exclusive=True).method.queue
    corr_id = str(uuid.uuid4())

    service_ch.basic_publish( # Implementação de comunicação assíncrona
        exchange='',
        routing_key=queue,
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body=json.dumps(payload)
    )

    response = None

    def callback(ch, method, props, body):
        nonlocal response
        if props.correlation_id == corr_id:
            response = json.loads(body)
            ch.stop_consuming()

    service_ch.basic_consume(
        queue=callback_queue,
        on_message_callback=callback,
        auto_ack=True
    )

    service_ch.start_consuming()
    service_conn.close()

    return response

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=DISPATCHER_QUEUE, on_message_callback=on_request)

print(" [x] Servidor DISPATCHER aguardando requisições...")
channel.start_consuming()
