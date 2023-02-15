from wifi_communication import socket_communication
from model import model 
import image_handling
import config
import socket 

m = model("weights/best.pt")
hostname = socket.gethostname()   
host = socket.gethostbyname(hostname)  
port = 0

client = config.socket_rpi_ip
address = config.socket_port_number

s = socket_communication(host, port, config.socket_buffer_size)
s.initiate_connection(client, address)

msg = s.receive_message()

np_msg = image_handling.bytes_to_np_array(msg)
result_array = m.get_results(np_msg)
image = image_handling.draw_bbox(image_handling.np_array_to_image(np_msg), result_array)

result_msg = image_handling.np_array_to_bytes(image_handling.image_to_np_array(image))


s.send_message(result_msg)

s.disconnect()






