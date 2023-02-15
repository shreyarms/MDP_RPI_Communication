from wifi_communication import wifi_communication
from model import model 
import image_handling
import config
import socket 
import time

client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

m = model("weights/best.pt")

w_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_recv.initiate_connection(client, sending_address) #8080

w_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
w_send.initiate_connection(client, receiving_address) #8081

#2)algorithm 

algo_output = b"C:FL010000&5,3,NSEPC:FR010000&6,7,SSEPC:FS000010&8,9,WSEPC:END00000&8,9,W"
w_send.send_message(algo_output)
byte_image = w_recv.receive_message()
image = byte_image.removeprefix(b"image:")
np_image = image_handling.bytes_to_np_array(image)
result_array = m.get_results(np_image)
print(result_array)
image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array)
image.save("images/result_1.jpg")
classes = []
for result in result_array:
    classes.append(result[1])
classes = "classes:"+ ','.join(classes)

classes = bytes(classes, 'utf-8')
w_send.send_message(classes)

w_send.disconnect()
w_recv.disconnect()