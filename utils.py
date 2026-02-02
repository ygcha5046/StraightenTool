# utils.py
import cv2
import numpy as np

def rotate_image(image, angle, background_color=(255,255,255)):
    """
    이미지 중심 기준으로 rotation (angle: degrees, + 이면 반시계)
    배경색은 기본 흰색.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # 회전 후 전체 이미지가 들어가도록 bounding box 계산
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    # 이동 보정
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    rotated = cv2.warpAffine(image, M, (new_w, new_h),
                             borderValue=background_color,
                             flags=cv2.INTER_LINEAR)
    return rotated
