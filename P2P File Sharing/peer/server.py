#!/usr/bin/python
import socket
import sys
import threading
import time
import os

HOSTNAME = 'localhost'
BUFFER = 65536

class handlers(threading.Thread):
    def __init__(self,client):
        super(handlers,self).__init__()
        self.client = client

    def request_handler(self):
        try:
            file_to_fetch = self.client.recv(BUFFER)
            path_to_file = './Files/'+file_to_fetch
            if os.path.isfile(path_to_file):
                fh = open(path_to_file,'rb')
                binary_data = fh.read()
                self.client.sendall(binary_data)
                return 'File Sent.!!'
                fh.close()
            else:
                self.client.sendall('Nope')
                return 'File not found..!!'    

        except Exception as e:    
            self.client.close()
            return  'File dosent exist.!!'

    def response_handler(self,data):
        try:
            self.client.sendall(data)
        except Exception as e:
            self.client.send('Unable to send the data, Check the connection.!')
            self.client.close()
            return

    def run(self):
        print '*'*80
        print 'Responding to client requests..!!'

        try:
            client_data = self.request_handler()

        finally:
            self.client.close()      
            
class server_class(threading.Thread):
    def __init__(self,port):
        super(server_class,self).__init__()
        self.PORT = port
        self.server = None
        self.threads_ = []
         
    def process_data(self):
        client_connection = None                

        while True:
            try:
                self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server.bind((HOSTNAME,self.PORT))
                self.server.listen(10)  # Listen upto 10 connections before droping them (queue).
                client_connection,client_addr = self.server.accept()
                if client_connection:
                    print 'Connection Received from: %s on port: %d' % (client_addr[0],client_addr[1])
                    handle = handlers(client_connection)
                    #multiple_cli.setDaemon(True)
                    thread_ = handle.start()
                    self.threads_.append(thread_)
                        
            except Exception as e:
                print '*'*80
                print 'Processing Error..!!'
                print e.message
                print '\nShutting down..!!'
                sys.exit(1)
                raise
                 
            finally:
                self.server.close() 
                #print '*'*80
    def close(self):
        self.server.close()
        
    def run(self):
        self.process_data()

    # Establish Connection between this peer and the centralized indexing server
    # Get the port number and other credentials from the centralized indexeing server

    # Move this function outside this file.
        
