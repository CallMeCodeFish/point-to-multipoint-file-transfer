import socket
import struct
from threading import Thread, Lock
from time import sleep, time


STOP_FLAG = False
SEQ_HOSTACK_MAP = {}
COUNTDOWN = 0
SEQNUM = 0
FILESOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ENDFLAG = False
HOST_ACK_TIME = {}

lock_sock = Lock()
lock_map = Lock()
lock_count = Lock()
lock_stop = Lock()
lock_ack_time = Lock()


def rdt_send(host_list, p, send_bytes, n, mss, to_value):
    global STOP_FLAG, COUNTDOWN, SEQNUM, SEQ_HOSTACK_MAP
    # 更新SEQNUM与清空重置MAP
    lock_map.acquire()
    SEQNUM = n*mss
    for rcvr in host_list:
        SEQ_HOSTACK_MAP[rcvr] = False
    lock_map.release()

    # initialize host-segment send time dict
    host_sendtime_dict = {}

    lock_stop.acquire()
    STOP_FLAG = False
    lock_stop.release()
    seq_num = (mss*n).to_bytes(4, "big", signed = False)
    checksum = generate_checksum(send_bytes)
    data_indicator = struct.pack('!H', int('0101010101010101', 2))
    segment_bytes = bytes()
    segment_bytes += seq_num
    segment_bytes += checksum
    segment_bytes += data_indicator
    segment_bytes += send_bytes

    resend = True
    # print(host_list)

    # 首次发送与每隔一个timeout进行重发
    while True:
        # 根据是否收到ACK进行发送
        for rcvr in host_list:
            lock_map.acquire()
            if SEQ_HOSTACK_MAP[rcvr] == False:   #locklocklock
                host_sendtime_dict[rcvr] = round(time(), 3)
                FILESOCKET.sendto(segment_bytes, (rcvr, p))   #locklocklock

            lock_map.release()
        countdown_thread = Thread(target=__countdown, args=[to_value])
        countdown_thread.start()
        #print("计时器", COUNTDOWN)
        resend = True
        lock_count.acquire()
        test_flag = COUNTDOWN
        lock_count.release()
        while test_flag > 0:   #locklocklock
            all_ack = True
            lock_map.acquire()
            for h in SEQ_HOSTACK_MAP.keys():
                if SEQ_HOSTACK_MAP[h] == False:   #locklocklock
                    all_ack = False
                    break
            lock_map.release()
            if all_ack:

                resend = False
                break
            lock_count.acquire()
            test_flag = COUNTDOWN
            lock_count.release()


        if resend:
            print("Timeout, sequence number = ", mss*n)
        else:
            break
    lock_stop.acquire()
    STOP_FLAG = True
    lock_stop.release()
    countdown_thread.join()
    host_rtt_dict = {}
    for rcvr in host_list:
        lock_ack_time.acquire()
        host_rtt_dict[rcvr] = HOST_ACK_TIME[rcvr] - host_sendtime_dict[rcvr]
        lock_ack_time.release()
    return host_rtt_dict


def generate_checksum(contents):
    sum = 0b0
    if 0 != len(contents) % 2:
        contents = contents + (0).to_bytes(1, "big", signed = False)
    for i in range(0, len(contents), 2):
        twoBytes = contents[i:i + 2]
        test_int = int.from_bytes(twoBytes, "big", signed = False)
        sum += test_int
        if sum >= 0b10000000000000000:
            sum %= 0b10000000000000000
            sum += 0b1
    sum_str = bin(sum)[2:]
    if len(sum_str) < 16:
        sum_str = "0" * (16 - len(sum_str)) + sum_str
    result = ''
    for i in range(len(sum_str)):
        if "0" == sum_str[i]:
            result += "1"
        else:
            result += "0"
    checksum_int = int(result, 2)
    checksum = (checksum_int).to_bytes(2, "big", signed=False)
    return checksum


def __countdown(timeout):
    while 0 <= timeout:
        global COUNTDOWN
        global STOP_FLAG
        lock_count.acquire()
        COUNTDOWN = timeout
        lock_count.release()
        lock_stop.acquire()
        if STOP_FLAG == True:
            lock_stop.release()
            break
        lock_stop.release()

        timeout -= 0.01
        sleep(0.01)
    lock_count.acquire()
    COUNTDOWN = timeout
    lock_count.release()


def receive_ack():
    try:
        while True:
            ack, addr = FILESOCKET.recvfrom(8)
            processThread = Thread(target=__process_ack, args=[ack, addr])
            processThread.start()
    except OSError:
        print("File Send Finish")
    finally:
        return


def __process_ack(a, b):
    global SEQNUM, SEQ_HOSTACK_MAP, HOST_ACK_TIME
    ack_num = int.from_bytes(a[0:4], 'big', signed=False)
    lock_map.acquire()
    if SEQNUM == ack_num:
        lock_ack_time.acquire()
        HOST_ACK_TIME[b[0]] = round(time(), 3)
        lock_ack_time.release()
        SEQ_HOSTACK_MAP[b[0]] = True
    lock_map.release()
    return
