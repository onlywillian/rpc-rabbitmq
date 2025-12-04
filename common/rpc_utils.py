import pika

def create_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )

def create_channel():
    connection = create_connection()
    return connection, connection.channel()
