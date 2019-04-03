import os
import socket
import time
from threading import Timer
import binascii
import sys

#**************************************************************************************************************************************************************************

def time_out():
    global timeout
    timeout = 1
    return

#**********************************************************************************************************************************************************************

def carry_add(word1, word2):
    result = word1 + word2
    return (result & 0xffff) + (result >> 16)

#**********************************************************************************************************************************************************************

def checksum(data):
    checksum_local = 0
    if (len(data) % 2) == 0:
        for i in range(0, len(data), 2):
            word = ord(data[i]) + (ord(data[i+1]) << 8)
            checksum_local = carry_add(checksum_local, word)
    else:
        for i in range(0, len(data)-1, 2):
            word = ord(data[i]) + (ord(data[i+1]) << 8)
            checksum_local = carry_add(checksum_local, word)
        word = ord(data[len(data)-1]) + (ord(' ') << 8)
        checksum_local = carry_add(checksum_local, word)
    checksum_local = ~checksum_local & 0xffff
    return bin(checksum_local).lstrip('0b').zfill(16)

#**********************************************************************************************************************************************************************

def make_segment(data,seq_no):
    sep = '###' 
    segment = seq_no + sep + checksum(data) + sep + '0101010101010101' + sep +  data
    return segment

#**********************************************************************************************************************************************************************

timeout = 0
print(sys.argv)
sep = '###'
client_ip = '127.0.0.1'
n = len(sys.argv)-3
filename = sys.argv[n+1]
MSS = int(sys.argv[n+2])
server_port = int(sys.argv[n])
server_ip_list = sys.argv[1:n]
server_not_acked = []
for server in server_ip_list:
    server_not_acked.append(server)
bytesToSend = []

if os.path.isfile(filename):
    print 'File is present'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Created the socket'
    with open(filename, mode = 'rb') as f:
        sequence_number = 0
        bytesToSend = '.'
        log_time_first = time.clock()
        print "*******************************************************"
        print "Starting File Transfer"
        print "*******************************************************"
        while bytesToSend != "":                                                             #Iterate of the file reading MSS bytes each time
            server_ip_list = sys.argv[1:n]
            bytesToSend = f.read(MSS)
            client_socket.settimeout(1)
            seq_no = '{0:032b}'.format(sequence_number)                                     #32 bit binary sequence number from an integer
            for server_ip in server_ip_list:                                                #Send each MSS bytes to all servers back to back
                segment = make_segment(bytesToSend, seq_no)                              #Make segment by passing the sequence number to attach and the data
                client_socket.sendto(segment,(server_ip, server_port))
            initial_time = time.clock()
            server_not_acked = server_ip_list                                               #Send the created segment

            while len(server_not_acked) != 0:
                try:
                    acknowledgement, ServerAddress = client_socket.recvfrom(1024)           #Receive the acknowledgment, next line is triggered as soon as any server responds. Store ACK and server IP
                    present_time = time.clock()
                    sock_timeout = 1 - (present_time - initial_time)
                    client_socket.settimeout(sock_timeout)
                    ack = acknowledgement.split(sep)                                            #Split the ACK and check if it is correct
                    if ack[0] != seq_no or ack[1] != '0000000000000000' or ack[2]!= '1010101010101010':
                        continue
                    server_not_acked.remove(ServerAddress[0])
                except socket.timeout:
                    for server_addr in server_not_acked:                                        #Resend the segment to those who are in server_not_acked if socket timed out.
                        client_socket.sendto(segment, (server_addr, server_port))
                        print "Time out, Sequence Number:",sequence_number," from:",server_addr
                    initial_time = time.clock()
            sequence_number += len(bytesToSend)                                                             #Increment the sequence number by MSS(in binary)
            
        log_time_last = time.clock()
        print "********************************************************"
        print "File Transfer complete in :",log_time_last - log_time_first
        print "*********************************************************"
        client_socket.close()
        
else:
    print('File not found')    
