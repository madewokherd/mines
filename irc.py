
# CONFUSINGLY GPL LICENSE

import random
import socket

random.seed()

def parse_irc(msg, server='x'):
    msg = msg.split(' ')
    
    # if our very first character is :
    # then this is the source, 
    # otherwise insert the server as the source
    if msg and msg[0].startswith(':'):
        msg[0] = msg[0][1:]
    else:
        msg.insert(0, server)
    
    # loop through the msg until we find 
    # something beginning with :
    for i, token in enumerate(msg):
        if token.startswith(':'):
            # remove the :
            msg[i] = msg[i][1:]
            
            # join up the rest
            msg[i:] = [' '.join(msg[i:])]
            break
    
    # filter out the empty pre-":" tokens and add on the text to the end
    return [m for m in msg[:-1] if m] + msg[-1:]

class Network:
    socket = None
    buf = bytearray()

    def __init__(self, server='irc.chat.twitch.tv', port=6667,
        nick=None, password='madewokherd', username='madewokherd',
        fullname='minesweeper bot', channel='madewokherd'):

        if nick is None:
            nick = 'justinfan' + str(random.randint(0,9999999))

        self.server = server
        self.port = port
        self.nick = nick
        self.password = password
        self.username = username
        self.fullname = fullname
        self.channel = channel

        result = socket.getaddrinfo(self.server, self.port, 0, socket.SOCK_STREAM)

        f, t, p, c, a = result[0]

        self.socket = socket.socket(f, t, p)

        self.socket.connect(a)

        self.send(f'PASS :{password}')
        self.send(f'NICK :{nick}')
        self.send(f'USER {username} 8 * :{fullname}')

        while True:
            line = self.readline()
            if line[1] == '004': # RPL_MYINFO
                # successfully connected
                break

        self.send(f'JOIN :{channel}')

        while True:
            line = self.readline()
            if line[1] == 'JOIN' and line[2] == channel:
                # successfully joined channel
                break

    def readline(self):
        while b'\r\n' not in self.buf:
            data = self.socket.recv(8192)
            if not data:
                return
            self.buf.extend(data)

        result, self.buf = self.buf.split(b'\r\n', 1)
        result = parse_irc(result.decode('utf8', 'surrogateescape'), self.server)
        print(result)
        return result

    def send(self, line):
        self.socket.send(f'{line}\r\n'.encode('utf8', 'surrogateescape'))

