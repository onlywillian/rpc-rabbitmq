import pika, uuid, json

class RPCClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if props.correlation_id == self.corr_id:
            self.response = json.loads(body)

    def call(self, service, payload):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key="rpc_dispatcher",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=json.dumps({
                "service": service,
                "payload": payload
            })
        )

        while self.response is None:
            self.connection.process_data_events()

        return self.response

if __name__ == "__main__":
    rpc = RPCClient()

    print("Escolha o serviço:")
    print("1 - Soma")
    print("2 - Média")
    print("3 - Busca")
    op = input("Opção: ")

    if op == "1":
        a = int(input("A: "))
        b = int(input("B: "))
        print(rpc.call("soma", {"a": a, "b": b}))

    elif op == "2":
        valores = list(map(int, input("Valores separados por espaço: ").split()))
        print(rpc.call("media", {"valores": valores}))

    elif op == "3":
        termo = input("Buscar por: ")
        print(rpc.call("busca", {"termo": termo}))
