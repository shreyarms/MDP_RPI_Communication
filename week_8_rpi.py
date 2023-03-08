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
    def __init__(self, num_of_pictures_to_take):
        self.num_of_pictures_to_take = num_of_pictures_to_take
        self.num_of_pictures_taken = 0
        self.photo_event = threading.Event()
        self.to_android = queue.Queue()
        self.to_STM = queue.Queue()
        self.to_wifi = queue.Queue()
        self.coordinate = None
        self.adjustments = 3
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
            print(message)
            if message.startswith(b"OBS_"):
                print("[RPi] Received Obstacle Data")
                self.wifi_send_socket.send_message(message)
                print("[RPi] Sent Obstacle Data to Algo")
                break 
        
        while True: 
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"BANANAS"):
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
            
    def write_android(self):
        while True:
            if not self.photo_event.is_set():
                try: 
                    if not self.to_android.empty():
                        message = self.to_android.get()
                        print("Bluetooth:{}".format(message))
                        self.bluetooth_socket.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Android: {}".format(str(e)))
            else:
                continue

    def write_STM(self):
        while True:
            if not self.photo_event.is_set():
                try: 
                    if not self.to_STM.empty():
                        STM_data = self.to_STM.get()
                        if STM_data.startswith(b"TAKEPIC")and self.num_of_pictures_taken < self.num_of_pictures_to_take:
                            print("[RPi] Entering Phototaking Event")
                            self.coordinate = STM_data.removeprefix(b"TAKEPIC")
                            # coordinate = coordinate.decode("UTF-8")
                            # x,y = [int(num) for num in coordinate.split(",")]
                            # x += 1
                            # y = 20 - y
                            # coordinate_str = str(x)+","+str(y)
                            # self.coordinate = bytes(coordinate_str, "UTF-8")
                            self.photo_event.set()
                        elif len(STM_data) == config.STM_buffer_size and self.num_of_pictures_taken < self.num_of_pictures_to_take:
                            print(STM_data)
                            self.stm_socket.write_to_STM(STM_data)
                            if(STM_data == b"END00000" and self.num_of_pictures_taken == self.num_of_pictures_to_take):
                                self.to_android.put("STOP")
                                self.to_wifi.put("STOP")
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
            print("[RPi] Inside Event")
            no_class_detected = True
            current_adjustments = 0
            self.num_of_pictures_taken += 1
            while no_class_detected:
                STM_msg = self.stm_socket.read_from_STM()
                if STM_msg == b"STOP0000":
                    print("[RPi] STM Stopped")
                    #image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(Image.open("images/test.jpg")))
                    image = image_handling.np_array_to_bytes(picam.take_picture())
                    print("[RPi] Sending Image")
                    self.wifi_send_socket.send_message(int.to_bytes(self.num_of_pictures_taken-1, "UTF-8")+b"_image:"+image)
                    print("[RPi] Receiving Classes")
                    classes = self.wifi_recv_socket.receive_message()
                    raw_classes = classes.removeprefix(b"classes:") 
                    if raw_classes != "0":
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
                        else:
                            print("[RPi] All Scanning Angles Exhausted")
                            no_class_detected = False
                            bluetooth_coordinates = b"classes:"+self.coordinate+b","+raw_classes
                            print("[RPi] Sending Classes to Android")
                            self.to_android.put(bluetooth_coordinates)
            self.to_wifi.put(b"nextalgo")
            self.photo_event.clear()  
        return



r = rpi_manager(6)
r.prestart()
read_wifi_thread = threading.Thread(target = r.read_wifi)
#android_communication_thread = threading.Thread(target = android_communication)
write_wifi_thread = threading.Thread(target = r.write_wifi)
read_android_thread  = threading.Thread(target= r.write_android)
write_STM_thread= threading.Thread(target= r.write_STM)
take_picture_thread = threading.Thread(target = r.take_picture)

read_wifi_thread.start()
#android_communication_thread.start()
write_wifi_thread.start()
read_android_thread.start()
write_STM_thread.start()
take_picture_thread.start()
