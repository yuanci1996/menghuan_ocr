import cv2
import numpy as np
import image_util

# 示例用法
if __name__ == "__main__":
    # 读取原图和模板图，转换为灰度图
    image = cv2.imread("text_image/zzg_text.png", cv2.IMREAD_GRAYSCALE)
    template = cv2.imread("key/3.png", cv2.IMREAD_GRAYSCALE)

    if image is None or template is None:
        print("读取图片失败，请检查路径！")
        exit()

    # 定义原图的放大比例（从 1.0 到 2.0，共 10 个尺度）
    scales = np.linspace(1, 10, num=10)[::-1]

    # 进行匹配
    matched_objects = image_util.pyramid_template_matching(image, template, scales, threshold=0.8)

    # 画出所有匹配结果
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if matched_objects:
        for (top_left, scale, match_val) in matched_objects:
            tH, tW = template.shape[:2]
            bottom_right = (top_left[0] + int(tW // scale), top_left[1] + int(tH // scale))
            cv2.rectangle(output, top_left, bottom_right, (0, 0, 255), 2)
            print(f"匹配得分：{match_val:.3f}，匹配尺度：{scale:.3f}，匹配位置：{top_left}")

        # 显示匹配结果
        cv2.imshow("匹配结果", output)
        cv2.waitKey(0)
    else:
        print("未找到匹配结果")
