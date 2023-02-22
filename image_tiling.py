import cv2
import numpy as np

def imageTiling():
    # Load the individual images to be tiled
    img1 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_1.jpg')
    img2 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_2.jpg')
    img3 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_3.jpg')
    img4 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_4.jpg')
    img5 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_5.jpg')
    img6 = cv2.imread('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/result_6.jpg')

    counter = 1
    # # Resize the images to the same size, if needed
    # img1 = cv2.resize(img1, (400, 400))

    # Create a numpy array with the individual images
    # images = np.array([img1, img2, img3])
    images = np.array([img1, img2, img3, img4, img5, img6])

    # Calculate the number of rows and columns needed to display the images
    rows = int(np.sqrt(images.shape[0]))
    cols = int(np.ceil(images.shape[0] / rows))

    # Create an empty black image with the required size
    tiled_image = np.zeros((rows*640, cols*640, 3), dtype=np.uint8)

    # Loop through the images and add them to the tiled image
    for i in range(rows):
        for j in range(cols):
            if i*cols + j >= images.shape[0]:
                break
            tiled_image[i*640:(i+1)*640, j*640:(j+1)*640, :] = images[i*cols + j]

    # Show the tiled image in a window
    cv2.imshow('Tiled Images', tiled_image)
    cv2.imwrite('/Users/shannenlee/Documents/GitHub/MDP_RPI_Communication/images/output.jpg', tiled_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()