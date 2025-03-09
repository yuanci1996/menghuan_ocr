import cv2
import numpy as np
import image_util
import time

now = time.time()
image = cv2.imread("text_image/wzg_text.png", cv2.IMREAD_GRAYSCALE)
loation = image_util.get_map_location(image)
print(f"{loation} 花费 {time.time() - now}")