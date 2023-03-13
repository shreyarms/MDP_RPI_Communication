
from wifi_communication import wifi_communication
from bluetooth_communication import bluetooth_communication
from stm_communication import stm_communication
from model import model
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
        self.model = model("weights/old_weights/v5_best.pt")
        self.bluetooth_socket = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
        self.stm_socket = stm_communication(config.serial_port,config.baud_rate,config.STM_buffer_size)
    
    def prestart(self):
        self.bluetooth_socket.advertise_and_accept_connection(config.bluetooth_host, config.bluetooth_port)
        self.stm_socket.connect_STM()
        
        while True: 
            message = self.bluetooth_socket.receive_message()
            if message.startswith(b"BANANAS"):
                self.to_STM.put(b"SENSOR00")
                self.to_STM.put(b"END00000")
                self.to_STM.put(b"TAKEPIC")
                print("[RPi] BANANAS")
                break
        return
    
    def write_STM(self):
        while True:
            if not self.photo_event.is_set():
                try: 
                    if not self.to_STM.empty():
                        STM_data = self.to_STM.get()
                        if STM_data.startswith(b"TAKEPIC"):
                            print("[RPi] Entering Phototaking Event")
                            self.photo_event.set()
                        elif len(STM_data) == config.STM_buffer_size:
                            self.stm_socket.write_to_STM(STM_data)          
                except Exception as e:
                    print("[RPi] Could Not Send to STM: {}".format(str(e)))
            else:
                continue
    
    def take_picture(self):
        while True:
            self.photo_event.wait()
            # print("[RPi] Inside Event")
            STM_msg = self.stm_socket.read_from_STM()
            if STM_msg == b"STOP0000":
                print("[RPi] STM Stopped")
                np_image = picam.take_picture()
                classes = self.model.get_results(np_image)
                raw_classes = classes.removeprefix(b"classes:") #15,17
                # if turn_number = 1, first turn. turn_number 2 is the second turn + going back to car park
                # after first turn, stm needs to move forward using ultrasound sensor till 30cm away from box, then stops and sends take pic
                
                # right is 0
                if raw_classes[0] == "38":
                    STM_input = config.path[self.turn_number-1][0]
                    self.to_STM.put(STM_input)
                # left is 1
                elif raw_classes[0] == "39":
                    STM_input = config.path[self.turn_number-1][1]
                    self.to_STM.put(STM_input)
            self.turn_number += 1
            self.photo_event.clear()  
        return

r = rpi_manager()
r.prestart()

write_STM_thread= threading.Thread(target= r.write_STM)
take_picture_thread = threading.Thread(target = r.take_picture)

write_STM_thread.start()
take_picture_thread.start()
