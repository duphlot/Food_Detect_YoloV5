import cv2

# Mở video AVI
input_file = 'input_video.avi'
output_file = 'output_video.mp4'

# Đọc video
cap = cv2.VideoCapture(input_file)

# Lấy thông tin về độ rộng, độ cao và fps của video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Khởi tạo writer để lưu video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' cho định dạng MP4
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)  # Ghi frame vào video MP4

# Giải phóng tài nguyên
cap.release()
out.release()
cv2.destroyAllWindows()

print("Video đã được chuyển đổi sang định dạng MP4.")
