# Importa o módulo JSON para manipulação de dados em formato JSON
import json
import socket
# Importa o módulo requests para fazer requisições HTTP
import requests

HOST, PORT = '34.125.107.117', 3389

# Função para verificar o status do caixa
def verifica_status_caixa(id_caixa):
    # Faz uma requisição GET para obter informações sobre um caixa específico
    response = requests.get(f"http://34.125.107.117:3389/caixa/{id_caixa}")
    if response.status_code == 200:
        caixa = response.json()
        return caixa.get("status", False)  
    else:
        print(f"Erro ao verificar o status do caixa {id_caixa}")
        return False

# Define a função iniciar_compra
def iniciar_compra(id_caixa):
    # Inicializa uma lista vazia chamada produtos
    produtos = []

    # Entra em um loop infinito
    while True:
        # Imprime uma mensagem no console
        print("\nInforme os detalhes do produto ou digite '.' para pagar a compra.")

        # Solicita o nome do produto ao usuário e armazena em uma variável
        nome = input("Nome do produto: ")

        # Verifica se o usuário digitou 'finalizado' (ignorando maiúsculas/minúsculas)
        if nome.lower() == '.':
            # Sai do loop
            break

        # Solicita o preço do produto ao usuário e converte para float
        preco = float(input("Preço do produto: "))
        # Solicita a quantidade do produto ao usuário e converte para int
        quantidade = int(input("Quantidade: "))

        # Cria um dicionário contendo as informações do produto
        produto = {
            'nome': nome,
            'preco': preco,
            'quantidade': quantidade
        }

        # Adiciona o dicionário do produto à lista de produtos
        if verifica_status_caixa(id_caixa):
            produtos.append(produto)
        else:
            return "Caixa bloqueado, tente novamente!"

    # Inicializa uma variável para armazenar o total da compra
    total = 0
    # Imprime uma mensagem no console
    print("\nItens no Carrinho:")

    # Loop para iterar sobre cada produto na lista de produtos
    for produto in produtos:
        # Imprime as informações de cada produto no console
        print(f"Nome: {produto['nome']}, Preço: {produto['preco']:.2f}, Quantidade: {produto['quantidade']}")
        # Atualiza o total da compra
        total += produto['preco'] * produto['quantidade']

    if verifica_status_caixa(id_caixa):

        # Imprime uma mensagem mostrando o total da compra
        print(f"\nTotal da Compra: {total:.2f}")

        # Solicita o valor pago pelo usuário e converte para float
        pago = float(input("Informe o valor pago: "))

        # Verifica se o valor pago é maior ou igual ao total da compra
        if pago >= total:
            # Calcula o troco
            troco = pago - total
            # Imprime o troco no console
            print(f"\nTroco: {troco:.2f}")

            # Cria um dicionário para armazenar os produtos, total da compra, valor pago e troco
            objeto_compra = {
                'produtos': produtos,
                'total': total,
                'pago': pago,
                'troco': troco
            }

            try:
                # Converte a lista objeto_compra para string JSON
                objeto_compra_json = json.dumps(objeto_compra)

                # Cria uma string HTTP POST request para enviar ao servidor
                request = f"POST /compras HTTP/1.1\r\nHost: {HOST}\r\nContent-Type: application/json\r\nContent-Length: {len(objeto_compra_json)}\r\n\r\n{objeto_compra_json}"

                try:
                    # Conecta ao servidor e envia a requisição
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        print("Conectando ao servidor...")
                        s.connect((HOST, PORT))
                        print("Conectado.")

                        print("Enviando dados...")
                        s.sendall(request.encode('utf-8'))
                        print("Dados enviados.")

                        # Recebe a resposta do servidor
                        print("Recebendo resposta...")
                        response = s.recv(1100).decode('utf-8')
                        print("Recebido:", response)

                        # Desserializa a resposta JSON para um objeto Python
                        response_dict = json.loads(response)
                        print("Resposta JSON: ", response_dict)
                        
                        # Verifica se a requisição foi bem-sucedida (Este é um exemplo, ajuste de acordo com seu caso)
                        if response_dict.get('status_code') == 201:  
                            print("\nCompra realizada com sucesso!")
                            return []
                        else:
                            print(f"\nErro ao realizar compra.")
                            return produtos

                except Exception as e:  # Captura qualquer exceção genérica
                    print(f"Ocorreu um erro: {e}")
                    return produtos

            except json.JSONDecodeError:  # Captura erros de decodificação JSON
                print("Não foi possível decodificar a resposta JSON.")
                return produtos


# Define a função caixa_disponivel
def caixa_disponivel():
    # Faz uma requisição GET para obter informações sobre os caixas disponíveis
    response = requests.get("http://34.125.107.117:3389/caixa")
    # Verifica o código de status da resposta
    if response.status_code == 200:
        # Converte a resposta JSON em um objeto Python
        caixas = response.json()
        # Cria uma lista dos IDs dos caixas disponíveis
        ids_disponiveis = [caixa["id"] for caixa in caixas]

        # Imprime os IDs dos caixas disponíveis no console
        print("\nCAIXAS DISPONÍVEIS ID:", ", ".join(map(str, ids_disponiveis)))

        # Entra em um loop infinito
        while True:
            try:
                # Solicita ao usuário que escolha um caixa
                escolha = int(input("Escolha um caixa para fazer suas compras:"))
                # Verifica se o caixa escolhido está na lista de caixas disponíveis
                if escolha in ids_disponiveis:
                    # Retorna o ID do caixa escolhido
                    return escolha
                else:
                    # Imprime uma mensagem de erro no console
                   
                    # Imprime uma mensagem de erro no console
                    print("\nID de caixa inválido. Tente novamente!")
            except ValueError:
                # Imprime uma mensagem de erro no caso de valor inválido (ex. texto ao invés de número)
                print("\nPor favor, insira um número válido para o ID do caixa.")
    else:
        # Imprime uma mensagem de erro caso não consiga recuperar informações sobre os caixas
        print("Erro ao recuperar caixas.")
        # Retorna None para indicar que a operação falhou
        return None

# Define a função principal, main
def main():
    id_caixa = caixa_disponivel()
    print(f"\nCaixa selecionado: {id_caixa}")

    compras = []

    while True:
        # Verifica se o caixa ainda está disponível
        if verifica_status_caixa(id_caixa):
            print("\nOpções:")
            print("1: Iniciar compra")
            print("2: Sair")
            
            escolha = input("\nSelecione uma opção: ")

            if escolha == '1':
                compras = iniciar_compra(id_caixa)
            elif escolha == '2':
                print("\nVolte sempre!")
                break
            else:
                print("\nOpção inválida!")
        else:
            print(f"\nO caixa {id_caixa} não está mais disponível.")
            id_caixa = caixa_disponivel()  # O usuário deve escolher um novo caixa
            print(f"\nNovo caixa selecionado: {id_caixa}")

if __name__ == "__main__":
    main()