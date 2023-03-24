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

class rpi_manager():
    def __init__(self, num_of_pictures_to_take):
        #declare number of pictures to take and number of pictures taken sort 
        self.num_of_pictures_to_take = num_of_pictures_to_take
        self.num_of_pictures_taken = 0
        # declare a threading event called photo event, which causes all the other threads to wait until the take_picture function finishes 
        self.photo_event = threading.Event()
        # declare three empty message queues 
        self.to_android = queue.Queue()
        self.to_STM = queue.Queue()
        self.to_wifi = queue.Queue()
        #declare a coordinate value to keep track of the corrdinates of the current box visited 
        self.coordinate = None
        # declare a constant to represent the number of times the robot adjusts it's location to detect an image
        self.adjustments = 2 
        # initialise connection socket objects 
        self.bluetooth_socket = bluetooth_communication(
            config.bluetooth_uuid,
            config.bluetooth_socket_buffer_size,
            config.terminating_str
        )
        self.wifi_recv_socket = wifi_communication(
            config.socket_buffer_size,
            config.terminating_str
        )
        self.wifi_send_socket = wifi_communication(
            config.socket_buffer_size,
            config.terminating_str
        )
        self.stm_socket = stm_communication(
            config.serial_port,
            config.baud_rate,
            config.STM_buffer_size
        )
    
    def prestart(self):
        # connect each connection socket object
        self.bluetooth_socket.advertise_and_accept_connection(
            config.bluetooth_host,
            config.bluetooth_port
        )
        self.wifi_send_socket.accept_connection(
            config.socket_rpi_ip,
            config.socket_sending_port
        ) # Port:8080
        self.wifi_recv_socket.accept_connection(
            config.socket_rpi_ip,
            config.socket_receiving_port
        )# Port:8081
        self.stm_socket.connect_STM()

        # Sending of Obstacles, starts with OBS_
        while True: 
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"OBS_"):
                print("[RPi] Received Obstacle Data")
                self.wifi_send_socket.send_message(message)
                print("[RPi] Sent Obstacle Data to Algo")
                break 
        
        # Sending of the START Command, which is BANANAS in our case 
        while True: 
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"BANANAS"):
                print("[RPi] BANANAS")
                break
        return
    
    # Function to read from wifi
    def read_wifi(self):
        while True:
            #listen to socket to see if it is receiving something 
            receiving,_,_ = select.select([self.wifi_recv_socket.socket], [], [])
            # checks the photo_event flag and only receives messages if flag is not set  
            if not self.photo_event.is_set() and receiving:
                message = self.wifi_recv_socket.receive_message()
                # to get instructions from algorithm, which all start with c: 
                if message.startswith(b"c:"):
                    instructions = message.split(b'c:')
                    for instruction in instructions:
                        instruction = instruction.removeprefix(b"c:")
                        self.to_STM.put(instruction)   
            else:
                continue
    
    # Function to write from wifi
    def write_wifi(self):
        while True:
            # checks the photo_event flag and only writes messages if flag is not set  
            if not self.photo_event.is_set():
                try: 
                    if not self.to_wifi.empty():
                        # gets from to_wifi queue and sends message over 
                        message = self.to_wifi.get()
                        self.wifi_send_socket.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Algo/Img Det: {}".format(str(e)))
            else:
                continue
            
    # Function to write to android 
    def write_android(self):
        while True:
            # checks the photo_event flag and only writes messages if flag is not set  
            if not self.photo_event.is_set():
                try: 
                    if not self.to_android.empty():
                        # gets from the to_android queue 
                        message = self.to_android.get()
                        print("Bluetooth:{}".format(message))
                        self.bluetooth_socket.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Android: {}".format(str(e)))
            else:
                continue
    
    # Fuction to write to STM 
    def write_STM(self):
        while True:
            # checks the photo_event flag and only writes messages if flag is not set  
            if not self.photo_event.is_set():
                try: 
                    if not self.to_STM.empty():
                        STM_data = self.to_STM.get()
                        # Point to Point instructions from the algorithm have a string of instruction to the STM and end with a TAKEPICx,y instruction, where x,y are the coordinates of the box 
                        # This is to let the RPi know that it should take pictures at that point
                        if STM_data.startswith(b"TAKEPIC") and self.num_of_pictures_taken < self.num_of_pictures_to_take:
                            print("[RPi] Entering Phototaking Event")
                            self.coordinate = STM_data.removeprefix(b"TAKEPIC")
                            # set photo event flag, which will only enable the take_picture fucntion to run  
                            self.photo_event.set()
                        elif len(STM_data) == config.STM_buffer_size and self.num_of_pictures_taken < self.num_of_pictures_to_take:
                            self.stm_socket.write_to_STM(STM_data)
                            if(STM_data == b"END00000" and self.num_of_pictures_taken == self.num_of_pictures_to_take):
                                self.to_android.put(b"STOP")
                                self.to_wifi.put(b"STOP")
                                self.bluetooth_socket.disconnect()
                                self.stm_socket.disconnect_STM()
                                self.wifi_recv_socket.disconnect()
                                self.wifi_send_socket.disconnect()              
                except Exception as e:
                    print("[RPi] Could Not Send to STM: {}".format(str(e)))
            else:
                continue
    
    def take_picture(self):
        while True:
            self.photo_event.wait()
            # starts running after the photo_event flag is set 
            print("[RPi] Inside Event")
            no_class_detected = True
            current_adjustments = 0
            while no_class_detected:
                # receive message from the STM that the robot has stopped 
                STM_msg = self.stm_socket.read_from_STM()
                if STM_msg == b"STOP0000":
                    print("[RPi] STM Stopped")
                    # take picture 
                    image = image_handling.np_array_to_bytes(picam.take_picture())
                    print("[RPi] Sending Image")
                    # send image to wifi device 
                    image_message = b"image:"+str(self.num_of_pictures_taken).encode()+b"SEPERATE"+image
                    self.wifi_send_socket.send_message(image_message)
                    # receive classes from wifi devoce after detecting images 
                    print("[RPi] Receiving Classes")
                    classes = self.wifi_recv_socket.receive_message()
                    raw_classes = classes.removeprefix(b"classes:") 
                    # if classes are detected, sedn classes via bluetooth to android tablet 
                    # if not, retry by adjusting the robot 
                    if raw_classes != b"0":
                        print("[RPi] Classes Detected:{}".format(raw_classes))
                        no_class_detected = False
                        bluetooth_coordinates = b"classes:"+self.coordinate+b","+raw_classes
                        print("[RPi] Sending Classes to Android")
                        self.to_android.put(bluetooth_coordinates)
                    else:
                        print("[RPi] No Classes Detected")
                        if current_adjustments < self.adjustments:
                            print("[RPi] Trying Out Different Scanning Angle")
                            current_adjustments += 1
                            self.stm_socket.write_to_STM(b"FALSE000")
                            self.stm_socket.write_to_STM(b"END00000")
                            self.wifi_send_socket.send_message(b"retry")
                        else:
                            print("[RPi] All Scanning Angles Exhausted")
                            no_class_detected = False
                            bluetooth_coordinates = b"classes:"+self.coordinate+b","+raw_classes
                            print("[RPi] Sending Classes to Android")
                            self.to_android.put(bluetooth_coordinates)
            #update num of pictures taken 
            self.num_of_pictures_taken += 1
            # request for next point to point algorithm 
            self.to_wifi.put(b"nextalgo")
            self.photo_event.clear()  
        return



r = rpi_manager(6)
r.prestart()

read_wifi_thread = threading.Thread(target = r.read_wifi)
write_wifi_thread = threading.Thread(target = r.write_wifi)
read_android_thread  = threading.Thread(target= r.write_android)
write_STM_thread= threading.Thread(target= r.write_STM)
take_picture_thread = threading.Thread(target = r.take_picture)

read_wifi_thread.start()
write_wifi_thread.start()
read_android_thread.start()
write_STM_thread.start()
take_picture_thread.start()
