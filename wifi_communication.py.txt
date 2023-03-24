import socket
import time

class wifi_communication:
    #Initialisation
    def __init__(self, buffer_size, terminating_string):
        self.socket = None
        self.client = None
        self.client_info = None
        self.buffer_size = buffer_size
        self.terminating_string = terminating_string
        return
    
    # Connect - Client Side
    def initiate_connection(self, client, address):
        retry = True
        while retry:
            try: 
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((client,address))
                self.client_info = (client,address) 
                print("[Wifi] Successful Connection with {}".format(self.client_info))
                retry = False
            except Exception as error:
                print("[Wifi] Initalise Connection: Could not connect to {}".format(client))
                retry = True
                time.sleep(1)
        return 

    #Connect - Server Side 
    def accept_connection(self, host, port):
        retry = True 
        while retry:
            try:
                listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listening_socket.bind((host, port))
                listening_socket.listen(1)
                print("[Wifi] Waiting For Connection...")
                if self.client_info is None:
                    self.socket,self.client_info = listening_socket.accept()
                    print("[Wifi] Successful Connection with {}".format(self.client_info))
                else:
                    print("[Wifi] Already Connected To {}".format(self.client_info))
                retry = False
            except Exception as error:
                print('[Wifi] Connection failed')
                retry = True
                time.sleep(1)
        return 
    
    #Disconnect
    def disconnect(self):
        retry = True
        while retry:
            try: 
                if self.client_info is not None:
                    print("[Wifi] Disconnecting connection to {}".format(self.client_info))
                    self.socket.close()
                    self.socket = None
                    self.client_info = None
                    print("[Wifi] Successfully Disconnected")
                retry = False
            except Exception as error:
                print("[Wifi] Could not Disconnect")
                retry = True
                time.sleep(1)
        return
    
    #Send Message
    def send_message(self, message):
        try:
            if self.client_info is not None:
                print("[Wifi] Sending message...")
                self.socket.sendall(message+self.terminating_string)
                print("[Wifi] Message Sent")
        except Exception as error:
            print("[Wifi] Send Failed")
        return

    #Receive Message
    def receive_frame(self):
        frame_txt = b''
        try: 
            frame_txt = self.socket.recv(self.buffer_size)
        except:
            print("[Wifi] Receive Failed")
            pass
        return frame_txt
    
    def receive_message(self):
        msg_txt = b''
        count = 1
        frame_txt = self.receive_frame()
        while self.terminating_string not in frame_txt and len(frame_txt) > 0:
            msg_txt = msg_txt + frame_txt
            if count%20 == 0:
                print("[Wifi] {} frames received".format(count))
            frame_txt = self.receive_frame()
            count += 1
        else:
            return msg_txt + frame_txt.removesuffix(self.terminating_string)

    

    

    


    





    
        


