from wifi_communication import wifi_communication
from bluetooth_communication import bluetooth_communication
from stm_communication import stm_communication
import picam
from PIL import Image
import image_handling
import config
import queue
import threading
import select
import time


class rpi_manager:
    def __init__(self):
        self.turn_number = 0
        self.prev_turn = None
        self.photo_event = threading.Event()
        self.to_android = queue.Queue()
        self.to_STM = queue.Queue()
        self.to_wifi = queue.Queue()
        self.bluetooth_socket = bluetooth_communication(
            config.bluetooth_uuid,
            config.bluetooth_socket_buffer_size,
            config.terminating_str,
        )
        self.wifi_recv_socket = wifi_communication(
            config.socket_buffer_size, config.terminating_str
        )
        self.wifi_send_socket = wifi_communication(
            config.socket_buffer_size, config.terminating_str
        )
        self.stm_socket = stm_communication(
            config.serial_port, config.baud_rate, config.STM_buffer_size
        )

    def prestart(self):
        self.bluetooth_socket.advertise_and_accept_connection(
            config.bluetooth_host, config.bluetooth_port
        )
        self.wifi_send_socket.accept_connection(
            config.socket_rpi_ip, config.socket_sending_port
        )  # 8080
        self.wifi_recv_socket.accept_connection(
            config.socket_rpi_ip, config.socket_receiving_port
        )  # 8081
        self.stm_socket.connect_STM()

        while True:
            message = self.bluetooth_socket.receive_message()
            message = b"BANANAS"
            if message.startswith(b"BANANAS"):
                #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test_1.jpg")))
                image = image_handling.np_array_to_bytes(picam.take_picture())
                self.to_wifi.put(b"preimage:"+image)
                self.to_STM.put(b"c:SENSOR30,c:END00000,c:TAKEPIC")
                print("[RPi] BANANAS")
                break
        return

    def read_wifi(self):
        while True:
            # listen to socket
            receiving, _, _ = select.select([self.wifi_recv_socket.socket], [], [])
            if not self.photo_event.is_set() and receiving:
                message = self.wifi_recv_socket.receive_message()
                # to get instructions from algorithm
                if message.startswith(b"c:"):
                    instructions = message.split(b"c:")
                    for instruction in instructions:
                        instruction = instruction.removeprefix(b"c:")
                        self.to_STM.put(instruction)
            else:
                continue

    def write_wifi(self):
        while True:
            if not self.photo_event.is_set():
                try:
                    if not self.to_wifi.empty():
                        message = self.to_wifi.get()
                        self.wifi_send_socket.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Algo/Img Det: {}".format(str(e)))
            else:
                continue

    def write_STM(self):
        while True:
            if not self.photo_event.is_set():
                try:
                    if not self.to_STM.empty():
                        STM_data = self.to_STM.get()
                        if STM_data.startswith(b"c:"):
                            instructions = STM_data.split(b"c:")
                            for instruction in instructions:
                                instruction = instruction.removeprefix(b"c:")
                                instruction = instruction.removesuffix(b",")
                                if instruction.startswith(b"TAKEPIC"):
                                    print("[RPi] Entering Phototaking Event")
                                    self.photo_event.set()
                                elif len(instruction) == config.STM_buffer_size:
                                    print(instruction)
                                    self.stm_socket.write_to_STM(instruction)           
                except Exception as e:
                    print("[RPi] Could Not Send to STM: {}".format(str(e)))
            else:
                continue

    def take_picture(self):
        while True:
            self.photo_event.wait()
            print("[TAKEPIC] Inside Event")
            STM_msg = self.stm_socket.read_from_STM()
            if STM_msg == b"STOP0000":
                retry = True
                print("[TAKEPIC] STM Stopped")
                if self.turn_number == 0:
                    self.wifi_send_socket.send_message(b"FINDOBS:"+str(self.turn_number).encode())
                    print("[TAKEPIC] First Turn, Receiving Classes From Image Taken at Start Point")
                    classes = self.wifi_recv_socket.receive_message()
                else:
                    print("[TAKEPIC] Taking Picture")
                    #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test_3.jpg")))
                    image = image_handling.np_array_to_bytes(picam.take_picture())
                    self.wifi_send_socket.send_message(b"image:"+image)
                    print("[TAKEPIC] Receiving Classes")
                    classes = self.wifi_recv_socket.receive_message()

                while classes:
                    raw_classes = classes.removeprefix(b"classes:")
                    raw_classes = raw_classes.split(b",")
                    match = False
                    tries = 2
                    for i in range(0, len(raw_classes)):
                        if raw_classes[i] == b"41":
                            continue
                        elif raw_classes[i] == b"38":
                            print("[TAKEPIC] Found Class 38")
                            if self.turn_number == 0:
                                STM_input = config.path1fast[0]
                            else:
                                STM_input = config.path2fast[0]
                            self.to_STM.put(STM_input)
                            self.turn_number += 1
                            match = True
                            classes = None
                            break
                        elif raw_classes[i] == b"39":
                            print("[TAKEPIC] Found Class 39")
                            if self.turn_number == 0:
                                STM_input = config.path1fast[1]
                            else:
                                STM_input = config.path2fast[1]
                            self.to_STM.put(STM_input)
                            self.turn_number += 1
                            match = True
                            classes = None
                            break
                    if not match:
                        print("[TAKEPIC] Retry")
                        if retry and self.turn_number == 0:
                            print("[TAKEPIC] Retaking Image")
                            #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test_3.jpg")))
                            image = image_handling.np_array_to_bytes(picam.take_picture())
                            self.wifi_send_socket.send_message(b"image:"+image)
                            print("[TAKEPIC] Receiving Messages")
                            classes = self.wifi_recv_socket.receive_message()
                        elif retry:
                            print("[TAKEPIC] STM Adjusting")
                            self.stm_socket.write_to_STM(b"FALSE000")
                            self.stm_socket.write_to_STM(b"END00000")
                            STM_msg = self.stm_socket.read_from_STM()
                            # STM_msg == b"STOP0000"
                            if STM_msg == b"STOP0000":
                                print("[TAKEPIC] Retaking Image")
                                #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test_2.jpg")))
                                image = image_handling.np_array_to_bytes(picam.take_picture())
                                self.wifi_send_socket.send_message(b"image:"+image)
                                print("[TAKEPIC] Receiving Messages")
                                classes = self.wifi_recv_socket.receive_message()
                            retry = False
                        elif not retry:
                            classes = None
                self.photo_event.clear()
        return


r = rpi_manager()
r.prestart()
read_wifi_thread = threading.Thread(target=r.read_wifi)
# android_communication_thread = threading.Thread(target = android_communication)
write_wifi_thread = threading.Thread(target=r.write_wifi)
# read_android_thread  = threading.Thread(target= r.write_android)
write_STM_thread = threading.Thread(target=r.write_STM)
take_picture_thread = threading.Thread(target=r.take_picture)

read_wifi_thread.start()
# android_communication_thread.start()
write_wifi_thread.start()
# read_android_thread.start()
write_STM_thread.start()
take_picture_thread.start()
