import socket
import threading
import time
import criptografia as cp

HOST = 'localhost'
PORT = 12321


def handle_received_message(sock):
    while True:
        try:
            data = sock.recv(1024)
        except ConnectionAbortedError:
            exit()
        data = cp.read_incoming(data)
        if data.msgType == 'brod':
            print(f'Broadcast recebido: ({data.msgValue.split(" ")[0]}) {" ".join(data.msgValue.split(" ")[1:])}')
        elif data.msgType == 'priv':
            print(f'Mensagem privada recebida recebido: {data.msgValue}')
        elif data.msgType == 'ok  ':
            print(f'Comando realizado com sucesso:\n {data.msgValue}')
        elif data.msgType == 'err ':
            print('Erro:\n' + error_dict[data.msgValue])
        elif data.msgType == 'clos':
            print('Servidor fechando, finalizando processo')
            sock.close()
            exit()




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    error_dict = {'1XX': 'usuario nao existente',
                  '2XX': 'senha errada',
                  '3XX': 'nao tinha usuario ainda',
                  '4XX': 'usuario nao logado',
                  '5XX': 'usuario nao encontrado'
                  }
    s.connect((HOST, PORT))

    while True:
        nomeUsuario = input('Digite seu nome de usuário: ')
        usuarioMensagem = cp.enviar('user', nomeUsuario)
        s.sendall(usuarioMensagem.encode())

        data = s.recv(1024)
        servidorResposta = cp.read_incoming(data)

        if servidorResposta.msgType == 'ok  ':
            print('Usuario aceito, prossiga com a senha...')
            break
        elif servidorResposta.msgType == 'err ':
            print('Erro:\n' + error_dict[servidorResposta.msgValue])

    while True:
        nomeUsuario = input('Digite sua senha: ')
        usuarioMensagem = cp.enviar('pass', nomeUsuario)
        s.sendall(usuarioMensagem.encode())

        data = s.recv(1024)
        servidorResposta = cp.read_incoming(data)

        if servidorResposta.msgType == 'ok  ':
            print('Senha aceita,conectado com sucesso...')
            break
        elif servidorResposta.msgType == 'err ':
            print('Erro:\n' + error_dict[servidorResposta.msgValue])


    t = threading.Thread(target=handle_received_message, args=(s,))
    t.start()

    while True:
        try:
            time.sleep(.1)
            comando = 'mesg'
            text = input('Digite uma mensagem a ser enviada ao servidor: \n')
            if text[0] == '-':
                comando = text[1:5]
                text = text[6:]
                if comando == 'priv':
                    pass
                elif comando == 'mesg':
                    pass
                elif comando == 'retr' or comando == 'clos':
                    text = ''
                else:
                    print('Comando inválido.')
                    continue

            msg = cp.enviar(comando, text)
            s.sendall(msg.encode())
            if comando == 'clos':
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            print('')
            print('Encerrando o cliente...')
            s.close()
            break

print('Bye bye!')
