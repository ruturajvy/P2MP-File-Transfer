#Point to Multi-point File Transfer

The solution contains two python scripts, one that runs at the client and the other at all the servers. This simulates the file transfer from a single source that is the client to multiple servers.

No. of Files: 2

OS: Windows

###Instructions:

1. Paste the p2mpserver.py or p2mpclient.py in a directory of choice.

2. In order to run the server program, open a command prompt or PowerShell and type in the command that is of the following format.
```
python p2mpserver.py <server_port> <file_name> <loss_probability>
```
3. In order to run the client program, open a command prompt or PowerShell and type in the command that is of the following format.
```
python p2mpserver.py <server_ip(s)> <server_port> <file_name> <MSS_value> 
```

NOTE: Start the server(s) before starting the client to accurately measure delays.

###Client Algorithm:

The client uses an iterative method to read MSS bytes of data from the file and sends it to all the
servers back to back after the specified encapsulation of the sequence number, checksum and data
packet indicator is appended.
The client then executes a while loop to receive acknowledgements from every server. The socket
timeout value is set to be 1 second. 
After receiving an acknowledgement, the client removes that
server from a list of servers which haven’t sent an acknowledgement, that is maintained on a per-
segment basis. 
This list contains all the servers’ IP addresses for every MSS iteration and
decremented until it becomes empty. 
Once it becomes empty, the client moves on to the next MSS
bytes and repeats the entire process.
If timeout occurs, the client code raises a socket timeout exception which then leads to the the
client iteratively resending that segment to all servers that are left in the unacknowledged server
list and the process repeats.
The socket.setimeout() value is dynamically changed after each server acknowledgement is
received. The value is decremented by the time difference between the time just after sending MSS
bytes and the time of the last acknowledgement. In this way the cumulative timeout for all server
remains equal to the initial timeout value set.

###Server Algorithm:

The server opens a file in write binary mode and runs a loop to receive the data packet using the
recvfrom method. 
It uses the loss_service() method uses the given loss probability to toggle a flag,
which determines if the packet has to be processed, that in turn, toggles the call to the
check_packet() method. 
The check_packet() method is responsible for decapsulating the packet,
verifying its checksum and sequence number and if the packet is not in error, it calls the
server_reply_write() method to construct and send an acknowledgement. 
This method also takes
the file pointer as an argument and writes the data portion of the received segment into the file
after sending the acknowledgement.