from model import model 
import image_handling
from PIL import Image

from wifi_communication import wifi_communication
import config
import time

# Set number of pictures to take
num_of_pics_to_take = 2
num_of_pics_taken = 0

# Declare array to store images for tiling
image_array = []

# Load Model
m = model("weights/week_9_best.pt")

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
    # receive images 
    message = w_recv.receive_message()
    # if image is taken at the start, then it is a preimage
    # preimages are saved in a dictionary and can be looked up later 
    if (message.startswith(b"preimage:")):
        print("[TAKEPIC] Preimage Event")
        print("[Wifi] Received Image")
        # get image data 
        image_data = message.removeprefix(b"preimage:")
        np_image = image_handling.bytes_to_np_array(image_data)

        # save raw image for training 
        image = image_handling.np_array_to_image(np_image)
        image.save("images/"+str(time.time()) +".jpg")

        # get results and put results in classes array 
        results_array = m.get_results(np_image)
        classes = []
        for result in results_array:
            classes.append(result[1])

        # if arrow classes are detected, draw their bboxes and add image into image_array for tiling 
        if len(classes) == 0:
            classes.append(str(0))
        else:
            image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
            image.save("images/"+str(time.time()) +".jpg")
            if "38" in classes or "39" in classes:
                current_image = ["Image "+str(num_of_pics_taken+1),[image]]
                image_array.append(current_image)
        
        # save classes into a dictionary
        classes_dict[num_of_pics_taken] = classes

    # Used to get classes form images taken before, by the preimage message  
    elif(message.startswith(b"FINDOBS:")):
        print("[TAKEPIC] FINDOBS Event")
        # get key for dictionary lookup from message 
        pic_idx = int(message.removeprefix(b"FINDOBS:").decode("UTF-8"))
        # if key is present in dictionary, send classes 
        # if not, send "classes:0" 
        if pic_idx in classes_dict:
            # send classes 
            classes = "classes:"+ ','.join(classes_dict[pic_idx])
            print("[Wifi] {}".format(classes))
            classes = bytes(classes, 'utf-8')
            print("[Wifi] Sending Classes")
            w_send.send_message(classes)
            # update number of pics taken only when arrow classes are detected 
            if "39" in classes_dict[pic_idx] or "38" in classes_dict[pic_idx]:
                num_of_pics_taken += 1
        else:
            w_send.send_message(b"classes:0")
    
    # If an image is to be detected and the classes are to be sent immediately after 
    elif (message.startswith(b"image:")):
        print("[TAKEPIC] Image Event")
        print("[Wifi] Received Image")
        # get image data 
        image_data = message.removeprefix(b"image:")
        np_image = image_handling.bytes_to_np_array(image_data)

        # save raw image for training 
        image = image_handling.np_array_to_image(np_image)
        image.save("images/"+str(time.time()) +".jpg")

        # get results and put results in a classes array
        results_array = m.get_results(np_image)
        classes = []
        for result in results_array:
            classes.append(result[1])

        # if classes are detected, draw bboxes 
        if len(classes) == 0:
            classes.append(str(0))
        else:            
            image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), results_array)
            image.save("images/"+str(time.time()) +".jpg")
            # if arrow classes are detcted, add to image_array for tiling and update num of pics taken
            if "38" in classes or "39" in classes:
                current_image = ["Image "+str(num_of_pics_taken+1),[image]]
                image_array.append(current_image)
                num_of_pics_taken += 1
        
        # send classes 
        classes = "classes:"+ ','.join(classes)
        print("[Wifi] {}".format(classes))
        classes = bytes(classes, 'utf-8')
        print("[Wifi] Sending Classes")
        w_send.send_message(classes)
    
# after all pictures ahve been detected, tile the images and display
tiled_image = image_handling.image_tiling(image_array)
tiled_image.show()
tiled_image.save("images/tiled_images.jpg")
w_send.disconnect()
w_recv.disconnect()