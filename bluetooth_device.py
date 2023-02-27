from bluetooth_communication import bluetooth_communication
import config
import queue
import threading

b = bluetooth_communication(config.bluetooth_uuid,config.bluetooth_socket_buffer_size,config.terminating_str)
b.find_connection(config.bluetooth_host, config.bluetooth_port)

# remote_control = b"rc:FS000010"
# b.send_message(remote_control)

# to_RPi = queue.Queue([])
# coordinate_buffer = queue.Queue([])
# image_classes = None

# def sender():
#     while True:
#         message = to_RPi.get()
#         print("Sending message to RPI...")
#         b.send_message(message)
#         to_RPi.task_done()

# def receiver():
#     while True:
#         message = b.receive_message()
#         if message is None:
#             continue
#         elif message.startswith("C:"):
#             coordinate_buffer.put(message)
#         elif message.startswith("classes:"):
#             image_classes = message
#         elif message == b"END":
#             break 

# #1) box_coordinates 
# # function to convert output into x,y,degreeSEPx,y,degreeSEP...

# box_coordinates = b"bc:"+"2,5,0SEP1,7,90"
# to_RPi.append(box_coordinates)


# send_thread = threading.Thread(target=sender, daemon=True).start()
# recv_thread = threading.Thread(target=receiver, daemon=True).start()


# wifi_msg = b.receive_message()

# if wifi_msg == b"Hi From Wifi":
#     bt_msg = b"Bye From Bluetooth"

# print("Sent From Wifi: ",wifi_msg)

# b.send_message(bt_msg)

b.disconnect()