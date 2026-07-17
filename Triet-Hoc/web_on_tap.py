import json
import random
import streamlit as st
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Thi Thử Triết Học", page_icon="📚")
st.title("📚 Ôn Thi Trắc Nghiệm Triết Học")

# Khởi tạo bộ lưu trữ cục bộ trên trình duyệt của người dùng
local_storage = LocalStorage()

@st.cache_data
def tai_ngan_hang_de():
    with open("Triet-Hoc/triet_data.json", "r", encoding="utf-8") as file:
        return json.load(file)

ngan_hang = tai_ngan_hang_de()

# Lấy danh sách câu sai đã lưu từ trước trong trình duyệt
cac_cau_sai_da_luu = local_storage.getItem("cac_cau_sai")
if cac_cau_sai_da_luu is None:
    cac_cau_sai_da_luu = []
else:
    cac_cau_sai_da_luu = json.loads(cac_cau_sai_da_luu)

# --- PHẦN MENU CHỌN CHẾ ĐỘ HỌC BÊN TRÁI ---
st.sidebar.header("Chế độ học")
che_do = st.sidebar.radio(
    "Bạn muốn làm gì?", 
    ["Thi thử vô tận", "Thi thử 50 câu", f"Luyện lại câu sai ({len(cac_cau_sai_da_luu)} câu)"]
)

# Xác định bộ đề hiện tại
if "50 câu" in che_do:
    # Tạo đề 50 câu mới nếu chưa có
    if "de_50_cau" not in st.session_state or st.session_state.che_do_cu != che_do:
        st.session_state.de_50_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
        st.session_state.diem_50_cau = 0
        st.session_state.so_cau_da_lam_50 = 0
        st.session_state.so_dap_an_dung = 0 
    bo_de_hien_tai = st.session_state.de_50_cau
elif "chung" in che_do or "vô tận" in che_do:
    bo_de_hien_tai = ngan_hang
else:
    bo_de_hien_tai = cac_cau_sai_da_luu

if not bo_de_hien_tai:
    st.info("Hiện tại bạn chưa có câu nào bị sai! Hãy chọn chế độ Thi thử bộ đề chung bên menu trái.")
else:
    # Tự động xáo bài và reset khi người dùng đổi chế độ ở menu
    if "che_do_cu" not in st.session_state or st.session_state.che_do_cu != che_do:
        # Chỉ xáo bài nếu không phải chế độ 50 câu (vì 50 câu đã xử lý riêng)
        if "50 câu" not in che_do:
            st.session_state.danh_sach_cau = random.sample(bo_de_hien_tai, len(bo_de_hien_tai))
        else:
            st.session_state.danh_sach_cau = st.session_state.de_50_cau
        st.session_state.chi_so_cau = 0
        st.session_state.da_tra_loi = False
        st.session_state.che_do_cu = che_do
        st.session_state.so_dap_an_dung = 0
        st.session_state.so_dap_an_dung = 0 # Đếm số câu đúng

    # Kiểm tra nếu đã làm hết các câu trong lượt hiện tại
    if st.session_state.chi_so_cau >= len(st.session_state.danh_sach_cau):
        if "50 câu" in che_do:
            # Hiển thị kết quả cho đề 50 câu
            st.balloons()
            st.success(f"🎉 Bạn đã hoàn thành đề 50 câu!")
            st.metric("Điểm số", f"{st.session_state.so_dap_an_dung}/{len(st.session_state.danh_sach_cau)}")
            st.metric("Tỷ lệ đúng", f"{st.session_state.so_dap_an_dung/len(st.session_state.danh_sach_cau)*100:.1f}%")
        else:
            st.success("🎉 Bạn đã hoàn thành lượt câu hỏi này!")
        
        if st.button("🔄 Làm lại từ đầu"):
            if "50 câu" in che_do:
                st.session_state.de_50_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
                st.session_state.danh_sach_cau = st.session_state.de_50_cau
            else:
                st.session_state.danh_sach_cau = random.sample(bo_de_hien_tai, len(bo_de_hien_tai))
            st.session_state.chi_so_cau = 0
            st.session_state.da_tra_loi = False
            st.session_state.so_dap_an_dung = 0
            st.rerun()
    else:
        cau_hien_tai = st.session_state.danh_sach_cau[st.session_state.chi_so_cau]
        
        # Hiển thị tiến độ cho đề 50 câu
        if "50 câu" in che_do:
            st.progress(st.session_state.chi_so_cau / len(st.session_state.danh_sach_cau))
            st.caption(f"Câu {st.session_state.chi_so_cau + 1}/{len(st.session_state.danh_sach_cau)}")
        
        st.subheader(f"Câu {st.session_state.chi_so_cau + 1}: {cau_hien_tai['cau_hoi']}")
        
        cac_lua_chon = [f"{k}. {v}" for k, v in cau_hien_tai["phuong_an"].items()]
        
        # Luôn hiển thị radio button, chỉ vô hiệu hóa khi đã trả lời
        chon_lua = st.radio(
            "Chọn đáp án của bạn:", 
            cac_lua_chon, 
            index=None,
            disabled=st.session_state.da_tra_loi
        )
        
        # Chỉ hiển thị nút Nộp bài nếu chưa trả lời
        if not st.session_state.da_tra_loi:
            if st.button("Nộp bài"):
                if chon_lua is not None:
                    st.session_state.da_tra_loi = True
                    st.session_state.cau_tra_loi_hien_tai = chon_lua[0]
                    st.rerun()
                else:
                    st.warning("Vui lòng chọn một đáp án trước khi nộp bài!")
        
        # Hiển thị kết quả và nút điều hướng khi đã trả lời
        if st.session_state.da_tra_loi and chon_lua is not None:
            dap_an_user = st.session_state.cau_tra_loi_hien_tai
            
            if dap_an_user == cau_hien_tai["dap_an_dung"]:
                st.success("✓ Chính xác!")
                st.session_state.so_dap_an_dung += 1  # Tăng điểm
                if "Luyện lại câu sai" in che_do and cau_hien_tai in cac_cau_sai_da_luu:
                    cac_cau_sai_da_luu.remove(cau_hien_tai)
                    local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
            else:
                st.error(f"✘ Sai rồi! Đáp án đúng là: {cau_hien_tai['dap_an_dung']}")
                if "Luyện lại câu sai" not in che_do and cau_hien_tai not in cac_cau_sai_da_luu:
                    cac_cau_sai_da_luu.append(cau_hien_tai)
                    local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
            
            st.info(f"**Giải thích:** {cau_hien_tai['giai_thich']}")
            
            # Hiển thị điểm hiện tại cho đề 50 câu
            if "50 câu" in che_do:
                st.metric("Điểm hiện tại", f"{st.session_state.so_dap_an_dung}/{st.session_state.chi_so_cau + 1}")
            
            # --- KHU VỰC CÁC NÚT ĐIỀU HƯỚNG ---
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➡️ Câu tiếp theo"):
                    st.session_state.chi_so_cau += 1
                    st.session_state.da_tra_loi = False
                    st.rerun()
            with col2:
                if st.button("🔄 Đổi lượt / Xáo bài ngay"):
                    if "50 câu" in che_do:
                        st.session_state.de_50_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
                        st.session_state.danh_sach_cau = st.session_state.de_50_cau
                    else:
                        st.session_state.danh_sach_cau = random.sample(bo_de_hien_tai, len(bo_de_hien_tai))
                    st.session_state.chi_so_cau = 0
                    st.session_state.da_tra_loi = False
                    st.session_state.so_dap_an_dung = 0
                    st.rerun()
