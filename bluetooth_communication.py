import os
from bluetooth import *
import config 
import time

class bluetooth_communication:
    # Initialisation 
    def __init__(self,bluetooth_uuid,bluetooth_socket_buffer_size,terminating_string):
        self.socket = None
        self.client_info = None
        self.bluetooth_uuid = bluetooth_uuid
        self.bluetooth_socket_buffer_size = bluetooth_socket_buffer_size
        self.terminating_string = terminating_string
        os.system('sudo chmod o+rw /var/run/sdp')
        os.system("sudo hciconfig hci0 piscan")
        

    # Connection to Android
    def advertise_and_accept_connection(self,host,port):
        retry = True
        while retry: 
            try: 
                listening_socket = BluetoothSocket(RFCOMM)
                listening_socket.bind((host, port))
                listening_socket.listen(1)
                advertise_service(listening_socket, "MDP-Team27",
                service_id = self.bluetooth_uuid,
                service_classes = [self.bluetooth_uuid, SERIAL_PORT_CLASS],
                profiles = [SERIAL_PORT_PROFILE],
                protocols = [OBEX_UUID]
                )
                print("[Bluetooth] Waiting for connection on RFCOMM channel {}".format(port))
                if self.client_info is None:
                    self.socket, self.client_info = listening_socket.accept()
                    print("[Bluetooth] Accepted bluetooth connection from {}".format(self.client_info))
                else:
                    print("[Bluetooth] Already Connected To {}".format(self.client_info))
                retry = False
            except Exception as e:
                print("[Bluetooth] Connection failed".format(str(e)))
                time.sleep(1)

    def find_connection(self,client,client_port):
        retry = True
        print("Finding Device...")
        while retry:
            try: 
                if self.client_info is None:
                    print("[Bluetooth] Connecting to {} on {}".format(client, client_port))
                    self.socket = BluetoothSocket( RFCOMM )
                    self.socket.connect((client, client_port))
                    self.client_info = (client, client_port)
                else:
                    print("[Bluetooth] Already Connected To {}".format(self.client_info))
                retry = False
            except Exception as e :
                print("[Bluetooth] Could Not Connect:".format(str(e)))
                time.sleep(1)

    # Disconnection
    def disconnect(self):
        retry = True
        while retry: 
            try: 
                if self.client_info is not None:
                    self.socket.close()
                    self.socket = None
                    self.client_info = None
                    print("[Bluetooth] Sucessfully disconnected")
                retry = False
            except Exception as e:
                print("[Bluetooth] Failed to disconnect %s" % str(e))
        return 
    
    # Sending Message 
    def send_message(self, message):
        try:
            if self.client_info is not None:
                print("[Bluetooth] Sending message...")
                self.socket.send(message+self.terminating_string)
                print("[Bluetooth] Message Sent")
        except BluetoothError as e:
            print("[Bluetooth] Failed to send %s" % str(e))
        return
    
    # Reading from Android
    def receive_frame(self):
        frame_txt = b''
        try:
            frame_txt = self.socket.recv(config.bluetooth_socket_buffer_size)
        except BluetoothError as e:
            print("[Bluetooth] Failed to read %s" % str(e))
            pass
        return frame_txt

    def receive_message(self):
        msg = b''
        count = 1
        frame_txt = self.receive_frame()
        while self.terminating_string not in frame_txt and len(frame_txt) > 0:
            msg = msg + frame_txt
            if count%20 == 0:
                print("[Bluetooth] {} frames received".format(count))
            frame_txt = self.receive_frame()
            count += 1
        else:
            return msg + frame_txt.removesuffix(self.terminating_string)