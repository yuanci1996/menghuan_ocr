import cv2
import numpy as np
import image_util
# pip install opencv-contrib-python --index-url https://mirrors.aliyun.com/pypi/simple/
# 读取图片
image = cv2.imread("image/zzg.png")

# 转换到 HSV 色彩空间
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义不同颜色文字的 HSV 阈值
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 30, 255])

# lower_yellow = np.array([20, 100, 100])
# upper_yellow = np.array([40, 255, 255])
lower_red2 = np.array([170, 100, 100])
upper_red2 = np.array([180, 255, 255])

# 颜色分割
# mask_white = cv2.inRange(hsv, lower_white, upper_white)
# mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

lower_yellow = np.array([25, 35, 150])
upper_yellow = np.array([35, 255, 255])
mask_yellow1 = cv2.inRange(hsv, lower_yellow, upper_yellow)
cv2.imshow("mask_yellow1", mask_yellow1)

lower_red1 = np.array([0, 35, 150])
upper_red1 = np.array([10, 255, 255])
mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

# mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

cv2.imshow("mask_red1", mask_red1)
# cv2.imshow("mask_red2", mask_red2)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 合并所有文字的二值化结果
# mask = cv2.bitwise_or(mask_yellow, mask_red2)
# mask = cv2.bitwise_or(mask, mask_red2)
#
# # 形态学操作，去除小噪声
# kernel = np.ones((3, 3), np.uint8)
# mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#
# # 文字区域
# text_region = cv2.bitwise_and(image, image, mask=mask)
#
# # 保存或显示结果
# cv2.imshow("Text Mask", mask)
# cv2.imshow("Extracted Text", text_region)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

