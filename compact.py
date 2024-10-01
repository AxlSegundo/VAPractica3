import cv2
import numpy as np
from PIL import Image

def change_and_save(gscimage, threshold):
    image = np.where(gscimage > threshold, 255, 0).astype(np.uint8)
    #image = Image.fromarray(image)
    #image.save('output.png')
    return image

def load_image_and_convert_grayscale(input):
    #image_paths = 'img\\cropped_parking_lot_10.JPG'
    #img = cv2.imread(image_paths)
    img = input
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_array = np.array(gray)

    return image_array

def divide(gscimage, delta, limit = 50):
    threshold = np.mean(gscimage)
    count = 0
    while True:
        front = np.where(gscimage > threshold, gscimage, 0)
        back = np.where(gscimage <= threshold, gscimage, 0)
        meanF = np.mean(front[front>0])
        meanB = np.mean(back[back>0])
        newThreshold = (meanF + meanB) / 2

        if abs(newThreshold - threshold) < delta or count >= limit:
            return newThreshold
        threshold = newThreshold
        count += 1

def main(input):
    #To change image path, refer to load_image function
    image_array = load_image_and_convert_grayscale(input)
    umbral = divide(image_array, 1)
    image = change_and_save(image_array, umbral)
    return image

#main()