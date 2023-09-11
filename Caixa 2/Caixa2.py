# Importa o módulo JSON para manipulação de dados em formato JSON
import json
import socket
# Importa o módulo requests para fazer requisições HTTP
import requests
# Importa o módulo subprocess para executar comandos shell externos
import subprocess
import random

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
    
# Define a função para ler tags RFID
def ler_tags():
    # Executa o script Python que está no Raspberry Pi e captura sua saída.
    # 'text=True' faz com que a saída seja capturada como uma string
    completed_process = subprocess.run(["python3", "read.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Verifica se o script foi executado com sucesso (código de retorno 0)
    if completed_process.returncode == 0:
        # Pega a saída padrão do script e remove espaços em branco do início e do fim
        # Em seguida, divide a saída em linhas
        linhas = completed_process.stdout.strip().split("\n")
        
        # Cria uma lista vazia para armazenar as tags processadas
        tags_processadas = []
        
        # Itera sobre as linhas da saída
        for i, linha in enumerate(linhas):
            # Divide cada linha em seus componentes (tag, read_count, horário)
            valores = linha.split()
            
            # Gera nomes genéricos para os produtos (Produto1, Produto2, ...)
            nome_produto = f"Produto{i+1}"
            
            # Gera um preço aleatório entre 1 e 50
            preco = random.uniform(1, 20)
            
            # Verifica se há pelo menos três valores na linha
            if len(valores) >= 3:
                tag_str = valores[0]
                read_count = int(valores[1])
                horario = " ".join(valores[2:])
                
                # Adiciona a tag processada à lista
                tags_processadas.append([tag_str, read_count, nome_produto, preco, horario])
            else:
                print(f"A linha {i+1} não possui informações suficientes e será ignorada.")
        
        # Retorna a lista de tags processadas
        return tags_processadas
    
    else:
        # Se o script não foi executado com sucesso, imprime uma mensagem de erro
        print("Erro na execução do script do Raspberry Pi")
        
        # Retorna uma lista vazia pois a leitura falhou
        return []


# Define a função iniciar_compra
def iniciar_compra(id_caixa):
    produtos = ler_tags()
    if not produtos:
        print("Nenhuma tag de produto encontrada.")
        return []

    total = 0
    print("\nItens no Carrinho:")
    
    dados_compra = []

    for produto in produtos:
        nome_produto = produto[2]
        preco_produto = produto[3]
        quantidade = produto[1]
        
        dados_compra.append({
            'tag': produto[0],
            'nome': nome_produto,
            'preco': preco_produto,
            'quantidade': quantidade
        })

        print(f"Nome: {nome_produto}, Preço: {preco_produto:.2f}, Quantidade: {quantidade}")
        total += preco_produto * quantidade

    print(f"\nTotal da Compra: {total:.2f}")
    
    if verifica_status_caixa(id_caixa):
        pago = float(input("Informe o valor pago: "))
        troco = pago - total

        # Criando um objeto único para a compra
        objeto_compra = {
            'produtos': dados_compra,
            'total': total,
            'valor_pago': pago,
            'troco': troco if troco >= 0 else 0
        }
        
        print(objeto_compra)

        if pago >= total:
            print(f"\nTroco: {troco:.2f}")

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
    response = requests.get("http://134.125.107.117:3389/caixa")
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