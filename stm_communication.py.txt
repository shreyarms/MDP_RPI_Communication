import serial
import time

class stm_communication:
    #Initialisation
    def __init__(self, serial_port, baud_rate, STM_buffer_size):
        self.port = serial_port
        self.baud_rate = baud_rate
        self.STM_buffer_size = STM_buffer_size
        self.STM_connection = None
    
    # Connection
    def connect_STM(self):
        print("[STM] Waiting for serial connection...")
        retry = True
        while retry:
            try:
                self.STM_connection = serial.Serial(self.port, self.baud_rate)

                if self.STM_connection is not None:
                    print("[STM] Successfully connected with STM")
                retry = False
            except Exception as e:
                print("[STM] Could Not Connect: {}".format(str(e)))
                retry = True
                time.sleep(1)
        return 

    #Disconnect message
    def disconnect_STM(self):
        try:
            if self.STM_connection is not None:
                self.STM_connection.close()
                self.STM_connection = None
                print('[STM] Successfully Disconnected')

        except Exception as e:
            print("[STM] Could Not Disconnect: {}".format(str(e)))
        return 

    #Read message
    def read_from_STM(self):
        print("[STM] Reading From STM")
        try:
            message = b''
            if self.STM_connection is not None:
                self.STM_connection.flush()
                message = self.STM_connection.read(self.STM_buffer_size)
            return message
        except Exception as e:
            print("[STM] Read Failed: {}".format(str(e)))
            pass 
        return None

    # Write message
    def write_to_STM(self, message):
        try:
            if self.STM_connection is not None:
                print("[STM] Writing to STM")
                self.STM_connection.write(message)
        except Exception as e:
            print("Write Failed: {}".format(str(e)))
        return 
