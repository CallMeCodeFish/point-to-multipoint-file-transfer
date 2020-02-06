#!usr/bin/python3
# -*- coding: utf-8 -*-
'''
# Created on Oct-16-19 19:57
# server_functions.py
# theme: 
# @author: Heng Yu
'''
import sys


def is_wrong_checksum(segment):
    checkSum = segment[4:6]
    contents = segment[8:]
    if len(contents) % 2 != 0:
        contents += (0).to_bytes(1, "big", signed = False)
    sum = int.from_bytes(checkSum, "big", signed = False)
    for i in range(0, len(contents), 2):
        twoBytes = contents[i:i+2]
        sum += int.from_bytes(twoBytes, "big", signed = False)
        if sum >= 0b10000000000000000:
            sum %= 0b10000000000000000
            sum += 0b1
    return 0b1111111111111111 != sum


def is_wrong_segment(segment, ackNumber, mss):
    sequenceNumber = segment[:4]
    ackNumber += mss
    return (ackNumber).to_bytes(4, "big", signed = False) != sequenceNumber


#input: bytes, output: bytes
def parse_segment_for_contents(segment):
    return segment[8:]


#input: int, output: bytes
def generate_ack(ackNumber):
    ack = (ackNumber).to_bytes(4, "big", signed = False)
    ack += (0).to_bytes(2, "big", signed = False)
    indication = int (0b0101010101010101)
    ack += (indication).to_bytes(2, "big", signed = False)
    return ack


#input: bytes, output: int
def get_new_ack_number(segment):
    sequenceNumber = segment[:4]
    return int.from_bytes(sequenceNumber, "big", signed = False)




if __name__ == "__main__":
    #test is_wrong_segment(segment, ackNumber, mss)
    # segment = (0).to_bytes(4, "big")
    # print(segment)
    # ackNumber = 0
    # mss = 0
    # print(is_wrong_segment(segment, ackNumber, mss))

    #test generate_ack(ackNumber)
    ackNumber = 100
    ack = generate_ack(ackNumber)
    print(ack) #bytes
    print(len(ack))
    print(int.from_bytes(ack[:4], "big"))
    # print(int.from_bytes(ack[4:6], "big"))
    # print(bin(int.from_bytes(ack[6:], "big")))
    print((100).to_bytes(4, "big"))
    print("hello, world".encode())