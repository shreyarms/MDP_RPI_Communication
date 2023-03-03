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
num_of_pics_to_take = 5
num_of_pics_taken = 0

image_array = []

m = model("weights/epoch_148.pt")

pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((settings.Window_Size), RESIZABLE)
pygame.display.set_caption("MDP Simulator")
#primary_surface is for resizeable purposes
primary_surface = DISPLAYSURF.copy()
primary_surface.fill([0,0,0])

client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080
w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

while True:
    message = w_recv.receive_message()
    print(message)
    if message.startswith(b"OBS_"):
        bbox_input = message
        bbox_str_array = bbox_input.split(b"OBS_")[1:]
        bbox_algo_input = []
        print(bbox_str_array)
        for bbox_str in bbox_str_array:
            input = bbox_str.split(b",")
            print(input)
            x = int(input[1]) - 1
            y = 20 - int(input[2])
            angle = 0
            if input[3] == b'0':
                angle = 90
            elif input[3] == b'1':
                angle = 0
            elif input[3] == b'2': 
                angle = -90
            elif input[3] == b'3':
                angle = 180
            bbox_algo_input.append([x,y,angle])
        break 

print(bbox_algo_input)

algo = path_planner(bbox_algo_input)

algo_output_array = algo.final_message_list
pygame.quit()

print(algo_output_array)
algo_array = []
start_index = 0
for algo_output_index in range(0,len(algo_output_array)):
    if algo_output_array[algo_output_index].startswith("c:TAKEPIC"):
        algo_array.append(algo_output_array[start_index:algo_output_index]+[algo_output_array[algo_output_index]])
        start_index = algo_output_index+1

print(algo_array)
algo_output_string = bytes(''.join(algo_array[num_of_pics_taken]), "UTF-8")
#algo_output_string = bytes(''.join(["c:FL180000c:END00000c:TAKEPIC1,2"]), "UTF-8")
w_send.send_message(algo_output_string)

while (num_of_pics_taken < num_of_pics_to_take):
    message = w_recv.receive_message()
    print(len(message))
    if (message.startswith(b"image:")):
        byte_image = message.removeprefix(b"image:")
        np_image = image_handling.bytes_to_np_array(byte_image)
        image = image_handling.np_array_to_image(np_image)
        print(len(np_image))
        
        results_array = m.get_results(np_image)

        classes = []
        for result in results_array:
            classes.append(result[1])
        print(classes)
        
        classes = "classes:"+ ','.join(classes)
        image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
        #image.save("images/bbox_"+str(time.time())+".jpg")
        image.show()
        num_of_pics_taken += 1
        
        current_image = ["Image "+str(num_of_pics_taken),image]
        image_array.append(current_image)
        classes = bytes(classes, 'utf-8')
        w_send.send_message(classes)
        message = w_recv.receive_message()
        print(message)
        if message == (b"nextalgo"):
            time.sleep(1)
            if num_of_pics_taken < len(algo_array):
                print(algo_array[num_of_pics_taken])
                algo_output_string = bytes(''.join(algo_array[num_of_pics_taken]), "UTF-8")
                # algo_output_string = bytes(''.join(["c:FS100000c:END00000c:TAKEPIC1,2"]), "UTF-8")
                w_send.send_message(algo_output_string)
            else:
                break

image_handling.image_tiling(image_array)
w_send.disconnect()
w_recv.disconnect()