from model import model 
import image_handling
from PIL import Image

m1 = model("weights/best.pt")

m2 = model("weights/aug_best.pt")

image = Image.open("images/test2image.png")
np_image = image_handling.image_to_np_array(image)
result_array_m1 = m1.get_results(np_image)
result_array_m2 = m2.get_results(np_image)
print(result_array_m1)
print(result_array_m2)