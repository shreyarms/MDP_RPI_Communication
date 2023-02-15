from wifi_communication import wifi_communication
from bluetooth_communication import bluetooth_communication
from stm_communication import stm_communication
from PIL import Image
import picam
import image_handling
import config
import queue
import threading


b_send = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
b_send.advertise_and_accept_connection(config.bluetooth_host, config.bluetooth_sending_port)

b_recv = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
b_recv.advertise_and_accept_connection(config.bluetooth_host, config.bluetooth_receiving_port)

w_send = wifi_communication(config.socket_buffer_size,config.terminating_str)
w_send.accept_connection(config.socket_rpi_ip, config.socket_sending_port) #8080

w_recv = wifi_communication(config.socket_buffer_size,config.terminating_str)
w_recv.accept_connection(config.socket_rpi_ip, config.socket_receiving_port) #8081

s = stm_communication(config.serial_port,config.baud_rate,config.STM_buffer_size)
s.connect_STM()

to_android = queue.Queue()
to_STM = queue.Queue()
android_to_STM = queue.Queue()
to_wifi = queue.Queue()

send_to_wifi = True
read_from_wifi = True
send_to_android = True
read_from_android = True
send_to_STM = True

def read_wifi():
    while True:
        if read_from_wifi:
            message = w_recv.receive_message()
            if message.startswith(b"C:"):
                coordinate_array = message.split(config.sep_str)
                for coordinate in coordinate_array:
                    to_STM.put(coordinate)
        else:
            continue
        
def write_wifi():
    while True:
        if send_to_wifi:
            try: 
                if not to_wifi.empty():
                    message = to_wifi.get()
                    w_send.send_message(message)
            except Exception as e:
                print("[RPi] Could Not Send to Algo/Img Det: {}".format(str(e)))
        else:
            continue

def read_android():
    while True:
        if read_from_android:
            message = b_recv.receive_message()
            if message.startswith(b"bc:"):
                to_wifi.put(message)
            elif message.startswith(b"A2STM:"):
                coordinate = message.removeprefix(b"A2STM:")
                android_to_STM.put(coordinate)
        else:
            continue

def write_android():
    while True:
        if write_android:
            try: 
                if not to_android.empty():
                    message = to_android.get()
                    print("Bluetooth:{}".format(message))
                    b_send.send_message(message)
            except Exception as e:
                print("[RPi] Could Not Send to Android: {}".format(str(e)))
        else:
            continue

def write_STM():
    while True:
        if send_to_STM:
            try: 
                if not to_STM.empty():
                    message = to_STM.get()
                    data_array = message.split(b'&')
                    STM_data = data_array[0]
                    bluetooth_data = data_array[1]
                    STM_data = STM_data.removeprefix(b'C:')
                    if(STM_data == b"TAKEPIC"):
                        take_picture()
                    else:
                        if len(STM_data) == config.STM_buffer_size:
                            print("STM : {}".format(STM_data))
                            s.send_message(STM_data)
                            b_send.send_message(bluetooth_data)
            except Exception as e:
                print("[RPi] Could Not Send to STM: {}".format(str(e)))
        else:
            continue

def take_picture():
    send_to_wifi = False
    read_from_wifi = False
    send_to_android = False
    read_from_android = False
    send_to_STM = False
    STM_msg = s.read_from_STM()
    if STM_msg == b"STOP0000":
        print("Taking Picture")
        #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test.jpg")))
        image = image_handling.np_array_to_bytes(picam.take_picture())
        w_send.send_message(b"image:"+image)
        classes = w_recv.receive_message()
        b_send.send_message(classes)
        w_send.send_message(b"Algo:Next Path")
    send_to_wifi = True
    read_from_wifi = True
    send_to_android = True
    read_from_android = True
    send_to_STM = True



read_wifi_thread = threading.Thread(target = read_wifi)
#write_wifi_thread = threading.Thread(target = write_wifi)
#take_picture = threading.Thread(target = take_picture, daemon = True)
#write_android_thread  = threading.Thread(target= write_android)
write_STM_thread= threading.Thread(target= write_STM)

read_wifi_thread.start()
#write_wifi_thread.start()
#write_android_thread.start()
write_STM_thread.start()