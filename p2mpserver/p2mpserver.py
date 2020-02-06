#!usr/bin/python3
# -*- coding: utf-8 -*-
'''
# Created on Oct-16-19 17:02
# p2mpserver.py
# theme: 
# @author: Heng Yu
'''


import sys
from socket import *
import random
from .server_functions import *


def main():
    if 4 != len(sys.argv):
        print("Error: 3 arguments expected, %d given.\nExit with 1." % len(sys.argv))
        sys.exit(1)

    #deal with input exception
    try:
        port = int(sys.argv[1])
        if port > 65535 or port < 1024:
            raise ValueError
    except ValueError as e:
        print("Error: Port number must be an integer and in the range from 1024 to 65535.\nExit with 1.")
        sys.exit(1)


    fileName_array = sys.argv[2].split('.')
    if 1 == len(fileName_array) or (2 == len(fileName_array) and "pdf" == fileName_array[1].lower()):
        fileName = fileName_array[0].lower()
    else:
        print("Error: File name invalid. It must be <fileName> or <fileName.pdf>.\nExit with 1.")
        sys.exit(1)

    try:
        lossProbability = float(sys.argv[3])
        if lossProbability > 1 or lossProbability < 0:
            raise ValueError
    except ValueError as e:
        print("Error: Probability must be a float number and in the range from 0 to 1\nExit with 1.")
        sys.exit(1)


    #open file
    try:
        file =open("%s.pdf" %fileName, "wb")
    except:
        print("Error: File cannot be opened.")


    #open up a UDP socket as a server
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", port))
    # print("start running...")

    mss = 0 #used for judging whether it is the last segment to receive
    ackNumber = 0
    while True: #loop for receiving whole contents of the file
        # print("\n\nWaiting for incoming segment...")
        segment, addr = serverSocket.recvfrom(10240)
        # print("A segment is received.")
        test_sq = int.from_bytes(segment[:4], "big", signed = False)
        # print("Sequence number: ", test_sq)
        
        #judge whether the segment is "lost": no other actions
        random.seed()
        if random.random() <= lossProbability:
            print("Packet loss, sequence number = %d" % test_sq)
            continue

        #check the checksum: no other actions
        if is_wrong_checksum(segment):
            # print("Wrong checksum. The segment has been discarded.")
            continue

        #check the sequence number to judge whether it is the segment desired
        if is_wrong_segment(segment, ackNumber, mss):
            ack = generate_ack(ackNumber)
            serverSocket.sendto(ack, addr)
            # print("Dupilicate packet.")
            continue
        
        #everything is correct
        # print("Everythin is correct.")
        contents = parse_segment_for_contents(segment)
        # print("Length of the segment: ", len(contents))


        if mss == 0: #the first segment
            # print("The first segment is received.")
            mss = len(contents)

        #FIN
        if 0 == len(contents):
            # print("FIN has been received.")
            break

        file.write(contents)
        # print("The segment has been written into the file.")

        ackNumber = get_new_ack_number(segment)
        ack = generate_ack(ackNumber)   #ack: bytes
        serverSocket.sendto(ack, addr)
        # print("ACK has been sent: ", ackNumber)
        
    #close socket
    serverSocket.close()
    # print("The socket has been closed.")

    #close file
    file.close()
    # print("The file has been closed.\nProcess finished!")
