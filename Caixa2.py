# Importa o módulo JSON para manipulação de dados em formato JSON
import json
# Importa o módulo requests para fazer requisições HTTP
import requests
# Importa o módulo subprocess para executar comandos shell externos
import subprocess

tag_to_produto = {
    "E20000172211009418905449": {'nome': 'Arroz 1kg', 'preco': 8.0, 'quantidade': 0},
    "E20000172211010218905459": {'nome': 'Feijão 1kg', 'preco': 12.0, 'quantidade': 0},
    "E2000017221101321890548C": {'nome': 'Milho de pipoca', 'preco': 4.5, 'quantidade': 0},
    "E2000017221101241890547C": {'nome': 'Repolho roxo', 'preco': 3.8, 'quantidade': 0},
    "E2000017221100961890544A": {'nome': 'Batata doce', 'preco': 10.0, 'quantidade': 0},
    "E20000172211010118905454": {'nome': 'Desinfetante', 'preco': 7.5, 'quantidade': 0},
    "E20000172211011118905471": {'nome': 'Sabonete', 'preco': 2.0, 'quantidade': 0},
    "E20000172211012518905484": {'nome': 'Papel higiênico', 'preco': 14.9, 'quantidade': 0},
    "E20000172211011718905474": {'nome': 'Ração gato castrado 3kg', 'preco': 50.0, 'quantidade': 0}
}

# Função para verificar o status do caixa
def verifica_status_caixa(id_caixa):
    # Faz uma requisição GET para obter informações sobre um caixa específico
    response = requests.get(f"http://34.16.181.77:3389/caixa/{id_caixa}")
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
    completed_process = subprocess.run(["sshpass", "-p", "larsid", "ssh", "tec502@172.16.103.0", "python3 /caminho/para/o/script.py"], capture_output=True, text=True)
    
    # Verifica se o script foi executado com sucesso (código de retorno 0)
    if completed_process.returncode == 0:
        # Pega a saída padrão do script e remove espaços em branco do início e do fim
        # Em seguida, divide a saída em linhas
        linhas = completed_process.stdout.strip().split("\n")
        
        # Divide cada linha em seus componentes (tag, read_count, etc.)
        # Isso é feito para cada linha na saída
        tags = [linha.split() for linha in linhas]
        
        # Itera sobre cada tag lida
        for tag in tags:
            # Desempacota os valores em variáveis
            tag_str, read_count, _, _ = tag
            
            # Verifica se a tag está em nosso dicionário de produtos
            if tag_str in tag_to_produto:
                # Atualiza a 'quantidade' do produto com base no 'read_count' da tag
                tag_to_produto[tag_str]['quantidade'] = int(read_count)
        
        # Retorna uma lista de produtos com quantidade maior que zero
        return [tag_to_produto[tag_str] for tag_str in tag_to_produto if tag_to_produto[tag_str]['quantidade'] > 0]
    
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

    for produto in produtos:
        print(f"Nome: {produto['nome']}, Preço: {produto['preco']:.2f}, Quantidade: {produto['quantidade']}")
        total += produto['preco'] * produto['quantidade']

    # Imprime uma mensagem mostrando o total da compra
    print(f"\nTotal da Compra: {total:.2f}")
    
    if verifica_status_caixa(id_caixa):
        # Solicita o valor pago pelo usuário e converte para float
        pago = float(input("Informe o valor pago: "))

        # Verifica se o valor pago é maior ou igual ao total da compra
        if pago >= total:
            # Calcula o troco
            troco = pago - total
            # Imprime o troco no console
            print(f"\nTroco: {troco:.2f}")

            # Faz uma requisição POST para adicionar os produtos à lista de compras no servidor
            response = requests.post("http://34.16.181.77:3389/compras", json=produtos)

            # Verifica o código de status da resposta
            if response.status_code == 201:
                # Imprime uma mensagem de sucesso no console
                print("\nCompra realizada com sucesso!")
                # Retorna uma lista vazia para iniciar uma nova compra
                return []
            else:
                # Imprime uma mensagem de erro no console
                print("\nErro ao realizar compra.")
                # Retorna a lista atual de produtos para tentar novamente
                return produtos
        else:
            # Imprime uma mensagem informando que o valor pago é insuficiente
            print("\nValor insuficiente.")
            # Retorna a lista atual de produtos para tentar novamente
            return produtos
    else:
        return "Caixa bloquado, tente novamente!"

# Define a função caixa_disponivel
def caixa_disponivel():
    # Faz uma requisição GET para obter informações sobre os caixas disponíveis
    response = requests.get("http://34.16.181.77:3389/caixa")
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