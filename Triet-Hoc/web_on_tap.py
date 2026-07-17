import json
import random
import streamlit as st
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Thi Thử Triết Học", page_icon="📚")
st.title("📚 Ôn Thi Trắc Nghiệm Triết Học")

local_storage = LocalStorage()

@st.cache_data
def tai_ngan_hang_de():
    with open("Triet-Hoc/triet_data.json", "r", encoding="utf-8") as file:
        return json.load(file)

ngan_hang = tai_ngan_hang_de()

cac_cau_sai_da_luu = local_storage.getItem("cac_cau_sai")
if cac_cau_sai_da_luu is None:
    cac_cau_sai_da_luu = []
else:
    cac_cau_sai_da_luu = json.loads(cac_cau_sai_da_luu)

st.sidebar.header("Chế độ học")
che_do = st.sidebar.radio(
    "Bạn muốn làm gì?", 
    ["Thi thử vô tận", "Thi thử 50 câu", f"Luyện lại câu sai ({len(cac_cau_sai_da_luu)} câu)"],
     key="che_do_radio"
)

# Reset toàn bộ khi đổi chế độ
if "che_do_cu" not in st.session_state or st.session_state.che_do_cu != che_do:
    st.session_state.che_do_cu = che_do
    st.session_state.chi_so_cau = 0
    st.session_state.da_tra_loi = False
    st.session_state.so_dap_an_dung = 0
    if "da_cong_diem" in st.session_state:
        del st.session_state.da_cong_diem
    
    if "50 câu" in che_do:
        st.session_state.danh_sach_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
        st.session_state.de_50_cau = st.session_state.danh_sach_cau
    elif "vô tận" in che_do:
        st.session_state.danh_sach_cau = random.sample(ngan_hang, len(ngan_hang))
        st.session_state.de_50_cau = None
    else:
        st.session_state.danh_sach_cau = random.sample(cac_cau_sai_da_luu, len(cac_cau_sai_da_luu))
        st.session_state.de_50_cau = None

if not st.session_state.danh_sach_cau:
    st.info("Hiện tại bạn chưa có câu nào bị sai! Hãy chọn chế độ Thi thử bộ đề chung bên menu trái.")
else:
    if st.session_state.chi_so_cau >= len(st.session_state.danh_sach_cau):
        if "50 câu" in che_do:
            st.balloons()
            st.success(f"🎉 Bạn đã hoàn thành đề 50 câu!")
            st.metric("Điểm số", f"{st.session_state.so_dap_an_dung}/{len(st.session_state.danh_sach_cau)}")
            st.metric("Tỷ lệ đúng", f"{st.session_state.so_dap_an_dung/len(st.session_state.danh_sach_cau)*100:.1f}%")
        else:
            st.success("🎉 Bạn đã hoàn thành lượt câu hỏi này!")
        
        if st.button("🔄 Làm lại từ đầu"):
            if "50 câu" in che_do:
                st.session_state.danh_sach_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
                st.session_state.de_50_cau = st.session_state.danh_sach_cau
            elif "vô tận" in che_do:
                st.session_state.danh_sach_cau = random.sample(ngan_hang, len(ngan_hang))
            else:
                st.session_state.danh_sach_cau = random.sample(cac_cau_sai_da_luu, len(cac_cau_sai_da_luu))
            st.session_state.chi_so_cau = 0
            st.session_state.da_tra_loi = False
            st.session_state.so_dap_an_dung = 0
            st.rerun()
    else:
        cau_hien_tai = st.session_state.danh_sach_cau[st.session_state.chi_so_cau]
        
        if "50 câu" in che_do:
            st.progress(st.session_state.chi_so_cau / len(st.session_state.danh_sach_cau))
            st.caption(f"Câu {st.session_state.chi_so_cau + 1}/{len(st.session_state.danh_sach_cau)}")
        
        st.subheader(f"Câu {st.session_state.chi_so_cau + 1}: {cau_hien_tai['cau_hoi']}")
        
        cac_lua_chon = [f"{k}. {v}" for k, v in cau_hien_tai["phuong_an"].items()]
        
        chon_lua = st.radio(
            "Chọn đáp án của bạn:", 
            cac_lua_chon, 
            index=None,
            disabled=st.session_state.da_tra_loi
        )
        
        if not st.session_state.da_tra_loi:
            if st.button("Nộp bài"):
                if chon_lua is not None:
                    st.session_state.da_tra_loi = True
                    st.session_state.cau_tra_loi_hien_tai = chon_lua[0]
                    st.rerun()
                else:
                    st.warning("Vui lòng chọn một đáp án trước khi nộp bài!")
        
        if st.session_state.da_tra_loi and chon_lua is not None:
            dap_an_user = st.session_state.cau_tra_loi_hien_tai
            
            if dap_an_user == cau_hien_tai["dap_an_dung"]:
                st.success("✓ Chính xác!")
                if "50 câu" in che_do and "da_cong_diem" not in st.session_state:
                    st.session_state.so_dap_an_dung += 1
                    st.session_state.da_cong_diem = True
                if "Luyện lại câu sai" in che_do and cau_hien_tai in cac_cau_sai_da_luu:
                    cac_cau_sai_da_luu.remove(cau_hien_tai)
                    local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
            else:
                st.error(f"✘ Sai rồi! Đáp án đúng là: {cau_hien_tai['dap_an_dung']}")
                if "Luyện lại câu sai" not in che_do and cau_hien_tai not in cac_cau_sai_da_luu:
                    cac_cau_sai_da_luu.append(cau_hien_tai)
                    local_storage.setItem("cac_cau_sai", json.dumps(cac_cau_sai_da_luu))
            
            st.info(f"**Giải thích:** {cau_hien_tai['giai_thich']}")
            
            if "50 câu" in che_do:
                st.metric("Điểm hiện tại", f"{st.session_state.so_dap_an_dung}/{st.session_state.chi_so_cau + 1}")
            
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                 if st.button("➡️ Câu tiếp theo"):
                    st.session_state.chi_so_cau += 1
                    st.session_state.da_tra_loi = False
                    if "da_cong_diem" in st.session_state:
                        del st.session_state.da_cong_diem
                    st.rerun()
            with col2:
                if st.button("🔄 Đổi lượt / Xáo bài ngay"):
                    if "50 câu" in che_do:
                        st.session_state.danh_sach_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
                        st.session_state.de_50_cau = st.session_state.danh_sach_cau
                    elif "vô tận" in che_do:
                        st.session_state.danh_sach_cau = random.sample(ngan_hang, len(ngan_hang))
                    else:
                        st.session_state.danh_sach_cau = random.sample(cac_cau_sai_da_luu, len(cac_cau_sai_da_luu))
                    st.session_state.chi_so_cau = 0
                    st.session_state.da_tra_loi = False
                    st.session_state.so_dap_an_dung = 0
                    st.rerun()
