from model import model 
import image_handling
from PIL import Image
import numpy as np
import time

m1 = model("weights/pls_work_1.pt")

m2 = model("weights/week_8_best.pt")

image_1 = Image.open("images/old_images/train_1677477845.7311687.jpg")
image_2 = Image.open("images/old_images/train_1677477958.3576334.jpg")
image_3 = Image.open("images/old_images/train_1677478067.7604969.jpg")
image_4 = Image.open("images/old_images/train_1677478113.1776884.jpg")
image_5 = Image.open("images/old_images/train_1677478152.7393823.jpg")
image_6 = Image.open("images/old_images/train_1677478200.4734597.jpg")
image_7 = Image.open("images/rsz_37marchtest.jpg")
image_8 = Image.open("images/old_images/test2image.jpg")
image_9 = Image.open("images/old_images/result_6.jpg")
image_10 = Image.open("images/old_images/6_img.jpg")
image_11 = Image.open("try_2/photo_6075840039377549090_x.jpg")
image_12 = Image.open("try/photo_6075840039377549041_x.jpg")
image_13 = Image.open("try/photo_6075840039377549040_x.jpg")

images = [image_1,image_2,image_3,image_4,image_5, image_6, image_7, image_8, image_9, image_10, image_11, image_12,image_13]

model_1 = []
model_2 = []
for image in images:
    np_image = image_handling.image_to_np_array(image)
    result_array_m1 = m1.get_results(np_image)
    result_array_m2 = m2.get_results(np_image)
    if len(result_array_m1) > 0 and len(result_array_m2) > 0:
        print(result_array_m1[0], result_array_m2[0])
    im1 = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array_m1)
    im2 = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array_m2)
    model_1.append(im1)
    model_2.append(im2)

model_1_array = ["model_1", model_1]
model_2_array = ["model_2", model_2]

tile_array = [model_1_array,["",[]],model_2_array]

resultant_img = image_handling.image_tiling(tile_array)

resultant_img.save("images/tiled_image.jpg")
# im1.save("images/old_images/result_old_model_5.jpg")
# im2.save("images/old_images/result_new_model_5.jpg")



# image_array = [["image",[image_1]],["image",[image_2]],["image",[image_3]],["image",[image_4]],["image",[image_5]]]

# a = image_handling.image_tiling(image_array)

# a.show()
