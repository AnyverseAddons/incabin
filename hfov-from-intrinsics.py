import numpy as np
import cv2

image_width = 800
image_height = 650
cx = 400
cy = 325
fx = 394
fy = 304.5
k1 = -0.137631404039
k2 = 0.1114321731
k3 = -0.030054425
k4 = 0

# Intrinsics
K = np.array([[fx, 0, cx],
              [0, fy, cy],
              [0,  0,  1]])
D = np.array([k1, k2, k3, k4])  # Fisheye distortion coefficients
W = image_width  # Image width in pixels
H = image_height

# Undistort left and right image points (on image center line)
pts = np.array([[[0, cy]], [[W-1, cy]]], dtype=np.float32)
print(pts)

undistorted = cv2.fisheye.undistortPoints(pts, K, D)
undistorted = cv2.undistortPoints(pts, K, D)
print(undistorted)
left_vec = undistorted[0,0]
right_vec = undistorted[1,0]

# Calculate angle between two direction vectors
dot_product = np.dot(left_vec, right_vec)
print(dot_product)
dot_product = np.clip(dot_product, -1.0, 1.0)  # Ensure safe arccos
print(dot_product)
hfov_rad = np.arccos(dot_product)
hfov_deg = np.degrees(hfov_rad)

print(f"Horizontal FOV ≈ {hfov_deg:.2f} degrees")
