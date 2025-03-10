import os
import cv2
import numpy as np
from matplotlib import pyplot as plt

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))

# pip install opencv-python --index-url https://mirrors.aliyun.com/pypi/simple/

def show_image(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)


def show_image_plt(title, img):
    plt.title(title)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.ion()
    plt.axis('on')
    plt.show()


def feature_based_alignment(padded_origin, padded_test):
    # 初始化 ORB 检测器
    orb = cv2.ORB.create()
    # 提取特征点和描述子
    keypoints1, descriptors1 = orb.detectAndCompute(padded_origin, None)
    keypoints2, descriptors2 = orb.detectAndCompute(padded_test, None)

    # 特征点匹配
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # 提取匹配点
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches])
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches])

    # 计算仿射变换
    matrix, _ = cv2.estimateAffinePartial2D(points2, points1)

    # 对齐图像
    aligned_image2 = cv2.warpAffine(padded_test, matrix, (padded_origin.shape[1], padded_origin.shape[0]),
                                    flags=cv2.INTER_NEAREST)
    return aligned_image2


def feature_based_alignment2(padded_origin, padded_test):
    # 初始化 ORB 检测器
    orb = cv2.ORB.create()

    # 提取特征点和描述子
    keypoints1, descriptors1 = orb.detectAndCompute(padded_origin, None)
    keypoints2, descriptors2 = orb.detectAndCompute(padded_test, None)

    # 特征点匹配
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # 复制图像，便于绘制
    padded_origin_marked = padded_origin.copy()
    padded_test_marked = padded_test.copy()

    # 遍历所有匹配，在两幅图像上绘制红色圆点
    for idx, match in enumerate(matches):
        # image1 中匹配点的坐标
        pt1 = tuple(np.int32(keypoints1[match.queryIdx].pt))
        # image2 中匹配点的坐标
        pt2 = tuple(np.int32(keypoints2[match.trainIdx].pt))

        # 生成随机颜色，生成三个 0-255 之间的随机整数，注意颜色顺序为 BGR
        color = tuple(np.random.randint(0, 256, size=3).tolist())

        # 绘制红色圆点，颜色为 (0, 0, 255)
        cv2.circle(padded_origin_marked, pt1, radius=4, color=color, thickness=-1)
        cv2.circle(padded_test_marked, pt2, radius=4, color=color, thickness=-1)

    show_image("padded_origin_marked", padded_origin_marked)
    show_image("padded_test_marked", padded_test_marked)

    # 提取匹配点（转换成适合 findHomography 的形状）
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # 计算透视变换矩阵，使用 RANSAC 来提高鲁棒性
    matrix, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

    # 对齐图像，使用 warpPerspective 而非 warpAffine
    aligned_image2 = cv2.warpPerspective(padded_test, matrix,
                                         (padded_origin.shape[1], padded_origin.shape[0]),
                                         flags=cv2.INTER_NEAREST)
    return aligned_image2


