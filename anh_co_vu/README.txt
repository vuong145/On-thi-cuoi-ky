# 📁 THƯ MỤC ẢNH (anh_co_vu)

Trong thư mục này có **2 thư mục con**:
- `anh_co_vu/`      → **ảnh cổ vũ** — đúng 5 câu liên tục → hiện 1 ảnh ngẫu nhiên
- `anh_che_gieu/`   → **ảnh chế giễu** — sai 3 câu liên tục → hiện 1 ảnh ngẫu nhiên

## 📤 Cách thêm ảnh để mọi người xem được trên Streamlit Cloud

1. Bỏ ảnh/GIF/video ngắn (.png .jpg .jpeg .gif .webp .bmp .mp4 .webm .ogg .mov)
   vào 1 trong 2 thư mục con ở trên (đặt tên không dấu, VD: anh1.png, video1.mp4).
2. Commit và push lên GitHub:
       git add anh_co_vu
       git commit -m "Them anh co vu / che gieu"
       git push origin main
3. Đợi Streamlit Cloud tự redeploy (1-2 phút).

⚠️ Ghi chú: chỉ bỏ ảnh ở máy local thì Streamlit Cloud KHÔNG có ảnh.
Ảnh phải nằm trong repo GitHub thì mọi người mới thấy được.

