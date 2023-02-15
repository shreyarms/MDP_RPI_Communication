from wifi_communication import wifi_communication
from model import model 
import image_handling
import config
import socket 
import time

client = config.socket_rpi_ip
sending_address = config.socket_sending_port #8080
receiving_address = config.socket_receiving_port #8081

m = model("RpiConnection/weights/best.pt")

s_recv = wifi_communication(config.socket_buffer_size, config.terminating_str)
s_recv.initiate_connection(client, sending_address) #8080

s_send = wifi_communication(config.socket_buffer_size, config.terminating_str)
s_send.initiate_connection(client, receiving_address) #8081


print(s_send.client_info)
print(s_recv.client_info)
#2)algorithm 
for i in range(0, 4):
    algo_output = b"C:FL010000,C:FR010000,C:FS000010,C:END00000,TAKEPIC"
    s_send.send_message(algo_output)
    byte_image = s_recv.receive_message()
    image = byte_image.removeprefix(b"image:")
    np_image = image_handling.bytes_to_np_array(image)
    result_array = m.get_results(np_image)
    print(result_array)
    image = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array)
    image.save("RpiConnection/images/result"+str(time.time())+".jpg")
    classes = []
    for result in result_array:
        classes.append(result[1])
    classes = "classes:"+ ','.join(classes)

    print(bytes(classes, 'utf-8'))
    s_send.send_message(b"test")

s_send.disconnect()
s_recv.disconnect()




