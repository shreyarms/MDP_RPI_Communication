# socket
socket_rpi_ip = "127.0.0.1"
socket_buffer_size = 16384
socket_sending_port = 8080
socket_receiving_port = 8081
# image rec
image_height = 640
image_width = 640
rpi_image_height = 1280
rpi_image_width = 1280
label_font = "arial.ttf"
label_size = 15
# bluetooth
bluetooth_uuid = "996c1b5f-170b-4f38-a5e0-85eef5acf12c"
bluetooth_host = "E4:5F:01:55:A7:10"
bluetooth_port = 1
bluetooth_socket_buffer_size = 8192
# STM32
serial_port = "/dev/ttyUSB0"
baud_rate = 115200
STM_buffer_size = 8
# communication
terminating_str = b"CLOSE"
# classes
names = {
    "11": "1",
    "12": "2",
    "13": "3",
    "14": "4",
    "15": "5",
    "16": "6",
    "17": "7",
    "18": "8",
    "19": "9",
    "20": "A",
    "21": "B",
    "22": "C",
    "23": "D",
    "24": "E",
    "25": "F",
    "26": "G",
    "27": "H",
    "28": "S",
    "29": "T",
    "30": "U",
    "31": "V",
    "32": "W",
    "33": "X",
    "34": "Y",
    "35": "Z",
    "36": "Up",
    "37": "Down",
    "38": "Right",
    "39": "Left",
    "40": "Circle",
}
# paths for week 9 [turn number, turn direction]
# first turn : [right, left]
path1fast = [
    b"c:P1R00000,c:END00000,c:TAKEPIC",
    b"c:P1L00000,c:END00000,c:TAKEPIC"
]

# second turn : [right, left]
path2fast = [
    b"c:P2R00000,c:END00000",
    b"c:P2L00000,c:END00000"
]

retry = b"c:FALSE000,c:END00000"