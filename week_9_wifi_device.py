import pygame
from wifi_communication import wifi_communication
from model import model 
import image_handling
import config
import socket 
import time
from PIL import Image
from pygame.locals import *
from Simulator_Pygame.path_planner import path_planner 
import Simulator_Pygame.settings as settings

# Declare array to store images for tiling
image_array = []

# Load Model
m = model("weights/week_8_best.pt")

# Get Socket IP and Port Values
client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

# Connect To Socket 
w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080
w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

while True:
    message = w_recv.receive_message()
    if (message.startswith(b"image:")):
        print("[Wifi] Received Image")
        image_data = message.removeprefix(b"image:")
        np_image = image_handling.bytes_to_np_array(image_data)
        image = image_handling.np_array_to_image(np_image)
        image.save("images/"+str(time.time()) +".jpg")
        results_array = m.get_results(np_image)

        classes = []
        for result in results_array:
            classes.append(result[1])

        if len(classes) == 0:
            classes.append(str(0))
        else:
            image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
            image.save("images/"+str(time.time()) +".jpg")
        
        classes = "classes:"+ ','.join(classes)
        print("[Wifi] {}".format(classes))
        classes = bytes(classes, 'utf-8')
        print("[Wifi] Sending Classes")
        w_send.send_message(classes)

        # # num_of_pics_taken += 1

        # message = w_recv.receive_message()
        # if message.startswith(b"nextalgo"):
        #     num_of_pics_taken += 1
        #     print("[Wifi] Sending Next Path")
        #     # time.sleep(1)
        #     if num_of_pics_taken < len(algo_array):
        #         algo_output_string = bytes(''.join(algo_array[num_of_pics_taken]), "UTF-8")
        #         #custom_input = ["c:FL180000","c:END00000","c:TAKEPIC1,2"]"
        #         #algo_output_string = bytes(''.join(custom_input), "UTF-8")
        #         w_send.send_message(algo_output_string)
        #     else:
        #         break

# tiled_image = image_handling.image_tiling(image_array)
# tiled_image.show()
# tiled_image.save("images/tiled_images.jpg")
w_send.disconnect()
w_recv.disconnect()