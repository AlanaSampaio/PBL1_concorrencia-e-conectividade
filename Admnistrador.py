# Importa a biblioteca requests para realizar requisições HTTP
import requests
# Importa a biblioteca threading para executar tarefas em paralelo
import threading
# Importa a biblioteca time para pausar a execução
import time
# Importa a biblioteca os para interagir com o sistema operacional
import os
# Importa a biblioteca sys para interagir com o sistema
import sys

# Define uma constante com o URL do servidor
SERVER_URL = "http://34.16.181.77:3389"

# Define a função get_caixas que obtém a lista de caixas do servidor
def get_caixas():
    # Realiza uma requisição GET ao endpoint /caixa no servidor
    response = requests.get(f"{SERVER_URL}/caixa")
    # Verifica se o status da resposta é 200 (OK)
    if response.status_code == 200:
        # Converte o conteúdo da resposta para JSON
        caixas = response.json()
        # Itera sobre cada caixa para imprimi-lo
        for caixa in caixas:
            print(caixa)
        # Retorna a lista de caixas
        return caixas
    else:
        # Imprime um erro se não conseguiu obter os caixas
        print("Erro ao recuperar caixas.")
        # Retorna uma lista vazia
        return []

# Define a função get_compras que obtém a lista de compras do servidor
def get_compras():
    # Realiza uma requisição GET ao endpoint /compras no servidor
    response = requests.get(f"{SERVER_URL}/compras")
    # Verifica se o status da resposta é 200 (OK)
    if response.status_code == 200:
        # Converte o conteúdo da resposta para JSON
        compras = response.json()
        # Itera sobre cada compra para imprimi-la
        for compra in compras:
            print(compra)
    else:
        # Imprime um erro se não conseguiu obter as compras
        print("Erro ao recuperar compras.")

# Define a função clear_terminal que limpa o terminal
def clear_terminal():
    # Verifica o sistema operacional e executa o comando de limpar o terminal correspondente
    os.system('cls' if os.name == 'nt' else 'clear')

# Define a função key_pressed_unix para sistemas Unix
def key_pressed_unix():
    import select
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    return dr != []

# Define a função key_pressed_windows para sistemas Windows
def key_pressed_windows():
    import msvcrt
    return msvcrt.kbhit()

# Escolhe a função adequada para verificar se uma tecla foi pressionada, com base no sistema operacional
key_pressed = key_pressed_windows if os.name == 'nt' else key_pressed_unix

# Define a função acompanhar_compras_tempo_real
def acompanhar_compras_tempo_real():
    print("Acompanhando compras em tempo real. Pressione CTRL+C para interromper.")
    try:
        # Entra em um loop infinito
        while True:
            # Limpa o terminal
            clear_terminal()
            # Chama a função get_compras para obter e imprimir as compras
            get_compras()
            # Verifica se alguma tecla foi pressionada
            if key_pressed():
                # Sai do loop se uma tecla foi pressionada
                break
            # Pausa a execução por 5 segundos
            time.sleep(5)
    except KeyboardInterrupt:
        # Sai do loop se CTRL+C for pressionado
        print("\nAcompanhamento interrompido.")

# Define a função criar_caixa que cria um novo caixa no servidor
def criar_caixa():
    try:
        # Solicita ao usuário para inserir o ID do caixa
        caixa_id = int(input("Informe o ID para o novo caixa: (somente números)"))
        # Prepara os dados para enviar ao servidor
        novo_caixa = {
            'id': caixa_id,
            'status': True  # Assume que o novo caixa estará ativo
        }
        # Realiza uma requisição POST para criar o novo caixa
        response = requests.post(f"{SERVER_URL}/caixa", json=novo_caixa)
        # Verifica se o caixa foi criado com sucesso
        if response.status_code == 201:
            print(f"\nCaixa com ID {caixa_id} criado com sucesso!")
        else:
            print("\nErro ao criar caixa. Tente novamente.")
    except ValueError:
        # Captura erro se o valor inserido não for um número
        print("O ID informado não é um número válido.")
    except Exception as e:
        # Captura qualquer outro tipo de erro
        print(f"Erro ao criar caixa: {e}")

# (O código ultrapassou o limite de caracteres. Continuarei na próxima mensagem.)
# Define a função bloquear_desbloquear_caixa para alterar o status de um caixa
def bloquear_desbloquear_caixa():
    try:
        # Mostra os caixas disponíveis
        get_caixas()
        # Solicita ao usuário que informe o ID do caixa
        caixa_id = int(input("\nInforme o ID do caixa que deseja bloquear ou desbloquear: "))
        
        # Busca informações sobre todos os caixas
        response = requests.get(f"{SERVER_URL}/caixa")
        caixas = response.json()
        
        # Procura pelo caixa com o ID especificado
        caixa_info = next((caixa for caixa in caixas if caixa['id'] == caixa_id), None)
        
        if caixa_info is None:
            print(f"\nCaixa com ID {caixa_id} não encontrado.")
            return

        # Recupera o status atual do caixa
        atual_status = caixa_info.get('status', None)

        if atual_status is None:
            print("\nNão foi possível determinar o status atual do caixa.")
            return
        
        # Pergunta ao administrador se ele quer mudar o status do caixa
        if atual_status:
            acao = input(f"O caixa {caixa_id} está desbloqueado. Você deseja bloqueá-lo? (sim/nao): ").lower()
            novo_status = False if acao == 'sim' else True
        else:
            acao = input(f"O caixa {caixa_id} está bloqueado. Você deseja desbloqueá-lo? (sim/nao): ").lower()
            novo_status = True if acao == 'sim' else False

        # Atualiza o status do caixa se for diferente do atual
        if novo_status != atual_status:
            data = {'status': novo_status}
            response = requests.put(f"{SERVER_URL}/caixa/{caixa_id}", json=data)
            if response.status_code == 200:
                status_msg = "Desbloqueado" if novo_status else "Bloqueado"
                print(f"\nStatus atual do caixa {caixa_id}: {status_msg}. Atualizado com sucesso!")
            else:
                print("\nErro ao atualizar o status do caixa.")
                print("Mensagem do servidor:", response.text)
        else:
            status_msg = "Desbloqueado" if atual_status else "Bloqueado"
            print(f"\nStatus atual do caixa {caixa_id}: {status_msg}. Nenhuma alteração realizada no caixa.")

    except Exception as e:
        # Captura qualquer exceção não tratada anteriormente
        print(f"Ocorreu um erro: {e}")

# Define a função principal do programa
def main():
    # Entra em um loop infinito para manter o programa rodando
    while True:
        # Mostra o menu de opções para o usuário
        print("\nOpções:")
        print("1: Ver caixas")
        print("2: Ver histórico de compras")
        print("3: Acompanhar compras em tempo real")
        print("4: Criar novo caixa")
        print("5: Bloquear/Desbloquear caixa")
        print("6: Sair")
        
        # Solicita uma escolha do usuário
        escolha = input("\nSelecione uma opção: ")
        
        # Executa a ação correspondente à escolha do usuário
        if escolha == '1':
            get_caixas()
        elif escolha == '2':
            get_compras()
        elif escolha == '3':
            # Inicia uma thread para acompanhar compras em tempo real
            threading.Thread(target=acompanhar_compras_tempo_real).start()
        elif escolha == '4':
            criar_caixa()
        elif escolha == '6':
            print("\nSaindo...")
            break
        elif escolha == '5':
            bloquear_desbloquear_caixa()
        else:
            print("\nOpção inválida!")

# Verifica se o script está sendo executado como o programa principal
if __name__ == "__main__":
    # Se for o caso, chama a função main para iniciar o programa
    main()
