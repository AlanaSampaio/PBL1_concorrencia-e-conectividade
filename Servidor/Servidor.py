import socket  # Utilizado para criar e gerenciar conexões de rede
import json  # Utilizado para codificar e decodificar dados em formato JSON
import re  # Utilizado para trabalhar com expressões regulares
import threading  # Utilizado para gerenciar múltiplas threads (conexões simultâneas)
import logging  # Utilizado para manter um registro (log) de eventos e mensagens

# Configura o logger para exibir mensagens de nível INFO ou superior
logging.basicConfig(level=logging.INFO)

# Define constantes numéricas para representar códigos de status HTTP
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405

# Define o endereço IP e a porta onde o servidor será executado no google cloud
#HOST, PORT = '0.0.0.0', 3389

#Define endereço IP e porta onde o servidor será executado quando executado no localhost
HOST, PORT = '192.168.0.105', 28600

# Declara a classe SimpleHTTPServer
class SimpleHTTPServer:
    def __init__(self):
        # Inicializa uma variável de instância para armazenar dados
        # Neste exemplo, 'caixa' contém uma lista de dicionários com 'id' e 'status'
        self.data_store = {
            'caixa': [{'id': 123, 'status': True}],
            'compras': [{'nome': 'Arroz', 'preco': 20.0, 'quantidade': 1}]  # Lista vazia para armazenar informações sobre compras
        }

    def handle_single_connection(self, conn, addr):
        # Esta função trata de uma única conexão de cliente
        # 'conn' é o soquete conectado ao clientebody
        # 'addr' é o endereço do cliente
        
        # Recebe até 1024 bytes do cliente e decodifica para texto
        data = conn.recv(1100).decode('utf-8', errors='ignore')
        
        # Se algum dado foi recebido
        if data:
            # Processa a requisição e obtém o código de status HTTP e a resposta
            status_code, response = self.handle_request(data)
            
            # Envia a resposta ao cliente
            conn.sendall(f"HTTP/1.1 {status_code} OK\r\nContent-Type: application/json\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode('utf-8'))

        # Fecha a conexão com o cliente
        conn.close()

    def handle_request(self, data):
        # Divide a requisição HTTP em várias linhas
        headers = data.split('\r\n')
        
        # A primeira linha da requisição contém o método e o caminho
        request_line = headers[0].split()
        method, path = request_line[0], request_line[1]
        
        # Direciona a requisição para o método correspondente com base no método HTTP
        if method == 'GET':
            return self.handle_get_request(path)
        elif method == 'POST':
            return self.handle_post_request(data, path)
        elif method == 'PUT':
            return self.handle_put_request(data, path)
        else:
            # Se o método HTTP não for GET, POST ou PUT, retorna um erro 405
            return HTTP_METHOD_NOT_ALLOWED, "Método não permitido"
    def handle_get_request(self, path):
        # Trata requisições HTTP GET baseadas no caminho especificado (path)
        
        # Verifica se o caminho é "/caixa" para retornar todos os caixas
        if path == '/caixa':
            return HTTP_OK, json.dumps(self.data_store['caixa'])  # Retorna um 200 OK e o conteúdo dos caixas em formato JSON

        # Verifica se o caminho começa com "/caixa/" para buscar um caixa específico
        elif path.startswith('/caixa/'):
            caixa_id = int(path.split('/')[-1])  # Extrai o ID do caixa da URL
            # Encontra o caixa pelo ID
            caixa = next((item for item in self.data_store['caixa'] if item['id'] == caixa_id), None)
            if caixa:  # Se o caixa foi encontrado, retorna um 200 OK e o caixa em formato JSON
                return HTTP_OK, json.dumps(caixa)
            else:  # Se o caixa não foi encontrado, retorna um 404 Not Found
                return HTTP_NOT_FOUND, "Caixa não encontrado"

        # Verifica se o caminho é "/compras" para retornar todas as compras
        elif path == '/compras':
            return HTTP_OK, json.dumps(self.data_store['compras'])  # Retorna um 200 OK e o conteúdo das compras em formato JSON

        else:  # Se o caminho não corresponde a nenhum dos anteriores, retorna um 404 Not Found
            return HTTP_NOT_FOUND, "Não encontrado"
    def handle_post_request(self, data, path):
        # Manipula requisições HTTP POST
        content_length = int(re.search(r'Content-Length: (\d+)', data).group(1))
        body = data[-content_length:]
        item = json.loads(body)

        # Se o caminho é "/caixa"
        if path == '/caixa':
            if isinstance(item, list):
                self.data_store['caixa'].extend(item)
            else:
                self.data_store['caixa'].append(item)
            return HTTP_CREATED, "Item(s) adicionado(s) ao caixa"

        # Se o caminho é "/compras"
        elif path == '/compras':
            if isinstance(item, list):
                self.data_store['compras'].extend(item)
            else:
                self.data_store['compras'].append(item)
            return HTTP_CREATED, "Item(s) adicionado(s) às compras"

        else:
            return HTTP_NOT_FOUND, "Não encontrado"


    def handle_put_request(self, data, path):
        # Manipula requisições HTTP PUT
        # Usa expressão regular para extrair o ID do caixa do caminho
        match = re.match(r'/caixa/(\d+)', path)
        
        if match:
            caixa_id = int(match.group(1))
            # Procura o caixa correspondente pelo ID
            caixa = next((item for item in self.data_store['caixa'] if item['id'] == caixa_id), None)
            
            # Se o caixa for encontrado
            if caixa:
                # Extrai o tamanho do conteúdo
                content_length = int(re.search(r'Content-Length: (\d+)', data).group(1))
                # Extrai o corpo da requisição
                body = data[-content_length:]
                # Transforma o corpo em um objeto Python
                update_data = json.loads(body)
                
                # Atualiza o status do caixa
                caixa['status'] = update_data.get('status', caixa['status'])
                # Retorna HTTP 200 OK e uma mensagem indicando sucesso
                return HTTP_OK, "Caixa atualizado com sucesso"
            else:
                # Se o caixa não for encontrado, retorna HTTP 404 Not Found
                return HTTP_NOT_FOUND, "Caixa não encontrado"
        else:
            # Se o caminho não corresponder ao padrão esperado, retorna HTTP 404 Not Found
            return HTTP_NOT_FOUND, "Não encontrado"
def main():
    # Cria uma instância do servidor HTTP simples
    server = SimpleHTTPServer()

    # Usa a biblioteca de soquete para criar um novo soquete
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Vincula o soquete ao endereço IP e porta especificados
        s.bind((HOST, PORT))
        
        # Coloca o servidor em modo de escuta para aceitar conexões de clientes
        s.listen()

        # Imprime uma mensagem no log informando que o servidor está escutando
        logging.info(f"Servidor escutando em {HOST}:{PORT}")
        
        # Loop infinito para lidar com múltiplas conexões
        while True:
            # Aceita uma conexão do cliente
            conn, addr = s.accept()
            
            # Imprime uma mensagem no log informando que uma nova conexão foi aceita
            logging.info(f"Conexão aceita de {addr}")
            
            # Cria um novo thread para lidar com a conexão do cliente
            # Isso permite que múltiplos clientes se conectem simultaneamente
            client_thread = threading.Thread(target=server.handle_single_connection, args=(conn, addr))
            
            # Inicia o thread
            client_thread.start()

# Verifica se este script é o ponto de entrada principal e, em caso afirmativo, chama a função main()
if __name__ == "__main__":
    main()
