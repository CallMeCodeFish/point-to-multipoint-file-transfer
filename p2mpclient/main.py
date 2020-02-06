import sys
import struct
from threading import Thread
from time import time
from .utils import rdt_send, receive_ack, generate_checksum, FILESOCKET, ENDFLAG


def main():
    mss = int(sys.argv[-1])
    file_name = sys.argv[-2]
    port_num = int(sys.argv[-3])
    in_file = open(file_name, 'rb')
    turn_num = 0

    host_rtt_dict = {}
    for ip in sys.argv[1:-3]:
        host_rtt_dict[ip] = 0.000

    # 接收线程开启
    recv_thread = Thread(target=receive_ack)
    recv_thread.start()
    start_time = time()
    while True:
        send_bytes = in_file.read(mss)
        if len(send_bytes) == 0:    #结束条件: n + 1
            break
        #print(sys.argv[1:2])
        # print(turn_num)
        d = rdt_send(sys.argv[1:-3], port_num, send_bytes, turn_num, mss, 0.08)
        for k in d:
            host_rtt_dict[k] += d[k]
        turn_num += 1

        # if len(send_bytes) < mss:
        #     global

    # 文件发送完成
    rdt_send(sys.argv[1:-3], port_num, b'', turn_num, mss, 0.08)
    end_time = time()
    t_delay = round(end_time-start_time, 3)
    record_f = open('./record_p_0.10', 'a')
    record_f.write(str(t_delay))
    record_f.close()
    rtt_f = open('./rtt_p_0.10', 'a')
    for k in host_rtt_dict:
        rtt_f.write(k+': '+str(host_rtt_dict[k]/float(turn_num-1))+'\n')
    rtt_f.close()
    FILESOCKET.close()
    in_file.close()

    return
