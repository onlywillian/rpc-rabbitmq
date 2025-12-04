RPC com RabbitMQ – Sistema de Processamento Assíncrono

Este projeto demonstra um sistema completo de comunicação assíncrona, utilizando RabbitMQ para implementar um mecanismo de RPC (Remote Procedure Call) entre um cliente e um serviço de processamento.

Estrutura do Projeto

├── client/  
│ └── rpc_client.py  
├── common/  
│ └── rpc_utils.py  
├── services/  
│ └── service_soma.py  
│ └── service_media.py  
│ └── service_busca.py  
├── server_dispatcher  
└── README.md

### Dependências Necessárias

Requisitos:

- Python 3.10+
- RabbitMQ (local ou Docker)
- Pip / venv

### Instalação das dependências Python

```
python3 -m venv .venv
.venv/Scripts/activate
pip install pika
```

### Como Executar o Projeto

Subir o RabbitMQ com Docker

```
# latest RabbitMQ 4.x
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management
```

Iniciar o(s) serviço(s)

```
python -m services.service_soma.py
python -m services.service_media.py
python -m services.service_busca.py
```

O serviço ficará aguardando requisições:

```
[x] Serviço SOMA esperando requisições...
```

Rodar o servidor (SERVER)

```
python -m .\server_dispatcher.py
```

Rodar o cliente (CLIENT)

```
python client/rpc_client.py
```

Exemplo de saída:

```
Escolha o serviço:
1 - Soma
2 - Média
3 - Busca
Opção: 1
A: 10
B: 20
{'resultado': 30}
```

### Fluxo Esperado de Funcionamento

1. O cliente cria uma fila exclusiva para receber respostas.
2. O cliente envia uma requisição para a fila rpc_soma, incluindo:

   - reply_to: fila para a resposta
   - correlation_id: identificador único

3. O serviço consome a mensagem, processa o cálculo e envia o resultado ao reply_to.
4. O cliente aguarda até receber uma resposta com o mesmo correlation_id.
5. O resultado é exibido ao usuário.

Esse fluxo implementa um RPC real sobre mensageria AMQP.
