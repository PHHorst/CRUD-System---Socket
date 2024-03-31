import socket
import struct
import mysql.connector 

#IDENTIFICANDO O IP AUTOMATICAMENTE
try:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f"Internal IPv4 Address for {hostname}: {ip}")
except socket.gaierror:
    print("There was an error resolving the hostname.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

meubd = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Pedroh12354',
    database='GAME'
)

cursor = meubd.cursor()

socketConexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

porta = 50001

socketConexao.bind((ip, porta))
socketConexao.listen()

while True: #Agora os bits das operações são passados para comunicar o servidor
    [socketDados, infoCliente] = socketConexao.accept()

    operacao = socketDados.recv(1).decode("utf-8")

    if operacao == 'C':
        bytes = socketDados.recv(2)
        tamanho_nome = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_nome)
        nome = bytes.decode("utf-8")

        bytes = socketDados.recv(2)
        tamanho_tema = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_tema)
        tema = bytes.decode("utf-8")

        bytes = socketDados.recv(2)
        tamanho_genero = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_genero)
        genero = bytes.decode("utf-8")

        bytes = socketDados.recv(4)
        ano = int.from_bytes(bytes, "big")

        bytes = socketDados.recv(8)
        nota = struct.unpack('>d', bytes)[0]

        comando_insert = 'INSERT INTO atributos (nome, tema, genero, ano, nota) VALUES (%s, %s, %s, %s, %s)'
        valores = (nome, tema, genero, ano, nota)
        cursor.execute(comando_insert, valores)
        meubd.commit()

        print("Jogo cadastrado com sucesso.")

    elif operacao == 'L':

        comando_select = 'SELECT * FROM atributos'
        cursor.execute(comando_select)
        row1= cursor.fetchone()
        resultado = cursor.fetchall()
        resultados= (str(row1)+ str(resultado)).encode()
        socketDados.send(resultados) 
        print("Jogos listados com sucesso.")

    elif operacao == 'R':
        bytes = socketDados.recv(2)
        tamanho_dados = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_dados)
        nome_jogo = bytes.decode("utf-8")
        valores_find=(nome_jogo,)
        comando_select = 'SELECT * FROM atributos WHERE nome = %s'
        cursor.execute(comando_select, valores_find)
        resultado= cursor.fetchone()


        resultados= (str(resultado)).encode()
        socketDados.send(resultados) 
        print("Jogo encontrado com sucesso.")


    elif operacao == 'U':
        bytes = socketDados.recv(2)
        tamanho_dados = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_dados)
        dados = bytes.decode("utf-8")

        #Como eu coloquei a chave primária do banco de dados sendo o nome, fiz tudo baseado na alteração do nome no banco
        # Separa os dados recebidos em nome e valores dos campos a serem atualizados
        id_jogo, *valores = dados.split(',')

        # Lista de campos disponíveis para atualização
        campos = ['nome', 'tema', 'genero', 'ano', 'nota']

        # Gera a parte SET do comando UPDATE
        set_clause = ", ".join([f"{campo} = %s" for campo in campos])

        # Monta o comando UPDATE
        comando_update = f'UPDATE atributos SET {set_clause} WHERE nome = %s'  # Assumindo que a chave primária é "id"

        # Executa o comando UPDATE com os valores recebidos e o nome do jogo
        cursor.execute(comando_update, [*valores, id_jogo])
        meubd.commit()

        print("Jogo atualizado com sucesso.")

    elif operacao == 'D':
        bytes = socketDados.recv(2)
        tamanho_dados = int.from_bytes(bytes, "big")
        bytes = socketDados.recv(tamanho_dados)
        nome_jogo = bytes.decode("utf-8")  # Obtém o nome do jogo, mesma coisa da chave primária
        comando_delete = 'DELETE FROM atributos WHERE nome = %s'  # Usando o nome como critério
        valores_delete = (nome_jogo,)
        cursor.execute(comando_delete, valores_delete)
        meubd.commit()

        print("Jogo deletado com sucesso.")


    socketDados.close()

cursor.close()
meubd.close()
socketConexao.close()
