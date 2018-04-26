from server import server_class
from FilesystemEventHandler import FilesystemEventHandler
from FilesystemEventHandler import destroy_peer
import socket
import sys
import json
import time
import datetime
import os
BUFFER = 65536
OUTPUT_DIR = './Files/'

class query_indexer():
    def __init__(self):
        self.ci_server_host = 'localhost'
        self.ci_server_port = 3000
        self.ci_server_addr = (self.ci_server_host,self.ci_server_port)
        self.index_socket = None
        self.credentials = None
        self.LIST_FILES = json.dumps({'command':'list_all_files'})
        self.GET_CREDENTIALS = json.dumps({'command':'register'})
        self.SEARCH_FOR_FILE = {'command':'search'}

    def send_command_to_cs(self,cmd):
        try:
            self.index_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.index_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.index_socket.connect(self.ci_server_addr)
            self.index_socket.sendall(cmd)
            response = self.index_socket.recv(BUFFER)
            return response

        except Exception as e:
            print 'Cannot connect to the Centralized Indexing Server'
            print 'Please make sure that the Server is running'
            print '*'*80
            print e.message
            sys.exit(1)
            return 'error'

        finally:    
            self.index_socket.close()         

    def get_credentials(self): 
        print '*'*80
        print 'Registering peer and fetching credentials from central server\n'
        try:
            self.credentials = self.send_command_to_cs(self.GET_CREDENTIALS)
            if self.credentials == 'error':
                raise
            self.credentials = int(self.credentials)   
            return self.credentials 
        except Exception as e:
            print 'Retrive credentials failed'
            print '*'*80

    def list_all_files(self):
        try:
            all_files = self.send_command_to_cs(self.LIST_FILES)
            all_files_ = json.loads(all_files)
            print '*'*80
            print '\nThe file index list from central server:\n'

            for i,v in all_files_.items():
                print '%s : %s' % (i,map(unicode.encode,v))
            print '*'*80    
        except Exception as e:
            print 'Retrive files list failed'
            print e.message
            print '*'*80

    def search_for_file(self,file_name):
        print '*'*80
        print '\nSearching central file index for the file and peer-id'
        try:
            self.SEARCH_FOR_FILE['filename'] = file_name
            search_command = json.dumps(self.SEARCH_FOR_FILE)
            search_file = self.send_command_to_cs(search_command)
            search_results = json.loads(search_file)
            try:
                print '\nThe File requested are in the following peers:'
                for files_ in search_results[file_name]:
                    print files_,
                print ''
                print '*'*80    
            except:
                print search_results        
                print '*'*80
        except Exception as e:
            print 'Retrive search file list failed (FILE NOT FOUND)'
            print e.message
            print '*'*80

    def obtain(self,peer_id,file_name):
        print '*'*80
        print 'Starting File Transfer..!'
        print 'Connecting to peer on:', peer_id

        st1 = datetime.datetime.now()
        try:
            server_addr = ('localhost',int(peer_id))
            connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            connection.connect(server_addr)
            connection.sendall(file_name)
            response = connection.recv(BUFFER)
            if response == 'Nope':
                print '\nOOPS, File Not Found'
                print '*'*80
                return
        except Exception as e:
            print 'File Transfer failed'
            print e.message
            print '*'*80
            return
        et1 = datetime.datetime.now()    

        try:
            file_path = OUTPUT_DIR + file_name
            fh = open(file_path,'wb')
            fh.write(response)
            fh.close()
            et2 = datetime.datetime.now()
            time_elapsed = (et2 - et1) + (et1 - st1)
            ns = time_elapsed.microseconds * pow(10,-3)
            file_size = os.path.getsize(file_path)
            print time_elapsed.microseconds
            bandwidth = ((file_size * pow(10,3)) / time_elapsed.microseconds)
            print '\nFile Transfer complete:'
            print 'Size of file transmitted: %d bytes' % file_size
            print 'Time Elapsed: %f nano seconds' % ns
            print 'Calculated Bandwidth from file transfer %f MegaBytes/Sec' % bandwidth
            print '*'*80

        except Exception as e:
            print 'File Transfer failed, check you connection parameters.'
            print e.message
            print '*'*80
            return

        finally:    
            connection.close()        

    def peer_stats(self):
        print '*'*80
        print 'Peer Host: localhost'
        print 'Peer Port: %d' % self.credentials
        print '*'*80

if __name__ == '__main__':

    print '*'*80

    try:
        qi = query_indexer()    
    except Exception as e:
        print 'Failed to import query package.!'
        print '*'*80
        sys.exit(1) 

    credentials = qi.get_credentials()

    if credentials == 'error':
        print 'Central Indexing Server is not running.!!, Please start that first'
        print '*'*80
        sys.exit(1)

    try:
        server = server_class(credentials) 
        server.setDaemon(True)
        server.start()
    except Exception as e:
        print 'Peer Server Could not be started.'
        print e.message
        print '*'*80
        sys.exit(1)

    try:
        fs_handler = FilesystemEventHandler(OUTPUT_DIR,credentials)
        fs_handler.setDaemon(True)
        fs_handler.start()
    except Exception as e:
        print 'File system monitor could not be started.'
        print e.message
        print '*'*80
        sys.exit(1)  

    print 'Central Indexing Server is running on port  : 3000'
    print 'This Peer Server is running on port         : %d' % credentials
    print 'Both Central Server and Peer are running on : localhost'    

    try:
        possibilities = [1,2,3,4]
        print '*'*80
        while 1:
            time.sleep(1)
            print '\nEnter your choice.\n'
            print '1 -  List all the files that are indexed in the Centralized Server.'
            print '2 -  Search the file (Returns peer-id and file size)'
            print '3 -  Get file from peers (Requires file name and peer-id)'
            print '4 -  Current peer statistics\n'
            print 'Press cntrl+c to exit.\n'
            command = raw_input()
            if int(command) not in possibilities:
                print 'Invalid choice entered, please select again\n'
                continue
            print '*'*80    
            print 'Choice selected: %d \n' % int(command)

            if int(command) == 3:
                print 'Enter Peer Id:\n'
                peer_transfer_id = raw_input()
                print 'Enter File name:'
                file_name = raw_input()
                file_name = file_name.lower()
                qi.obtain(peer_transfer_id,file_name)

            elif int(command) == 1:
                qi.list_all_files()

            elif int(command) == 2:
                print 'Enter File name:'
                file_name = raw_input()
                file_name = file_name.lower()
                qi.search_for_file(file_name)    

            elif int(command) == 4:
                qi.peer_stats()
                    

    except Exception as e:
        print e.message
    except KeyboardInterrupt:
        destroy_peer(int(credentials))
        print '*'*78
        print '\nKeyboard Interrupt Caught.!'
        print 'Shutting Down Peer Server..!!!'
        print '*'*80
        time.sleep(1)
        sys.exit(1)

    finally:
        server.close()   
