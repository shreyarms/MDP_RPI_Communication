# socket
socket_rpi_ip = "192.168.27.27"
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
sep_str = b"SEP"
loop_path = b"BS020000,FL090000,FS008000,FR180000,BS030000,END00000"
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
# 0,0 : 1st right
# 0,1 : 1st left
# 1,0 : 2nd right
# 1,1 : 2nd left

path = [
    ["c:FR090000,c:END00000"],
    ["c:FL090000,c:END000000"],
    ["c:FR090000,c:END00000"],
    ["c:FL090000,c:END00000"],
]



# first turn : [right, left]
path1 = [
    b"c:FR031397,c:FS033948,c:FL031397,c:TPR00000,c:END00000,c:TAKEPIC",
    b"c:FL031397,c:FS033948,c:FR031397,c:TPL00000,c:END00000,c:TAKEPIC",
]

# first turn left, second turn : [right, left]
path2left = [
    b"c:SENSOR50,c:FR057645,c:FS061298,c:FL148715,c:FS047242,c:FL091070,c:MOVEMEMO,c:FL065307,c:FS023022,c:FR065307,c:SENSOR10,c:END00000",
    b"c:SENSOR50,c:FL020794,c:FS061258,c:FR109671,c:FS050101,c:FR088877,c:MOVEMEMO,c:FR065307,c:FS023022,c:FL065307,c:SENSOR10,c:END00000",
]

# first turn right, second turn : [right, left]
path2right = [
    b"c:SENSOR50,c:FR020794,c:FS061258,c:FL111864,c:FS04724,c:FL091070,c:MOVEMEMO,c:FL065307,c:FS023022,c:FR065307,c:SENSOR10,c:END00000",
    b"c:SENSOR50,c:FL057645,c:FS061298,c:FR146522,c:FS050101,c:FR088877,c:MOVEMEMO,c:FR065307,c:FS023022,c:FL065307,c:SENSOR10,c:END00000",
]


# ------------------------------------------------------------------------------------------------------

# first turn : [right, left]
path1fast = [
    b"c:P1R00000,c:END00000",
    b"c:P1L00000,c:END00000"
]

# second turn : [right, left]
path2fast = [
    b"c:P2R00000,c:END00000",
    b"c:P2L00000,c:END00000"
]

retry = b"c:SENSOR60,c:END00000,c:TAKEPIC"
