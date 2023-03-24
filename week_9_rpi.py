from wifi_communication import wifi_communication
from bluetooth_communication import bluetooth_communication
from stm_communication import stm_communication
import picam
from PIL import Image # for testing without an RPi
import image_handling
import config
import queue
import threading
import select
import time

class rpi_manager:
    def __init__(self):
        # declare turn number and previous turn value for determining which path to take 
        self.turn_number = 0
        self.prev_turn = None
        # declare a threading event called photo event, which causes all the other threads to wait until the take_picture function finishes 
        self.photo_event = threading.Event()
        # declare three empty message queues 
        self.to_android = queue.Queue()
        self.to_STM = queue.Queue()
        self.to_wifi = queue.Queue()
        # initialise connection socket objects 
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
        # connect each connection socket object
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

        # Sending of the START Command, which is BANANAS in our case 
        while True:
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"BANANAS"):
                #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open(image_queue.pop(0))))
                image = image_handling.np_array_to_bytes(picam.take_picture())
                # take a picture immediately after starting and put it in the to_wifi queue
                self.to_wifi.put(b"preimage:"+image)
                self.to_STM.put(b"c:START000,c:END00000,c:TAKEPIC")
                print("[RPi] BANANAS")
                break
        return

    def read_wifi(self):
        while True:
            #listen to socket to see if it is receiving something 
            receiving, _, _ = select.select([self.wifi_recv_socket.socket], [], [])
            # checks the photo_event flag and only receives messages if flag is not set  
            if not self.photo_event.is_set() and receiving:
                message = self.wifi_recv_socket.receive_message()
                # to get instructions from algorithm (not used)
                if message.startswith(b"c:"):
                    instructions = message.split(b"c:")
                    for instruction in instructions:
                        instruction = instruction.removeprefix(b"c:")
                        self.to_STM.put(instruction)
            else:
                continue

    def write_wifi(self):
        while True:
            # checks the photo_event flag and only writes messages if flag is not set 
            if not self.photo_event.is_set():
                try:
                    if not self.to_wifi.empty():
                        # get data from to_wifi queue and send the message 
                        message = self.to_wifi.get()
                        self.wifi_send_socket.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Algo/Img Det: {}".format(str(e)))
            else:
                continue

    def write_STM(self):
        while True:
            # checks the photo_event flag and only writes messages if flag is not set 
            if not self.photo_event.is_set():
                try:
                    if not self.to_STM.empty():
                        # get data from the to_STM queue
                        STM_data = self.to_STM.get()
                        # if message conatins instruction starting with c:, split the instructions and send one by one to STM
                        if STM_data.startswith(b"c:"):
                            instructions = STM_data.split(b"c:")
                            for instruction in instructions:
                                instruction = instruction.removeprefix(b"c:")
                                instruction = instruction.removesuffix(b",")
                                # if message is TAKEPIC, set photo_event flag, which cause other threads to wait until the take_picture function executes 
                                if instruction.startswith(b"TAKEPIC"):
                                    print("[RPi] Entering Phototaking Event")
                                    self.photo_event.set()
                                elif len(instruction) == config.STM_buffer_size:
                                    print("[RPI] {}".format(instruction))
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
            # receive message from STM that the robot has stopped 
            if STM_msg == b"STOP0000":
                retry = 2
                print("[TAKEPIC] STM Stopped")
                # if it is the first turn, ask the wifi_device if it has any detected classes from the picture taken at the start 
                if self.turn_number == 0:
                    self.wifi_send_socket.send_message(b"FINDOBS:"+str(self.turn_number).encode())
                    print("[TAKEPIC] Receiving Classes From Image Taken at Start Point")
                    classes = self.wifi_recv_socket.receive_message()
                
                # if not, take a picture and send to the wifi device 
                else:
                    print("[TAKEPIC] Taking Picture")
                    #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open(image_queue.pop(0))))
                    image = image_handling.np_array_to_bytes(picam.take_picture())
                    self.wifi_send_socket.send_message(b"image:"+image)
                    print("[TAKEPIC] Receiving Classes")
                    classes = self.wifi_recv_socket.receive_message()

                # both cases return an array of classes sorted by arrows, which can checked for arrows 
                while classes:
                    raw_classes = classes.removeprefix(b"classes:")
                    raw_classes = raw_classes.split(b",")
                    match = False
                    for i in range(0, len(raw_classes)):
                        # if class is a target, continue
                        if raw_classes[i] == b"41":
                            continue
                        # if class is right, then turn right 
                        elif raw_classes[i] == b"38":
                            print("[TAKEPIC] Found Class 38")
                            # check turn number to send the correct path as the instructions differ for each turn
                            if self.turn_number == 0:
                                STM_input = config.path1fast[0]
                            else:
                                STM_input = config.path2fast[0]
                            # put new oath in the to_STM queue, increase turn number by 1, and set match to True  
                            self.to_STM.put(STM_input)
                            self.turn_number += 1
                            match = True
                            classes = None
                            break
                        # if class is left, turn left 
                        elif raw_classes[i] == b"39":
                            print("[TAKEPIC] Found Class 39")
                            # check turn number to send the correct path as the instructions differ for each turn
                            if self.turn_number == 0:
                                STM_input = config.path1fast[1]
                            else:
                                STM_input = config.path2fast[1]
                            # put new oath in the to_STM queue, increase turn number by 1, and set match to True
                            self.to_STM.put(STM_input)
                            self.turn_number += 1
                            match = True
                            classes = None
                            break
                    # Retry Condition
                    if not match:
                        print("[TAKEPIC] Retry")
                        # if no picture was detected in the picture taken from the start, take a picture without adjusting the position of the robot 
                        if retry == 2 and self.turn_number == 0:
                            print("[TAKEPIC] Retaking Image")
                            #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open(image_queue.pop(0))))
                            image = image_handling.np_array_to_bytes(picam.take_picture())
                            self.wifi_send_socket.send_message(b"image:"+image)
                            print("[TAKEPIC] Receiving Messages")
                            classes = self.wifi_recv_socket.receive_message()
                            # update retry to allow for the adjusting of the robot if no classes are detected 
                            retry -= 1
                        elif retry:
                            # adjust the robot by sending the FALSE000 command 
                            print("[TAKEPIC] STM Adjusting")
                            self.stm_socket.write_to_STM(b"FALSE000")
                            self.stm_socket.write_to_STM(b"END00000")
                            STM_msg = self.stm_socket.read_from_STM()
                            # receive a message from STM to inform the robot has stopped after adjusting
                            if STM_msg == b"STOP0000":
                                # take a picture 
                                print("[TAKEPIC] Retaking Image")
                                #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open(image_queue.pop(0))))
                                image = image_handling.np_array_to_bytes(picam.take_picture())
                                self.wifi_send_socket.send_message(b"image:"+image)
                                print("[TAKEPIC] Receiving Messages")
                                classes = self.wifi_recv_socket.receive_message()
                            # set retry to 0 
                            retry = 0
                        elif not retry:
                            # if there was no class detected even after the retires, the run has flopped :(
                            print("[TAKEPIC] Prof Abort :((")
                            classes = None
                self.photo_event.clear()
        return


r = rpi_manager()
r.prestart()

read_wifi_thread = threading.Thread(target=r.read_wifi)
write_wifi_thread = threading.Thread(target=r.write_wifi)
write_STM_thread = threading.Thread(target=r.write_STM)
take_picture_thread = threading.Thread(target=r.take_picture)

read_wifi_thread.start()
write_wifi_thread.start()
write_STM_thread.start()
take_picture_thread.start()