def split_contour(image):
    # 高斯模糊去噪
    gs_blur = cv2.GaussianBlur(image, (5, 5), 0)
    # 双边滤波
    blur = cv2.bilateralFilter(gs_blur, 9, 75, 75)
    # 转为灰度图像
    gray_image = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

    # 阈值处理，生成二值图像
    th3 = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    # 使用 Canny 边缘检测
    edges = cv2.Canny(th3, 15, 50)
    # 形态学转换 闭运算
    edges_close = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    # 轮廓
    contours, _ = cv2.findContours(edges_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = max(contours, key=cv2.contourArea)
    return largest_contour


def split_image(image):
    largest_contour = split_contour(image)

    # 获取轮廓的边界框
    x1, y1, w1, h1 = cv2.boundingRect(largest_contour)
    roi1 = image[y1:y1 + h1, x1:x1 + w1]  # 裁剪出感兴趣区域 (ROI)

    # 创建空白掩膜并绘制轮廓
    mask1 = np.zeros((h1, w1), dtype="uint8")
    draw_contour = [largest_contour - [x1, y1]]
    cv2.drawContours(mask1, draw_contour, -1, 255, thickness=cv2.FILLED)

    # 计算非轮廓区域的平均颜色
    non_contour_pixels = roi1[mask1 == 0]  # 掩膜外部的像素点
    if non_contour_pixels.size > 0:
        mean_color = np.mean(non_contour_pixels, axis=0)  # 计算平均颜色
    else:
        mean_color = [0, 0, 0]  # 如果没有非轮廓区域，使用默认黑色

    # 创建一个与 ROI 区域大小相同的图像，并填充为平均颜色
    background = np.full_like(roi1, mean_color, dtype="uint8")

    # 合成最终图像，保留轮廓内部像素，非轮廓区域使用平均颜色
    cropped1 = cv2.bitwise_and(roi1, roi1, mask=mask1)  # 保留轮廓内部像素
    mask1_inv = cv2.bitwise_not(mask1)  # 生成掩膜的反向
    background = cv2.bitwise_and(background, background, mask=mask1_inv)  # 填充背景
    result = cv2.add(cropped1, background)  # 合成结果
    # th4 = cv2.adaptiveThreshold(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                             cv2.THRESH_BINARY, 5, 2)
    return result, draw_contour


def abs_diff(padded_origin, padded_test, type=""):
    print("padded_origin shape:", padded_origin.shape)
    print("padded_test shape:", padded_test.shape)
    # 检查并调整尺寸
    if padded_origin.shape[:2] != padded_test.shape[:2]:
        padded_test = cv2.resize(padded_test, (padded_origin.shape[1], padded_origin.shape[0]))

    diff = cv2.absdiff(padded_origin, padded_test)
    show_image("diff_" + type, diff)
    diff_sum = np.sum(diff, axis=2)  # 对 LAB 三个通道的差异求和
    # 将 diff_sum 转换为 float32 以便于归一化
    diff_sum = diff_sum.astype(np.float32)
    # 归一化颜色差异（0-255）
    diff_visualization = cv2.normalize(diff_sum, None, 0, 255, cv2.NORM_MINMAX)
    # 将结果转换回 uint8
    diff_visualization = diff_visualization.astype("uint8")
    # 统计颜色差异信息
    mean_diff = np.mean(diff_sum)  # 平均差异
    max_diff = np.max(diff_sum)  # 最大差异
    print(f"平均差异{type}:  {mean_diff} ,最大差异{type}: {max_diff}")
    show_image("abs_diff_" + type, diff_visualization)


def auto_canny(image, sigma=0.33):
    # 计算图像中位数
    v = np.median(image)
    # 根据中位数计算低、高阈值
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    return edged


color_thresholds = 35

colors = [
    {"key": "red_lower", "value": [np.array([0, color_thresholds, color_thresholds]), np.array([10, 255, 255])]},
    {"key": "orange", "value": [np.array([10, color_thresholds, color_thresholds]), np.array([25, 255, 255])]},
    {"key": "yellow",
     "value": [np.array([25, color_thresholds, color_thresholds]), np.array([color_thresholds, 255, 255])]},
    {"key": "green", "value": [np.array([35, color_thresholds, color_thresholds]), np.array([85, 255, 255])]},
    {"key": "cyan", "value": [np.array([85, color_thresholds, color_thresholds]), np.array([100, 255, 255])]},
    {"key": "blue", "value": [np.array([100, color_thresholds, color_thresholds]), np.array([140, 255, 255])]},
    {"key": "purple", "value": [np.array([140, color_thresholds, color_thresholds]), np.array([160, 255, 255])]},
    {"key": "pink", "value": [np.array([160, color_thresholds, color_thresholds]), np.array([170, 255, 255])]},
    {"key": "red_upper", "value": [np.array([170, color_thresholds, color_thresholds]), np.array([180, 255, 255])]},
    {"key": "black", "value": [np.array([0, 0, 0]), np.array([180, 255, color_thresholds])]},
    {"key": "white", "value": [np.array([0, 0, 200]), np.array([180, color_thresholds, 255])]},
    {"key": "gray", "value": [np.array([0, 0, color_thresholds]), np.array([180, color_thresholds, 200])]},
]


def get_color_distribution_in_contour(image, contour, colors):
    # 创建一个与图像大小相同的掩码
    # show_image_plt("image", image)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, contour, -1, [255, 255, 255], -1)
    # show_image_plt("mask", mask)

    # 将图像转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 初始化颜色分布列表
    color_distribution = []

    # 遍历每个颜色区间
    for color in colors:
        value_list = color['value']
        # 创建颜色掩码
        color_mask = cv2.inRange(hsv_image, value_list[0], value_list[1])
        # 与轮廓掩码进行与操作，得到轮廓内的颜色区域
        contour_color_mask = cv2.bitwise_and(mask, color_mask)
        # 计算该颜色区域内的像素数量
        count = np.count_nonzero(contour_color_mask)
        # show_image_plt(color['key'] + " - " + str(count), contour_color_mask)
        # 添加到分布列表中
        color_distribution.append({"key": color['key'], "count": count, })

    return color_distribution


def pyramid_template_matching(image,
                              template,
                              scales=(8.5, 8, 7, 7.5, 6),
                              threshold=0.8,
                              proximity_threshold=5):
    """
    在不同尺度上对原图进行缩放，并进行模板匹配，返回所有匹配的结果
    :param image:待匹配的原图（灰度图）
    :param template:模板图像（灰度图）
    :param scales:原图缩放因子列表，例如 np.linspace(1.0, 2.0, num=10)
    :param threshold:设定的匹配阈值（0~1），超过该值的匹配才会被记录
    :param proximity_threshold: 去重时的距离阈值，单位：像素
    :return: (matched_objects) 包含多个匹配位置、匹配尺度、匹配得分的信息
    """
    matched_objects = []
    matched_locations = np.empty((0, 2), dtype=int)  # Stores matched locations as a numpy array

    for scale in scales:
        # 按当前尺度缩放原图
        resized_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        if resized_image.shape[0] < template.shape[0] or resized_image.shape[1] < template.shape[1]:
            break  # 停止继续缩小

        # print(f"当前尺度：{scale}，缩放后原图尺寸：{resized_image.shape}")

        # 进行模板匹配
        result = cv2.matchTemplate(resized_image, template, cv2.TM_CCOEFF_NORMED)

        # 找出所有匹配度大于阈值的点
        locations = np.where(result >= threshold)

        for loc in zip(*locations[::-1]):  # 解析匹配的坐标
            # 映射回原始尺度
            original_loc = (int(loc[0] / scale), int(loc[1] / scale))

            # Check if the current location is too close to any of the previous matched locations
            if len(matched_locations) > 0:
                # Calculate the absolute difference in x and y coordinates
                diff = np.abs(matched_locations - original_loc)

                # Check if the difference in both x and y is below the proximity threshold (5 pixels)
                if np.all(diff <= proximity_threshold, axis=1).any():
                    continue  # Skip this duplicate match

            # If not duplicate, add to the list
            matched_objects.append((original_loc,
                                    (int(template.shape[1] / scale), int(template.shape[0] / scale)),
                                    scale,
                                    result[loc[1], loc[0]]))
            matched_locations = np.vstack([matched_locations, original_loc])  # Add new location

        # 可选择性地添加停止条件，避免不必要的多次迭代
        if len(matched_objects) > 0:
            break

    return matched_objects


def get_map_image(image, color_type='yellow'):
    if color_type == 'yellow':
        return cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV),
                           np.array([25, 35, 150]),
                           np.array([35, 255, 255]))
    else:
        return cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV),
                           np.array([170, 100, 100]),
                           np.array([180, 255, 255]))


