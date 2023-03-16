from model import model 
import image_handling
from PIL import Image

# Load Model
m = model("weights/best_week9_final.pt")

from wifi_communication import wifi_communication
import config
import time

# Set number of pictures to take
num_of_pics_to_take = 2
num_of_pics_taken = 0

# Declare array to store images for tiling
image_array = []



#Initiate a Classes Dictionary
classes_dict = {}

# Get Socket IP and Port Values
client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

# Connect To Socket 
w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080
w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

while num_of_pics_taken < num_of_pics_to_take:
    print(num_of_pics_taken)
    message = w_recv.receive_message()
    if (message.startswith(b"preimage:")):
        print("[TAKEPIC] Preimage Event")
        print("[Wifi] Received Image")
        image_data = message.removeprefix(b"preimage:")
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
            if "38" in classes or "39" in classes:
                current_image = ["Image "+str(num_of_pics_taken+1),[image]]
                image_array.append(current_image)
                
        classes_dict[num_of_pics_taken] = classes

    elif(message.startswith(b"FINDOBS:")):
        print("[TAKEPIC] FINDOBS Event")
        pic_idx = int(message.removeprefix(b"FINDOBS:").decode("UTF-8"))
        if pic_idx in classes_dict:
            classes = "classes:"+ ','.join(classes_dict[pic_idx])
            print("[Wifi] {}".format(classes))
            classes = bytes(classes, 'utf-8')
            print("[Wifi] Sending Classes")
            w_send.send_message(classes)
            if "39" in classes_dict[pic_idx] or "38" in classes_dict[pic_idx]:
                num_of_pics_taken += 1
        else:
            w_send.send_message(b"classes:0")

    elif (message.startswith(b"image:")):
        print("[TAKEPIC] Image Event")
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
            if "38" in classes or "39" in classes:
                current_image = ["Image "+str(num_of_pics_taken+1),[image]]
                image_array.append(current_image)
                num_of_pics_taken += 1
        
        classes = "classes:"+ ','.join(classes)
        print("[Wifi] {}".format(classes))
        classes = bytes(classes, 'utf-8')
        print("[Wifi] Sending Classes")
        w_send.send_message(classes)
    
tiled_image = image_handling.image_tiling(image_array)
tiled_image.show()
tiled_image.save("images/tiled_images.jpg")
w_send.disconnect()
w_recv.disconnect()