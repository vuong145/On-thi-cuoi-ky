# On-thi-cuoi-ky

📚 Web ôn thi hỗn hợp **trắc nghiệm + tự luận**.  
Chạy bằng: `streamlit run web_on_tap.py`

## 📁 Cấu trúc thư mục

```text
web_on_tap.py
requirements.txt

Triet-Hoc/
  triet_data.json                  # dữ liệu trắc nghiệm Triết học (legacy)

Luat-Kinh-Doanh/
  questions.json                   # ngân hàng câu hỏi tự luận
  exams/
    de_01.json                     # đề tham chiếu bằng question_id

Toan-cho-DS/
  questions.json
  exams/
    de_01.json

Xac-Suat-Thong-Ke/
  questions.json
  exams/
    de_01.json

anh_co_vu/
  anh_co_vu/
  anh_che_gieu/
```

## ✨ Chế độ hiện có

- **Triết học (trắc nghiệm)**:
  - Thi thử vô tận
  - Thi thử 50 câu
  - Luyện lại câu sai
- **3 môn mới (tự luận)**:
  - Làm một đề đầy đủ
  - Luyện từng câu

## ➕ Thêm môn tự luận mới

1. Tạo thư mục môn mới, ví dụ: `Mon-Moi/`
2. Thêm `questions.json` (mỗi câu có `id` duy nhất)
3. Tạo `exams/` và các file đề JSON
4. Trong mỗi đề, chỉ tham chiếu câu bằng `question_id` (không lặp lại toàn bộ nội dung câu)
5. Thêm cấu hình môn vào `MON_HOC` trong `web_on_tap.py`:

```python
"Môn mới": {
    "thu_muc": "Mon-Moi",
    "file_cau_hoi": "questions.json",
    "thu_muc_de_thi": "exams",
    "loai": "tu_luan",
}
```

## ▶️ Chạy local

```bash
pip install -r requirements.txt
streamlit run web_on_tap.py
```

## ☁️ Deploy Streamlit Cloud

1. Push repo lên GitHub.
2. Vào https://share.streamlit.io → Create app → chọn repo + nhánh `main`.
3. **Main file path**: `web_on_tap.py` → Deploy.
