from wifi_communication import wifi_communication
from model import model 
import image_handling
import config
import socket 
import time
from PIL import Image

num_of_pics_to_take = 5
num_of_pics_taken = 0
counter = 1

m = model("weights/epoch_148.pt")

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
#         bbox_input = message
#         bbox_str_array = bbox_input.split(b"OBS_")[1:]
#         bbox_algo_input = []
#         print(bbox_str_array)
#         for bbox_str in bbox_str_array:
#             input = bbox_str.split(b",")
#             print(input)
#             x = int(input[1]) - 1
#             y = 20 - int(input[2])
#             angle = 0
#             if input[3] == b'0':
#                 angle = 90
#             elif input[3] == b'1':
#                 angle = 0
#             elif input[3] == b'2': 
#                 angle = -90
#             elif input[3] == b'3':
#                 angle = 180
#             bbox_algo_input.append([x,y,angle])
        break 

# print(bbox_algo_input)

# algo = path_planner(bbox_algo_input)

# algo_output_array = algo.final_message_list
# pygame.quit()

# print(algo_output_array)
# algo_array = []
# start_index = 0
# for algo_output_index in range(0,len(algo_output_array)):
#     if algo_output_array[algo_output_index].startswith("c:TAKEPIC"):
#         algo_array.append(algo_output_array[start_index:algo_output_index]+[algo_output_array[algo_output_index]])
#         start_index = algo_output_index+1

# print(algo_array)
# algo_output_string = bytes(''.join(algo_array[0]), "UTF-8")

algo_output_string = bytes(''.join(["c:FS100000,c:END00000,c:TAKEPIC1,2"]), "UTF-8")
w_send.send_message(algo_output_string)

# while (True): 
#         message = w_recv.receive_message()
#         coordinate_message = b""
#         if message.startswith(b"OBS_"):
#             box_coordinates_array = message.split("OBS_")
#             bc_input_array = []
#             for bc in box_coordinates_array:
#                 bc = bc.removeprefix(b"OBS_")
#                 bc_input_array.append(bc.split(b","))
#             # algo.generate_path(bc_input_array)
#             # coordinate_message = algo.get_path()
#         elif message.startswith(b"BANANAS"):
#             coordinate_message = b"c:FL010000,c:FR010000,c:FS000010,c:END00000"
#             w_send.send_message(coordinate_message)
#             break


# def get_input():
#     while True:
#         print("input:")
#         input()
#     message = bytes("c:END00000,c:TAKEPIC", "UTF-8")
#     w_send.send_message(message)
    
# get_input()

while (num_of_pics_taken < num_of_pics_to_take):
    message = w_recv.receive_message()
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
        image.save("images/train_"+str(time.time())+".jpg")
        image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
        image.save("images/bbox_"+str(time.time())+".jpg")
        num_of_pics_taken += 1
        
        classes = bytes(classes, 'utf-8')
        w_send.send_message(classes)
    message = w_recv.receive_message()
    print(message)
    if message == (b"nextalgo"):
        time.sleep(1)
        algo_output_string = bytes(''.join(["c:FS100000,c:END00000,c:TAKEPIC1,2"]), "UTF-8")
        #algo_output_string = bytes(''.join(algo_array[counter]), "UTF-8")
        w_send.send_message(algo_output_string)
        counter += 1

#imageTiling()
w_send.disconnect()
w_recv.disconnect()