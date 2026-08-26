# On-thi-cuoi-ky

📚 Web ôn thi trắc nghiệm **nhiều môn** .
Chạy bằng: `streamlit run web_on_tap.py`

## 📁 Cấu trúc thư mục

```
web_on_tap.py            <- file chính của app
requirements.txt         <- các thư viện cần cài
Triet-Hoc/
  └── triet_data.json    <- ngân hàng câu hỏi môn Triết học (bản đầy đủ nhất, 453 câu)
anh_co_vu/
  ├── anh_co_vu/         <- ảnh cổ vũ (đúng 5 câu liên tục -> hiện 1 ảnh ngẫu nhiên)
  └── anh_che_gieu/      <- ảnh chế giễu (sai 3 câu liên tục -> hiện 1 ảnh ngẫu nhiên)
```

## ➕ Thêm môn học mới 

1. Tạo thư mục môn học, ví dụ: `Toan-hoc/`
2. Bỏ file ngân hàng câu hỏi (JSON, cấu trúc giống `Triet-Hoc/triet_data.json`)
   vào thư mục đó, ví dụ: `Toan-hoc/toan_data.json`
3. Mở `web_on_tap.py`, thêm 1 dòng vào mục `MON_HOC`:

```python
MON_HOC = {
    "Triết học": {"thu_muc": "Triet-Hoc", "file_json": "triet_data.json"},
    "Toán học": {"thu_muc": "Toan-hoc", "file_json": "toan_data.json"},  # <- thêm dòng này
}
```

4. Commit & push lên GitHub là xong — dropdown bên trái tự động hiện môn mới.
   (Danh sách "câu sai" được lưu riêng cho từng môn, không lẫn nhau.)

## ▶️ Chạy local

```
pip install -r requirements.txt
streamlit run web_on_tap.py
```

## ☁️ Deploy lên Streamlit Cloud

1. Push repo lên GitHub.
2. Vào https://share.streamlit.io → Create app → chọn repo + nhánh `main`.
3. **Main file path**: `web_on_tap.py` → Deploy.

