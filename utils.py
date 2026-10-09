import cv2
import numpy as np

def nv21_to_bgr(nv21_data, w, h):
    nv21_height = h * 3 // 2
    if nv21_data.ndim == 1:
        data = nv21_data[:nv21_height * w].reshape((nv21_height, w))
    else:
        data = nv21_data
    bgr_img = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_NV21)
    return bgr_img

def focus_peaking(frame, threshold=100, blur_kernel_size=(5, 5)):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(img, blur_kernel_size, 0)

    gradient_x = cv2.Sobel(blurred_img, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(blurred_img, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(gradient_x ** 2 + gradient_y ** 2)

    gradient_8bit = np.uint8(gradient_magnitude)

    _, edges = cv2.threshold(gradient_8bit, threshold, 255, cv2.THRESH_BINARY)

    img_color = frame.copy()

    img_color[edges > 0] = [0, 0, 255]
    return img_color