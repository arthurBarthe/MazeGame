import threading
import sys
import socket
from collections import deque

class Communication_out(threading.Thread):
    def __init__(self, connection, lock):
        threading.Thread.__init__(self)
        self.connection = connection
        self.to_send_queue = deque()
        self.all_sent = True
        self.lock = lock

    def add_message_to_send(self, message):
        self.all_sent = False
        self.to_send_queue.append(message)

    def send_and_confirm_reception(self, message):
        #First we empty the stack
        while not self.all_sent:
            pass
        message_title, message_content = message
        message_size = sys.getsizeof(message_content)/1024
        #We send the size
        self.connection.send(str(message_size))
        response = self.connection.recv()
        if response == 'ready':
            self.connection.send(message_content)
            

    def run(self):
        while 1:
            if not self.all_sent:
                self.lock.acquire()
                message_title, message_content = self.to_send_queue.popleft()
                message_size = sys.getsizeof(message_content)/1024
                #We send the size
                self.connection.send(str(message_size))
                response = self.connection.recv(100)
                if response == 'ready':
                    self.connection.send(message_content)
                response = self.connection.recv(100)
                if response == 'received' and len(self.to_send_queue) == 0:
                    self.all_sent = True
                self.lock.release()

class Communication_in(threading.Thread):
    def __init__(self, connection, lock):
        threading.Thread.__init__(self)
        self.connection = connection
        self.lock = lock

    def run(self):
        while 1:
            self.lock.acquire()
            message_size = int(self.connection.recv(100))
            self.connection.send('ready')
            message_content = self.connection.recv((message_size+1)*1024)
            self.connection.send('received')
            print "Friend> " + message_content
            self.lock.release()

if __name__ == '__main__':
    server = raw_input('Are you the <s>erver or <c>lient?').upper()
    if server == 'S':
        host = socket.gethostname()
        port = 6000
        print 'Adresse serveur: ' + host + ", PORT " + str(port)
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            mySocket.bind((host, port))
        except socket.error:
            print "Connection failed."
            sys.exit()
        print "Server is ready"
        mySocket.listen(1)
        connection, address = mySocket.accept()
        lock = threading.Lock()
        communication_out = Communication_out(connection, lock)
        communication_in = Communication_in(connection, lock)
        communication_out.start()
        communication_in.start()
    else:
        host = raw_input('host?')
        port = 6000
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            connection.connect((host, port))
        except socket.error:
            print "Connection has failed."
            sys.exit()
        print "Connection has been established with the server."
        lock = threading.Lock()
        communication_out = Communication_out(connection, lock)
        communication_in = Communication_in(connection, lock)
        communication_out.start()
        communication_in.start()
    while 1:
        message = raw_input("You> ")
        communication_out.add_message_to_send(("test", message))

                    
    
            
            
        
