from model import model 
import image_handling
from PIL import Image
import numpy as np



m1 = model("weights/epoch_148.pt")

m2 = model("weights/epoch_152.pt")

image_1 = Image.open("images/old_images/train_1677477845.7311687.jpg")
image_2 = Image.open("images/old_images/train_1677477958.3576334.jpg")
image_3 = Image.open("images/old_images/train_1677478067.7604969.jpg")
image_4 = Image.open("images/old_images/train_1677478113.1776884.jpg")
image_5 = Image.open("images/old_images/train_1677478152.7393823.jpg")
image_6 = Image.open("images/old_images/train_1677478200.4734597.jpg")
image_7 = Image.open("images/old_images/raw_result_1.jpg")
                     
image_1 = Image.open("images/old_images/test2image.jpg")
image_2 = Image.open("images/old_images/result_6.jpg")
image_3 = Image.open("images/old_images/6_img.jpg")
image_4 = Image.open("images/old_images/image3.jpg")
image_5 = Image.open("images/old_images/result_2.jpg")

images = [image_1,image_2,image_3,image_4,image_5, image_6, image_7]
new_model = []
old_model = []
for image in images:
    np_image = image_handling.image_to_np_array(image)
    result_array_m1 = m1.get_results(np_image)
    result_array_m2 = m2.get_results(np_image)
    print("Old Model results")
    print(result_array_m1)
    im1 = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array_m1)
    im2 = image_handling.draw_bbox(image_handling.np_array_to_image(np_image), result_array_m2)
    old_model.append(im1)
    new_model.append(im2)

new_model_array = ["new_model", new_model]
old_model_array = ["old_model", old_model]

tile_array = [new_model_array, old_model_array]

resultant_img = image_handling.image_tiling(tile_array)

resultant_img.save("images/tiled_image.jpg")
im1.save("images/old_images/result_old_model_5.jpg")
im2.save("images/old_images/result_new_model_5.jpg")



# # image_array = [["image",[image_1]],["image",[image_2]],["image",[image_3]],["image",[image_4]],["image",[image_5]]]

# # a = image_handling.image_tiling(image_array)

# # a.show()
