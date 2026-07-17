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

# Lấy danh sách câu sai đã lưu từ trước trong trình duyệt của người đó (nếu có)
cac_cau_sai_da_luu = local_storage.getItem("cac_cau_sai")
if cac_cau_sai_da_luu is None:
    cac_cau_sai_da_luu = []
else:
    cac_cau_sai_da_luu = json.loads(cac_cau_sai_da_luu)

# --- PHẦN MENU CHỌN CHẾ ĐỘ HỌC ---
che_do = st.sidebar.radio("Chọn chế độ ôn tập:", ["Thi thử bộ đề chung", f"Luyện lại câu sai ({len(cac_cau_sai_da_luu)} câu)"])

# Xác định bộ đề sẽ chạy dựa trên chế độ chọn
bo_de_hien_tai = ngan_hang if "chung" in che_do else cac_cau_sai_da_luu

if not bo_de_hien_tai:
    st.info("Hiện tại bạn chưa có câu nào bị sai! Hãy chọn chế độ Thi thử bộ đề chung.")
else:
    if "danh_sach_cau" not in st.session_state or st.sidebar.button("Đổi lượt/Xáo bài"):
        st.session_state.danh_sach_cau = random.sample(bo_de_hien_tai, len(bo_de_hien_tai))
        st.session_state.chi_so_cau = 0
        st.session_state.da_tra_loi = False

    if st.session_state.chi_so_cau >= len(st.session_state.danh_sach_cau):
        st.success("🎉 Bạn đã hoàn thành lượt câu hỏi này!")
    else:
        cau_hien_tai = st.session_state.danh_sach_cau[st.session_state.chi_so_cau]
        st.subheader(f"Câu {st.session_state.chi_so_cau + 1}: {cau_hien_tai['cau_hoi']}")
        
        cac_lua_chon = [f"{k}. {v}" for k, v in cau_hien_tai["phuong_an"].items()]
        chon_lua = st.radio("Chọn đáp án của bạn:", cac_lua_chon, index=None)
        
        if st.button("Nộp bài") or st.session_state.da_tra_loi:
            if chon_lua is not None:
                st.session_state.da_tra_loi = True
                dap_an_user = chon_lua[0]
                
                if dap_an_user == cau_hien_tai["dap_an_dung"]:
                    st.success(" 正 Chính xác!")
                    # NẾU ĐANG Ở CHẾ ĐỘ LUYỆN CÂU SAI: Làm đúng câu nào, xóa câu đó khỏi danh sách câu sai vĩnh viễn
                    if "Luyện lại câu sai" in che_do and cau_hien_tai in cac_cau_sai_da_luu:
                        cac_cau_sai_da_luu.remove(cau_hien_tai)
                        local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
                else:
                    st.error(f" ✘ Sai rồi! Đáp án đúng là: {cau_hien_tai['dap_an_dung']}")
                    # NẾU ĐANG Ở CHẾ ĐỘ THI THỬ CHUNG: Làm sai thì mới thêm vào danh sách câu sai
                    if "Thi thử bộ đề chung" in che_do and cau_hien_tai not in cac_cau_sai_da_luu:
                        cac_cau_sai_da_luu.append(cau_hien_tai)
                        local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
                    
                st.info(f"**Giải thích:** {cau_hien_tai['giai_thich']}")
