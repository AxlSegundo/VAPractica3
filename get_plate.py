import cv2
import numpy as np
import imutils

def main(impath):
    img = cv2.imread(impath, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (620, 480))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grey scale

    gray = cv2.bilateralFilter(gray, 13, 15, 15)
    edged = cv2.Canny(gray, 30, 200)  # Perform Edge detection

    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    for c in contours:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is not None:
        # Get bounding box for the contour
        x, y, w, h = cv2.boundingRect(screenCnt)
        
        # Crop the image to this bounding box
        roi = img[y:y+h, x:x+w]
        
        return roi
    else:
        return None
