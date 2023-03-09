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

# Set number of pictures to take
num_of_pics_to_take = 6
num_of_pics_taken = 0

# Declare array to store images for tiling
image_array = []

# Load Model
m = model("weights/epoch_148.pt")

# Load Algo
pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((settings.Window_Size), RESIZABLE)
pygame.display.set_caption("MDP Simulator")
#primary_surface is for resizeable purposes
primary_surface = DISPLAYSURF.copy()
primary_surface.fill([0,0,0])

# Get Socket IP and Port Values
client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

# Connect To Socket 
w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080
w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

# Get Obstacles  
while True:
    message = w_recv.receive_message()
    if message.startswith(b"OBS_"):
        print("[Wifi] Received Obstacles")
        obs_input = message
        obs_str_array = obs_input.split(b"OBS_")[1:]
        obs_algo_input = []
        for obs_str in obs_str_array:
            input = obs_str.split(b",")
            # Get X, Y and Angle of Obstacle 
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
            obs_algo_input.append([x,y,angle])
        break 

print("[Wifi] Obstacle Input:{}".format(obs_algo_input))

# Pass Obstacles Into Algo 
algo = path_planner(obs_algo_input)

# Get Algo Output 
algo_output_array = algo.final_message_list
pygame.quit()

# Split Algo Array To Send Point-to-Point Instructions 
algo_array = []
start_index = 0
for algo_output_index in range(0,len(algo_output_array)):
    if algo_output_array[algo_output_index].startswith("c:TAKEPIC"):
        algo_array.append(algo_output_array[start_index:algo_output_index]+[algo_output_array[algo_output_index]])
        start_index = algo_output_index+1


print("[Wifi] Algo Output: {}".format(algo_array))
algo_output_string = bytes(''.join(algo_array[num_of_pics_taken]), "UTF-8")

#for custom input 
#custom_input = ["c:FL180000","c:END00000","c:TAKEPIC1,2"]"
#algo_output_string = bytes(''.join(custom_input), "UTF-8")

w_send.send_message(algo_output_string)

while (num_of_pics_taken < num_of_pics_to_take):
    message = w_recv.receive_message()
    if (message.startswith(b"image:")):
        print("[Wifi] Received Image")
        image_data = message.removeprefix(b"image:")
        image_data_split = image_data.split(b"SEPERATE")
        num_of_pics_taken, byte_image = int(image_data_split[0]),b''.join(image_data_split[1:])
        np_image = image_handling.bytes_to_np_array(byte_image)
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
            current_image = ["Image "+str(num_of_pics_taken+1),[image]]
            image_array.append(current_image)
        
        classes = "classes:"+ ','.join(classes)
        print("[Wifi] {}".format(classes))
        classes = bytes(classes, 'utf-8')
        print("[Wifi] Sending Classes")
        w_send.send_message(classes)

        # num_of_pics_taken += 1

        message = w_recv.receive_message()
        if message.startswith(b"nextalgo"):
            num_of_pics_taken += 1
            print("[Wifi] Sending Next Path")
            # time.sleep(1)
            if num_of_pics_taken < len(algo_array):
                algo_output_string = bytes(''.join(algo_array[num_of_pics_taken]), "UTF-8")
                #custom_input = ["c:FL180000","c:END00000","c:TAKEPIC1,2"]"
                #algo_output_string = bytes(''.join(custom_input), "UTF-8")
                w_send.send_message(algo_output_string)
            else:
                break

tiled_image = image_handling.image_tiling(image_array)
tiled_image.show()
tiled_image.save("images/tiled_images.jpg")
w_send.disconnect()
w_recv.disconnect()