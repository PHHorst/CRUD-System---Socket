import socket
import struct
import re
import itertools

#IDENTIFICANDO O IP AUTOMATICAMENTE
try:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f"Internal IPv4 Address for {hostname}: {ip}")
except socket.gaierror:
    print("There was an error resolving the hostname.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Função para criar uma conexão com o servidor
def connect_to_server():
    try:
        socketDados = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        enderecoServidor = (ip, 50001)
        socketDados.connect(enderecoServidor)
        #socketDados.settimeout(10)  # Define um timeout de 10 segundos para operações de leitura
        return socketDados
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")
        return None

# Função para enviar uma mensagem para o servidor
def send_message(socketDados, mensagem):
    try:
        socketDados.send(mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem para o servidor: {e}")

# Função para receber uma mensagem do servidor
def receive_message(socketDados):
    try:
        dados_recebidos = b""
        while True:
            dados = socketDados.recv(1024)
            if not dados:
                break
            dados_recebidos += dados
        return dados_recebidos
    except Exception as e:
        print(f"Erro ao receber mensagem do servidor: {e}")
        return None

# Função para cadastrar um jogo
def cadastrar_jogo(socketDados):
    try:
        print('Cadastre um jogo')
        nome = input('Digite o nome: ')
        tema = input('Digite o tema: ')
        genero = input('Digite o gênero: ')
        ano = int(input('Digite o ano: '))
        nota = float(input('Digite a nota: '))

        operacao = 'C'  # 'C' para criação
        operacao_byte = operacao.encode("utf-8")
        
        nome_byte = nome.encode("utf-8")
        tema_byte = tema.encode("utf-8")
        genero_byte = genero.encode("utf-8")
        ano_byte = ano.to_bytes(length=4, byteorder="big")

        tamanho_nome = len(nome_byte)
        tamanho_byte1 = tamanho_nome.to_bytes(2, "big")
        tamanho_tema = len(tema_byte)
        tamanho_byte2 = tamanho_tema.to_bytes(2, "big")
        tamanho_genero = len(genero_byte)
        tamanho_byte3 = tamanho_genero.to_bytes(2, "big")

        nota_bytes = struct.pack('>d', nota)

        mensagem = operacao_byte + tamanho_byte1 + nome_byte + tamanho_byte2 + tema_byte + tamanho_byte3 + genero_byte + ano_byte + nota_bytes

        send_message(socketDados, mensagem)
    except Exception as e:
        print(f"Erro ao cadastrar jogo: {e}")

# Função para listar os jogos cadastrados
def listar_jogos(socketDados):
    try:
        operacao = 'L'  # 'R' para leitura
        operacao_byte = operacao.encode("utf-8")
        mensagem = operacao_byte
        send_message(socketDados, mensagem)

        dados_recebidos = receive_message(socketDados)
        if dados_recebidos:
            tamanho_dados = int.from_bytes(dados_recebidos[:2], "big")
            dados_decodificados = dados_recebidos[2:2 + tamanho_dados]
            dados= dados_decodificados.decode("utf-8")
            palavras_entre_aspas = re.findall(r"'([^']*)'", dados)
            dados_marcados = re.sub(r"'([^']*)'", r'\1', dados)
            resultados = re.split(r"[\[\],\(\)]+|\s*,\s*", dados_marcados)
            resultados = [p if p != '__MARCA__' else palavras_entre_aspas.pop(0) for p in resultados]
            resultados = [r.strip() for r in resultados if r.strip()]
            resultado_iter=itertools.cycle(resultados)
            tamanho_iterador = len(resultados)
            print()
            for _ in range(tamanho_iterador // 5):
                print("Nome:", next(resultado_iter))
                print("Tema:", next(resultado_iter))
                print("Gênero:", next(resultado_iter).strip("'"))
                print("Ano de Lançamento:", next(resultado_iter))
                print("Nota:", next(resultado_iter))
                print()
    except Exception as e:
        print(f"Erro ao ler jogos: {e}")


def find_jogo(socketDados):
    try:
        nome_jogo = input("Digite o nome do jogo a ser Procurado: ")

        operacao = 'R'  # 'R' para encontrar
        operacao_byte = operacao.encode("utf-8")

        dados = nome_jogo
        dados_byte = dados.encode("utf-8")
        tamanho_dados = len(dados_byte)
        tamanho_dados_byte = tamanho_dados.to_bytes(2, "big")
        mensagem = operacao_byte + tamanho_dados_byte + dados_byte
        send_message(socketDados, mensagem)

        dados_recebidos = receive_message(socketDados)
        if dados_recebidos:
            tamanho_dados = int.from_bytes(dados_recebidos[:2], "big")
            dados_decodificados = dados_recebidos[2:2 + tamanho_dados]
            dados= dados_decodificados.decode("utf-8")
            palavras_entre_aspas = re.findall(r"'([^']*)'", dados)
            dados_marcados = re.sub(r"'([^']*)'", r'\1', dados)
            resultados = re.split(r"[\[\],\(\)]+|\s*,\s*", dados_marcados)
            resultados = [p if p != '__MARCA__' else palavras_entre_aspas.pop(0) for p in resultados]
            resultados = [r.strip() for r in resultados if r.strip()]
            resultado_iter=itertools.cycle(resultados)
            tamanho_iterador = len(resultados)
            print()
            print("Nome:", next(resultado_iter))
            print("Tema:", next(resultado_iter))
            print("Gênero:", next(resultado_iter).strip("'"))
            print("Ano de Lançamento:", next(resultado_iter))
            print("Nota:", next(resultado_iter))
            print()
    except Exception as e:
        print(f"Erro ao procurar jogo: {e}")

# Função para atualizar um jogo
def atualizar_jogo(socketDados):
    try:
        nome_jogo = input("Digite o nome do jogo a ser atualizado: ")

        operacao = 'U'  # 'U' para atualização
        operacao_byte = operacao.encode("utf-8")

        campos = ['nome', 'tema', 'genero', 'ano', 'nota']
        campos_atualizar = campos

        dados = f'{nome_jogo},' + ','.join([input(f"Digite o novo valor para {campo}: ") for campo in campos_atualizar])
        dados_byte = dados.encode("utf-8")
        tamanho_dados = len(dados_byte)
        tamanho_dados_byte = tamanho_dados.to_bytes(2, "big")
        mensagem = operacao_byte + tamanho_dados_byte + dados_byte

        send_message(socketDados, mensagem)
    except Exception as e:
        print(f"Erro ao atualizar jogo: {e}")

# Função para excluir um jogo
def excluir_jogo(socketDados):
    try:
        nome_jogo = input("Digite o nome do jogo a ser excluído: ")

        operacao = 'D'  # 'D' para exclusão
        operacao_byte = operacao.encode("utf-8")

        dados = nome_jogo
        dados_byte = dados.encode("utf-8")
        tamanho_dados = len(dados_byte)
        tamanho_dados_byte = tamanho_dados.to_bytes(2, "big")
        mensagem = operacao_byte + tamanho_dados_byte + dados_byte

        send_message(socketDados, mensagem)
    except Exception as e:
        print(f"Erro ao excluir jogo: {e}")

# Função para sair do programa
def sair(socketDados):
    socketDados
    print("Saindo do programa...")
    exit()

# Função principal
def main():
    socketDados = connect_to_server()
    if not socketDados:
        exit()

    options = {
        'create': cadastrar_jogo,
        'list': listar_jogos,
        'find': find_jogo,
        'update': atualizar_jogo,
        'delete': excluir_jogo,
        'sair': sair
    }

    while True:
        print("\nOpções disponíveis: create, list, find, update, delete, sair")
        opcao = input("Escolha uma opção: ").lower()

        if opcao in options:
            options[opcao](socketDados)
            socketDados.close()
            socketDados = connect_to_server()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
