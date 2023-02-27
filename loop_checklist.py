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

num_of_pictures_to_take = 4
num_of_pictures_taken = 0



b = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
b.advertise_and_accept_connection(config.bluetooth_host, config.bluetooth_port)

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

num_of_pics_taken = 0
num_of_boxes = 4

photo_event = threading.Event()

def read_wifi():
    while True:
        #listen to socket
        receiving,_,_ = select.select([w_recv.socket], [], [])
        if not photo_event.is_set() and receiving:
            message = w_recv.receive_message()
            # to get instructions from algorithm
            if message.startswith(b"c:"):
                instruction_array = message.split(b',')
                for instruction in instruction_array:
                    instruction = instruction.removeprefix(b"c:")
                    to_STM.put(instruction)   
        else:
            continue
        
def write_wifi():
    while True:
        if not photo_event.is_set():
            try: 
                if not to_wifi.empty():
                    message = to_wifi.get()
                    w_send.send_message(message)
            except Exception as e:
                print("[RPi] Could Not Send to Algo/Img Det: {}".format(str(e)))
        else:
            continue

def android_communication():
    while True:
        receiving,_,_ = select.select([b.socket], [], [])
        if not photo_event.is_set():
            if receiving:
                message = b.receive_message()
                #sending remote control commands to STM
                if message.startswith(b"rc:"):
                    control_array = message.split(b",")
                    for instruction in control_array:
                        controls = instruction.removeprefix(b"rc:")
                        android_to_STM.put(controls)
            else:
                try: 
                    if not to_android.empty():
                        message = to_android.get()
                        print("Bluetooth:{}".format(message))
                        b.send_message(message)
                except Exception as e:
                    print("[RPi] Could Not Send to Android: {}".format(str(e)))


# def read_android():
#     while True:
#         if not photo_event.is_set():
#             message = b.receive_message()
            # sending start message to Wifi/Algo
            # if message.startswith(b"BANANAS"):
                # start = message
                # to_wifi.put(start)
            # sending box coordinates to Wifi/Algo
            # elif message.startswith(b"OBS_"):
            #     box_coordinates = message
            #     to_wifi.put(box_coordinates)
            # sending remote control commands to STM
            # if message.startswith(b"rc:"):
            #     print(message)
            #     controls = message.removeprefix(b"rc:")
            #     controls = message
            #     android_to_STM.put(controls)


def write_STM():
    while True:
        if not photo_event.is_set():
            try: 
                if not android_to_STM.empty() or not to_STM.empty():
                    if not android_to_STM.empty():
                        STM_data = android_to_STM.get()
                        if len(STM_data) == config.STM_buffer_size:
                            print("A2STM : {}".format(STM_data))
                            s.write_to_STM(STM_data)
                            print("A2STM : END00001")
                            s.write_to_STM(b"END00001")
                    else:
                        STM_data = to_STM.get()
                        print(STM_data)
                        if STM_data == b"TAKEPICLOOP" and num_of_pictures_taken < num_of_pictures_to_take:
                            photo_event.set()
                        elif len(STM_data) == config.STM_buffer_size and num_of_pictures_taken < num_of_pictures_to_take:
                            print("STM : {}".format(STM_data))
                            s.write_to_STM(STM_data)
                            if(STM_data == b"END00000" and num_of_pictures_taken == num_of_pictures_to_take):
                                to_android.put("STOP")
                                to_wifi.put("STOP")
                                b.disconnect()
                                s.disconnect_STM()
                                w_recv.disconnect()
                                w_send.disconnect()              
            except Exception as e:
                print("[RPi] Could Not Send to STM: {}".format(str(e)))
        else:
            continue

def take_picture_loop():
    photo_event.wait()
    classes = take_picture()
    classes = classes.removeprefix(b"classes:")
    while classes == b"Bullseye":
        path = config.loop_path
        path_array = path.split(b",")
        for STM_data in path_array:
            if (len(STM_data) == config.STM_buffer_size):
                print("STM : {}".format(STM_data))
                #s.write_to_STM(STM_data)
        classes = take_picture()
        classes = classes.removeprefix(b"classes:")
    print(classes)
    photo_event.clear()


def take_picture():
    STM_msg = s.read_from_STM()
    if STM_msg == b"STOP0000":
        print("Taking Picture")
        global num_of_pictures_taken
        num_of_pictures_taken = num_of_pictures_taken + 1
        image = Image.open("images/result_"+str(num_of_pictures_taken)+".jpg")
        image = image_handling.np_array_to_bytes(image_handling.image_to_np_array(image))
        #image = image_handling.np_array_to_bytes(picam.take_picture())
        print("sending {}".format(num_of_pictures_taken))
        w_send.send_message(b"image:"+image)
        print("Receiving Messages")
        classes = w_recv.receive_message()
        print(classes)
    return classes
        
        

# read_wifi_thread = threading.Thread(target = read_wifi)
# android_communication_thread = threading.Thread(target = android_communication)
# write_wifi_thread = threading.Thread(target = write_wifi)
# write_STM_thread= threading.Thread(target= write_STM)
# take_picture_loop_thread = threading.Thread(target = take_picture_loop)

# read_wifi_thread.start()
# android_communication_thread.start()
# write_wifi_thread.start()
# write_STM_thread.start()
# take_picture_loop_thread.start()
