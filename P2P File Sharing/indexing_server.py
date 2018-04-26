#!/usr/bin/python
import socket
import sys
import threading
import time
import os
import json

HOSTNAME = 'localhost'
PORT = 3000             # Random port 
BUFFER = 65536
                
class central_server_class():
    def __init__(self):
        #super(central_server_class,self).__init__()
        self.server = None
        self.threads_ = []
        self.file_index = {}
        self.peer_offset_port = 6000
        self.peer_list = []

    # Register peer    

    def register_peer(self):
        if len(self.peer_list) != 0:
            port_no = max(self.peer_list) + 1 
            self.peer_list.append(port_no)
            return str(port_no)
        else:
            self.peer_list.append(self.peer_offset_port)
            return str(self.peer_offset_port)    


    # Index the files, They are now in {file_name: [peer1,peer2..]} format.
    # Each key (file_name) maintains a list of all the peer's that contains the file.

    def index(self,request):
        for i,v in request.items():
            if i == 'command':
                pass
            else:
                if type(v) == list:
                    for sub_f in v:
                        sub_f = sub_f.lower()
                        if sub_f in self.file_index.keys():
                            self.file_index[sub_f].append(i)
                        else:
                            self.file_index[sub_f] = []
                            self.file_index[sub_f].append(i)

                elif type(v) == tuple:
                    files_added = v[0]
                    files_deleted = v[1]
                    if len(files_added) != 0:
                        for subs in files_added:
                            subs = subs.lower()
                            if subs in self.file_index.keys():
                                self.file_index[subs].append(i)
                            else:
                                self.file_index[subs] = []
                                self.file_index[subs].append(i)      
                    if len(files_deleted) != 0:
                        for subs_ in files_deleted:
                            subs_ = subs_.lower()
                            self.file_index[subs_].pop(self.file_index.index(i))            

    def search(self,request):
        file_name = request['filename']
        if file_name in self.file_index.keys():
            return json.dumps({file_name:self.file_index[file_name]})
        else:
            return 'File not found in the index.'    

    def list_all_files(self):
        return json.dumps(self.file_index)

    def destroy_peer(self,peer):
        for i,v in self.file_index.items():
            if unicode(peer) in v:
                v.pop(v.index(unicode(peer)))

    def process_request(self):
        client_connection = None                
        print '*'*80
        print 'Server is now running on port %d' % PORT
        print 'Press cntrl+c to shutdown server.!!'
        print '*'*80
        infinite = 1

        while infinite:
            try:
                self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server.bind((HOSTNAME,PORT))
                self.server.listen(10)  # Listen upto 10 connections before droping them (queue).
                client_connection,client_addr = self.server.accept()
                if client_connection:
                    print 'Connection Received from: %s on port: %d' % (client_addr[0],client_addr[1])
                    request = client_connection.recv(BUFFER)
                    req = json.loads(request)
                    command = req['command']

                    if command == 'index':
                        self.index(req)
                    elif command == 'list_all_files':
                        all_files = self.list_all_files()
                        client_connection.sendall(all_files)
                    elif command == 'search':
                        search_results = self.search(req)
                        client_connection.sendall(search_results)
                    elif command == 'register':
                        peer_id = self.register_peer()
                        client_connection.sendall(peer_id)
                    elif command == 'destroy':
                        peer_id = req['peer']
                        self.destroy_peer(peer_id)    
                    else:    
                        pass   

            except KeyboardInterrupt:
                infinite = 0
                print '*'*78
                print '\nKeyboard Interrupt Caught.!'
                print 'Shutting Down Peer Server..!!!'
                print '*'*80
                sys.exit(1)                                  
                        
            except Exception as e:
                print '*'*80
                print 'Processing Error..!!'
                print e.message
                print ''
                #print '\nShutting down..!!'
                sys.exit(1)
                raise
             
                 
            finally:
                self.server.close() 
                #print '*'*80
    def close(self):
        self.server.close()
        
    def run_(self):
        self.process_request()

if __name__ == '__main__':
    try:
        cs = central_server_class()
        cs.run_()

    except KeyboardInterrupt:
        print '*'*78
        print '\nKeyboard Interrupt Caught.!'
        print 'Shutting Down Peer Server..!!!'
        print '*'*80
        cs.close()
        sys.exit(1)