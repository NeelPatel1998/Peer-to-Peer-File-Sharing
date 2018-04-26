Centralised Peer to Peer System
=======================================================================================================
**Requirements:**

- Linux system with python installed.
- Python version should be equal or greater than 2.6.
- You can check this just be typing python in the terminal (assuming python is already installed).

*Note:* Please refer to the design document for detailed explaination of the architecture.

*******************************************************************************************************

**Package:**

There are two main components in the packege:

1. Indexing Server (indexing_server.py)
2. Peer (peer)

*Indexing Server:*

- Manages peer registration.
- Manages file index.
- Manages Client requests for searching index.
- Manages Peer list in the network that are connected to the server.

*Peer:*
	
Peer has three sub components components:

1) 	Peer (peer.py)
- Serves as client for users using the peer.
- Gives option for Listing and Searching files from the Central Indexing Server.
- Initiates connection to Central server and registers to the network.
- Starts the peer server which will serve other peers (This is Daemonized).
- Starts the file system handler, which updates Central Server about the files it has.
- Initates file transfer upon client request.

2)  File System EventHandler (FilesystemEventHandler.py)
- This is a daemon thread that is spawned by the peer thread.
- This constantly monitors the allocated directory for file updates (Addtion and Deletion).
- Upon any such event, it automatically updates the changes to the Central Indexing server.

3) 	Peer Server	(server.py)
- This is also a daemon server, this runs on the port which the Central Server allocates.
- This will listen to any peer requests and initiates file transfer.
			
*******************************************************************************************************
*Note:* The 'Files' folder inside directory is used as the input and outpu directory for file transfer. 
      So, please use this directory to place your test files.                                         
*******************************************************************************************************
     

=======================================================================================================
**Usage:**

Steps to start the file transfer process:

1. Start the Central Indexing Server.

   > python indexing_server.py

2. Depending on the requirement, open n number of terminals (here n = 3).
3. Depending on the number of peers, go into the peer(x) directory using terminal (x = 1,2,3).
4. Place all the initial files into the 'Files' directory.
5. Launch peers inside the peer directory.
 
   > python peer.py

6. Follow the promts in the terminal.

*******************************************************************************************************



    
