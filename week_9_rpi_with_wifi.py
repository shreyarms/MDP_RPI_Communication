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

class rpi_manager():
    def __init__(self):
        self.turn_number = 1
        self.photo_event = threading.Event()
        self.to_android = queue.Queue()
        self.to_STM = queue.Queue()
        self.to_wifi = queue.Queue()
        self.bluetooth_socket = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
        self.wifi_recv_socket = wifi_communication(config.socket_buffer_size,config.terminating_str)
        self.wifi_send_socket = wifi_communication(config.socket_buffer_size,config.terminating_str)
        self.stm_socket = stm_communication(config.serial_port,config.baud_rate,config.STM_buffer_size)
    
    def prestart(self):
        self.bluetooth_socket.advertise_and_accept_connection(config.bluetooth_host, config.bluetooth_port)
        self.wifi_send_socket.accept_connection(config.socket_rpi_ip, config.socket_sending_port) #8080
        self.wifi_recv_socket.accept_connection(config.socket_rpi_ip, config.socket_receiving_port) #8081
        self.stm_socket.connect_STM()
        
        while True: 
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"BANANAS"):
                self.to_STM.put(b"c:SENSOR30,c:END00000,c:TAKEPIC")
                print("[RPi] BANANAS")
                break
        return
    
    def read_wifi(self):
        while True:
            #listen to socket
            receiving,_,_ = select.select([self.wifi_recv_socket.socket], [], [])
            if not self.photo_event.is_set() and receiving:
                message = self.wifi_recv_socket.receive_message()
                # to get instructions from algorithm
                if message.startswith(b"c:"):
                    instructions = message.split(b'c:')
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
            
    # def write_android(self):
    #     while True:
    #         if not self.photo_event.is_set():
    #             try: 
    #                 if not self.to_android.empty():
    #                     message = self.to_android.get()
    #                     print("Bluetooth:{}".format(message))
    #                     self.bluetooth_socket.send_message(message)
    #             except Exception as e:
    #                 print("[RPi] Could Not Send to Android: {}".format(str(e)))
    #         else:
    #             continue

    def write_STM(self):
        while True:
            if not self.photo_event.is_set():
                try: 
                    if not self.to_STM.empty():
                        STM_data = self.to_STM.get()
                        if STM_data.startswith(b"c:"):
                            instructions = STM_data.split(b'c:')
                            for instruction in instructions:
                                print(instruction)
                                instruction = instruction.removeprefix(b"c:")
                                instruction = instruction.removesuffix(b",")
                                print(instruction)
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
            print("[RPi] Inside Event")
            STM_msg = self.stm_socket.read_from_STM()
            if STM_msg == b"STOP0000":
                print("[RPi] STM Stopped")
                #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test.jpg")))
                image = image_handling.np_array_to_bytes(picam.take_picture())
                self.wifi_send_socket.send_message(b"image:"+image)
                print("Receiving Messages")
                classes = self.wifi_recv_socket.receive_message()
                raw_classes = classes.removeprefix(b"classes:") #15,17
                # if turn_number = 1, first turn. turn_number 2 is the second turn + going back to car park
                # after first turn, stm needs to move forward using ultrasound sensor till 30cm away from box, then stops and sends take pic
                print(raw_classes)
                if raw_classes[0] == "38":
                    STM_input = config.path[self.turn_number-1][0]
                    self.to_STM.put(STM_input)
                elif raw_classes[0] == "39":
                    STM_input = config.path[self.turn_number-1][1]
                    self.to_STM.put(STM_input)
                self.turn_number += 1
                self.photo_event.clear()
        return



r = rpi_manager()
r.prestart()
read_wifi_thread = threading.Thread(target = r.read_wifi)
#android_communication_thread = threading.Thread(target = android_communication)
write_wifi_thread = threading.Thread(target = r.write_wifi)
# read_android_thread  = threading.Thread(target= r.write_android)
write_STM_thread= threading.Thread(target= r.write_STM)
take_picture_thread = threading.Thread(target = r.take_picture)

read_wifi_thread.start()
#android_communication_thread.start()
write_wifi_thread.start()
# read_android_thread.start()
write_STM_thread.start()
take_picture_thread.start()
