from picamera import PiCamera
import time
import numpy as np
import config as config 

def take_picture():
        camera = PiCamera()
        camera.resolution = (config.rpi_image_height, config.rpi_image_width)
        camera.framerate = 80
        time.sleep(1)
        output = np.empty((config.image_height, config.image_width, 3), dtype=np.uint8)
        camera.capture(output, 'rgb', resize = (config.image_width, config.image_height))
        camera.close()
        return output