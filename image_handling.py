import numpy as np
from PIL import Image, ImageDraw, ImageFont 
import config 
import matplotlib.pyplot as plt

def bytes_to_np_array(msg):
    np_msg = np.frombuffer(msg, dtype=np.uint8)
    np_msg = np_msg.reshape(config.image_height,config.image_width,3)
    return np_msg

def np_array_to_image(np_msg):
    image = Image.fromarray(np_msg, "RGB")
    return image

def draw_bbox(image,result_array):
    bb_image = ImageDraw.Draw(image)  
    for result in result_array:
        bb_image.rectangle(result[0], outline ="red")
        font = ImageFont.truetype(config.label_font, config.label_size)
        bb_image.text(result[0],result[1]+"\n"+str(round(result[2],2)), font=font)
    return image

def image_to_np_array(image):
    np_msg = np.asarray(image)
    return np_msg

def np_array_to_bytes(np_msg):
    msg = np_msg.tobytes()
    return msg

#TODO: add image tiling as a step here 
def image_tiling(image_array):
    rows = len(image_array)
    cols = 1
    for image_details in image_array:
        if len(image_details[1])+1 > cols:
            cols = len(image_details[1])+1

    tiled_image = Image.new('RGB', (cols*config.image_width, rows*config.image_height))
    label_image = ImageDraw.Draw(tiled_image)  
    font = ImageFont.truetype(config.label_font, config.label_size*3)
    
    for i in range(rows):
        label_image.text((config.image_width/4, config.image_height*i+config.image_height/2), image_array[i][0], font=font)
        for j in range(len(image_array[i][1])):
            tiled_image.paste(im=image_array[i][1][j], box=((j+1)*config.image_width, i*config.image_height))
    
    # tiled_image.show()
    return tiled_image

# image = Image.open("images/test2image.jpg")

# image_array = [["test",[image,image,image]],["test2",[image,image]]]


# image_tiling(image_array)





    