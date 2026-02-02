# modes.py
import cv2
import numpy as np
from utils import rotate_image

def get_dominant_angle_from_lines(lines):
    """
    허프라인 결과에서 각도(도)를 추출하여 중앙값을 반환
    """
    angles = []
    if lines is None:
        return 0.0
    for x1, y1, x2, y2 in lines.reshape(-1,4):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            angle = 90.0
        else:
            angle = np.degrees(np.arctan2(dy, dx))
        # normalize angle to [-90,90]
        if angle > 90:
            angle -= 180
        if angle <= -90:
            angle += 180
        angles.append(angle)
    if len(angles) == 0:
        return 0.0
    # use median for robustness
    return float(np.median(angles))

def auto_straighten(image, debug=False):
    """
    자동 보정: 에지 추출 -> 허프랜 검출 -> dominant angle -> rotate to make lines horizontal
    반환: rotated_image, angle_applied (degrees)
    """
    # 그레이스케일
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 블러로 노이즈 제거
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    # 엣지
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    # 확장/수축으로 엣지 굵기 조정 (선택적)
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    # Probabilistic HoughLinesP
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50,
                            minLineLength=min(image.shape[:2])//10, maxLineGap=20)
    angle = get_dominant_angle_from_lines(lines)
    # 우리가 "수평으로 만들기"를 원하면 angle의 부호 반대만큼 회전
    to_rotate = -angle
    rotated = rotate_image(image, to_rotate)
    if debug:
        return rotated, to_rotate, edges, lines
    return rotated, to_rotate

def manual_straighten(image, angle):
    """
    사용자가 입력한 각도(angle)를 그대로 적용 (회전)
    angle: degrees (양수는 반시계)
    """
    rotated = rotate_image(image, angle)
    return rotated, angle

def batch_process(input_paths, output_folder, mode='auto', manual_angle=0.0, debug=False):
    """
    파일 목록을 받아서 일괄 처리.
    input_paths: 리스트(파일 경로)
    output_folder: 저장할 폴더
    mode: 'auto' | 'manual'
    manual_angle: 수동 모드 각도
    반환: list of dict {in, out, angle, ok}
    """
    import os
    results = []
    for p in input_paths:
        try:
            img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                raise RuntimeError("이미지 로드 실패")
            if mode == 'auto':
                out_img, angle = auto_straighten(img)
            else:
                out_img, angle = manual_straighten(img, manual_angle)
            # 저장 (한글 경로 안전)
            basename = os.path.splitext(os.path.basename(p))[0]
            out_path = os.path.join(output_folder, f"{basename}_straightened.png")
            # cv2.imwrite는 유니코드 경로에서 문제 => np.tofile 사용
            _, buf = cv2.imencode('.png', out_img)
            buf.tofile(out_path)
            results.append({"in": p, "out": out_path, "angle": angle, "ok": True})
        except Exception as e:
            results.append({"in": p, "out": None, "angle": None, "ok": False, "error": str(e)})
    return results
