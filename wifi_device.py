from image_tiling import imageTiling
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

client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

m1 = model("weights/epoch_102.pt")
bullseye = model("weights/bullseye.pt")

w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080

w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

    # while (True):
    #     message = w_recv.receive_message()
    #     coordinate_message = b""
    #     if message.startswith(b"OBS_"):
    #         box_coordinates_array = message.split("OBS_")
    #         bc_input_array = []
    #         for bc in box_coordinates_array:
    #             bc = bc.removeprefix(b"OBS_")
    #             bc_input_array.append(bc.split(b","))
    #         # algo.generate_path(bc_input_array)
    #         # coordinate_message = algo.get_path()
    #     elif message.startswith(b"BANANAS"):
    #         coordinate_message = b"c:FL010000,c:FR010000,c:FS000010,c:END00000"
    #         w_send.send_message(coordinate_message)
    #         break
fs_length = "040000"
message = bytes("c:END00000,c:TAKEPICLOOP", "UTF-8")

w_send.send_message(message)
    
while (num_of_pics_taken < num_of_pics_to_take):
    message = w_recv.receive_message()
    if (message.startswith(b"image:")):
        byte_image = message.removeprefix(b"image:")
        np_image = image_handling.bytes_to_np_array(byte_image)
        image = image_handling.np_array_to_image(np_image)
        image.show()
        #bullseye_array = bullseye.get_results(np_image)
        results_array = m1.get_results(np_image)

        classes = []
        for result in results_array:
            classes.append(result[1])
        print(classes)

        # if len(classes) == 0:
        #     for detections in bullseye_array:
        #         if detections[1] == "Bullseye":
        #             results_array = bullseye_array
        #             classes = [detections[1]]
        
        classes = "classes:"+ ','.join(classes)
        image.save("images/train_"+str(time.time())+".jpg")
        image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
        image.save("images/bbox_"+str(time.time())+".jpg")
        counter += 1
        num_of_pics_taken += 1
        
        classes = bytes(classes, 'utf-8')
        w_send.send_message(classes)

#imageTiling()
w_send.disconnect()
w_recv.disconnect()