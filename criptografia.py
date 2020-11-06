from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES
from Cryptodome.Cipher import PKCS1_OAEP

class criptografiaMessage:

    def __init__(self, msgType='', msgLength=0, msgValue=''):
        self.msgType = msgType
        self.msgLength = msgLength
        self.msgValue = msgValue

        chave = RSA.generate(2048, e=65537)

        self.private_key = chave.exportKey("PEM")
        self.public_key = chave.publickey().exportKey("PEM")
        self.AES_key = None
        self.other_key = None

    def encode(self):
        return f'{self.msgType} {self.msgValue}'.encode('utf8')

    def decode(self, data):
        msg = data.decode('utf-8')
        self.msgType = msg[0:4]
        self.msgLength = len(data)
        self.msgValue = msg[5:]

    def __repr__(self):
        return f'{self.msgType} {self.msgValue}'


def read_incoming(received):
    x = criptografiaMessage()
    x.decode(received)
    return x

def encode_rsa(self):
    publ = PKCS1_OAEP.new(RSA.import_key(self.other_key))
    return publ.encrypt(f'{self.msgType} {self.msgValue}'.encode('utf8'))


def decode_rsa(self, data):
    priv = PKCS1_OAEP.new(RSA.import_key(self.private_key))
    self.decode_raw(priv.decrypt(data))


def enviar(command, message=''):
    if command.lower() in ['retr', 'clos']:
        x = criptografiaMessage(command.lower().ljust(4), 5)
    else:
        x = criptografiaMessage(command.lower().ljust(4), 5 + len(message.encode('utf-8')), message)
    return x

