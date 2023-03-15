from picamera import PiCamera
import time
import numpy as np
import config as config 

def take_picture():
        camera = PiCamera()
        camera.resolution = (config.rpi_image_height, config.rpi_image_width)
        print(camera.exposure_speed)
        camera.shutter_speed = 12500
        camera.exposure_mode = 'off'
        camera.framerate = 80
        output = np.empty((config.image_height, config.image_width, 3), dtype=np.uint8)
        camera.capture(output, 'rgb')
        camera.close()
        return output