map_keys = [
    ('傲来国', 'alg'),
    ('宝象国', 'bxg'),
    ('长寿村', 'csc'),
    ('大唐境外', 'dtjw'),
    ('建邺城', 'jyc'),
    ('江南野外', 'jnyw'),
    ('女儿村', 'nec'),
    ('普陀山', 'pts'),
    ('五庄观', 'wzg'),
    ('西凉女国', 'xlng'),
    ('朱紫国', 'zzg'),
]

def is_overlap(obj1, obj2):
    """
    判断两个矩形区域是否存在重叠
    :param obj1: (x, y, w, h) -> 第一个矩形 (map_location)
    :param obj2: (x, y, w, h) -> 第二个矩形 (matched_object)
    :return: True/False 是否重叠
    """
    x1, y1, w1, h1 = obj1
    x2, y2, w2, h2 = obj2

    # 计算矩形的边界
    left1, right1, top1, bottom1 = x1, x1 + w1, y1, y1 + h1
    left2, right2, top2, bottom2 = x2, x2 + w2, y2, y2 + h2

    # 判断是否有重叠
    if right1 > left2 and right2 > left1 and bottom1 > top2 and bottom2 > top1:
        return True  # 存在重叠
    return False  # 无重叠


def get_map_location(image):
    # x, y, w, h, map_name
    map_location = None

    for map_name, map_key in map_keys:
        path = os.path.normpath(os.path.join(project_root, "static", "images", "key", f"{map_key}.png"))
        template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # print("开始匹配" + map_key)
        matched_objects = pyramid_template_matching(image,
                                                    template)
        if len(matched_objects) > 0:
            print("匹配地图位置：", matched_objects)
            (x, y), (w, h), _, _ = matched_objects[0]
            map_location = [x, y, w, h, map_name]
            break

    if map_location is None:
        return '', 0, 0
    image = image[map_location[1]:map_location[1] + map_location[3] * 2, :]
    map_location[1] = 0
    show_image("新地图文字：", image)
    num_locations = []

    for i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'dh']:
        path = os.path.normpath(os.path.join(project_root, "static", "images", "key", f"{i}.png"))
        template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        matched_objects = pyramid_template_matching(image,
                                                    template)
        if len(matched_objects) > 0:
            print(f"匹配{i}：", matched_objects)
            for matched_object in matched_objects:
                (x, y), (w, h), _, _ = matched_object
                if is_overlap((x, y, w, h), (map_location[0], map_location[1], map_location[2], map_location[3])):
                    print(f"匹配到的{i}与地图范围存在重叠：", matched_object)
                else:
                    num_locations.append((x, i))

    # print(num_locations)
    # 按 x 从小到大排序
    sorted_data = sorted(num_locations, key=lambda item: item[0])

    # 找到 'dh' 的索引
    split_index = next((i for i, (x, key) in enumerate(sorted_data) if key == 'dh'), None)

    # 分割列表
    if split_index is not None:
        part1 = sorted_data[:split_index]  # 'dh' 之前的部分
        part2 = sorted_data[split_index + 1:]  # 'dh' 之后的部分
    else:
        part1 = sorted_data
        part2 = []

    # 提取 key 并组合成数字
    location_x = ''.join([key for (x, key) in part1])
    location_y = ''.join([key for (x, key) in part2])

    # 打印结果
    print(f"map_name: {map_location[4]}, x: {location_x}, y: {location_y}")
    return map_location[4], int(location_x), int(location_y)
