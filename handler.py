import criptografia as cp
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

class ServerHandler(Thread):

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = []
        self.active = True
        self.users = {'bruno': 'a',
                      'joao': 's',
                      'maria': 'd',
                    }

    def stop(self):
        self.active = False


    def VerificaUsuario(self, nomeUsuario):
        if nomeUsuario in self.users.keys():
            return True
        else:
            return False


    def brod(self, msg, from_addr):
        for client in self.connections:
            if client.addr != from_addr:
                client.conn.sendall(msg.encode())

    def todasConexoes(self, from_addr):
        data = ''
        for client in self.connections:
            if client.addr != from_addr:
                data += f'{client.nomeUsuario} : {client.addr}\n'
        return data


    def close_conn(self):
        return


    def VerificaSenha(self, nomeUsuario, password):
        if self.users[nomeUsuario] == password:
            return True
        else:
            return False

    def priv(self, data, from_user):
        to_user = data.msgValue.split(' ')[0]
        for client in self.connections:
            if client.nomeUsuario == to_user:
                msg = cp.enviar('priv', f'({from_user}): {" ".join(data.msgValue.split(" ")[1:])}')
                

                client.conn.sendall(msg.encode())
                return True
        return False  

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(5)

            while self.active:
                print(f'Waiting for new connections...')

                conn, addr = s.accept()

                ch = ConnectionHandler(conn, addr, self)
                self.connections.append(ch)
                ch.start()



class ConnectionHandler(Thread):

    def __init__(self, conn, addr, callback):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.callback = callback
        self.active = True
        self.logged = False
        self.nomeUsuario = ''
        self.password = ''
        self.tent = 0

    def close_conn(self):
        return


    def run(self):
        print(f'O cliente {self.addr} foi conectado!\n')

        with self.conn:
            while self.active:
                data = self.conn.recv(1024) 
                data_rec = cp.read_incoming(data)

                if data_rec.msgType == 'user':
                    if self.callback.VerificaUsuario(data_rec.msgValue):
                        self.nomeUsuario = data_rec.msgValue
                        print(f'O cliente {self.addr} conectou como {self.nomeUsuario}!\n')
                        response = cp.enviar('ok')
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.enviar('err', message='1XX')  
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'pass':
                    if self.nomeUsuario == '':
                        response = cp.enviar('err', message='3XX')  
                        self.conn.sendall(response.encode())

                    if self.callback.VerificaSenha(self.nomeUsuario, data_rec.msgValue):
                        self.password = data_rec.msgValue
                        self.logged = True
                        print(f'O cliente {self.addr} conectado como {self.nomeUsuario} logou com sucesso!\n')
                        response = cp.enviar('ok')
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.enviar('err', message='2XX') 
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'mesg':
                    if self.logged:
                        broad_send = cp.enviar('brod', self.nomeUsuario + ' ' + data_rec.msgValue)
                        self.callback.brod(broad_send, self.addr)
                        print(f'O cliente {self.addr} mandou um texto broadcast : {data_rec.msgValue}\n')
                    else:
                        response = cp.enviar('err', message='4XX')  
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'retr':
                    if self.logged:
                        msg = self.callback.todasConexoes(self.addr)
                        response = cp.enviar('ok', message=msg)
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.enviar('err', message='4XX') 
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'priv':
                    if self.logged:
                        if self.callback.priv(data_rec, self.nomeUsuario):
                            pass
                        else:
                            response = cp.enviar('err', message='5XX')  
                            self.conn.sendall(response.encode())
                    else:
                        response = cp.enviar('err', message='4XX')  
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'brod':
                    if self.logged:
                        ...
                    else:
                        response = cp.enviar('err', message='4XX') 
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'clos':
                    print(f'O cliente {self.addr} conectado como {self.nomeUsuario} desconectou com sucesso!\n')
                    self.active = False
                    self.callback.connections.remove(self)

                elif data_rec.msgType == 'ok  ':
                    ...
                elif data_rec.msgType == 'err ':
                    ...
