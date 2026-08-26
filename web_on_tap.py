import json
import os
import random

import streamlit as st
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Ôn Thi Trắc Nghiệm", page_icon="📚")
st.title("📚 Ôn Thi Trắc Nghiệm")

# Bộ lưu trữ cục bộ trên trình duyệt của người dùng
local_storage = LocalStorage()

# ======================================================================
# 📖 DANH SÁCH MÔN HỌC
# ----------------------------------------------------------------------
# MUỐN THÊM MÔN MỚI, chỉ cần làm 3 bước:
#   1. Tạo thư mục môn học trong repo, ví dụ:  Toan-hoc/
#   2. Bỏ file ngân hàng câu hỏi (JSON, cấu trúc giống triet_data.json)
#      vào thư mục đó, ví dụ:                  Toan-hoc/toan_data.json
#   3. Thêm 1 dòng vào MON_HOC bên dưới, ví dụ:
#        "Toán học": {
#            "thu_muc": "Toan-hoc",
#            "file_json": "toan_data.json",
#        },
# Giao diện sẽ tự động hiện thêm môn đó trong dropdown bên trái.
# ======================================================================
MON_HOC = {
    "Triết học": {
        "thu_muc": "Triet-Hoc",
        "file_json": "triet_data.json",
    },
}

THU_MUC_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DINH_DANG_ANH = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")


def tim_thu_muc_anh():
    ung_vien = [
        os.path.join(THU_MUC_SCRIPT, "anh_co_vu"),
        os.path.normpath(os.path.join(THU_MUC_SCRIPT, "..", "anh_co_vu")),
    ]
    for duong_dan in ung_vien:
        if os.path.isdir(duong_dan) and any(
            ten.lower().endswith(DINH_DANG_ANH) for ten in os.listdir(duong_dan)
        ):
            return duong_dan
    os.makedirs(ung_vien[0], exist_ok=True)
    return ung_vien[0]


THU_MUC_ANH = tim_thu_muc_anh()
anh_co_vu = sorted(
    ten for ten in os.listdir(THU_MUC_ANH) if ten.lower().endswith(DINH_DANG_ANH)
)


@st.cache_data
def tai_ngan_hang_cau_hoi(thu_muc, file_json):
    """Đọc ngân hàng câu hỏi của môn đang chọn (thử nhiều đường dẫn cho chắc)."""
    cac_duong_dan = [
        os.path.join(THU_MUC_SCRIPT, thu_muc, file_json),
        os.path.join(THU_MUC_SCRIPT, thu_muc.lower(), file_json),
        os.path.join(THU_MUC_SCRIPT, file_json),
        file_json,
    ]
    for duong_dan in cac_duong_dan:
        try:
            with open(duong_dan, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"Không tìm thấy file '{file_json}' của môn '{thu_muc}'.")


# ---------------- MENU CHỌN MÔN HỌC (bên trái) ----------------
st.sidebar.header("Môn học")
ten_mon = st.sidebar.selectbox("Chọn môn cần ôn tập:", list(MON_HOC.keys()))
thong_tin_mon = MON_HOC[ten_mon]
st.sidebar.caption(f"📖 Đang ôn: **{ten_mon}**")

# Khóa lưu câu sai RIÊNG cho từng môn (lưu trên trình duyệt của người dùng)
KHOI_CAU_SAI = f"cac_cau_sai_{thong_tin_mon['thu_muc'].lower()}"

cac_cau_sai_da_luu = local_storage.getItem(KHOI_CAU_SAI)
if cac_cau_sai_da_luu is None:
    # Chuyển dữ liệu cũ (khóa "cac_cau_sai") cho môn đầu tiên
    du_lieu_cu = local_storage.getItem("cac_cau_sai")
    if du_lieu_cu is not None:
        cac_cau_sai_da_luu = du_lieu_cu
if cac_cau_sai_da_luu is None:
    cac_cau_sai_da_luu = []
else:
    cac_cau_sai_da_luu = json.loads(cac_cau_sai_da_luu)

# ---------------- MENU CHỌN CHẾ ĐỘ HỌC (bên trái) ----------------
st.sidebar.header("Chế độ học")
che_do = st.sidebar.radio(
    "Bạn muốn làm gì?",
    ["Thi thử vô tận", "Thi thử 50 câu", f"Luyện lại câu sai ({len(cac_cau_sai_da_luu)} câu)"],
    key="che_do_radio",
)

# Tải ngân hàng câu hỏi của môn đang chọn
try:
    ngan_hang = tai_ngan_hang_cau_hoi(thong_tin_mon["thu_muc"], thong_tin_mon["file_json"])
except FileNotFoundError as loi:
    st.error(str(loi))
    st.info("Hãy kiểm tra lại mục MON_HOC ở đầu file web_on_tap.py.")
    st.stop()

def tao_de_moi():
    """Xáo lại bộ đề của chế độ hiện tại và quay về câu đầu tiên."""
    if "50 câu" in che_do:
        st.session_state.danh_sach_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
    elif "vô tận" in che_do:
        st.session_state.danh_sach_cau = random.sample(ngan_hang, len(ngan_hang))
    else:
        st.session_state.danh_sach_cau = random.sample(cac_cau_sai_da_luu, len(cac_cau_sai_da_luu))
    st.session_state.chi_so_cau = 0
    # Lưu câu trả lời theo từng câu: chỉ số câu -> {"chon": "A", "dung": True/False}
    st.session_state.cac_cau_da_tra_loi = {}
    st.session_state.chuoi_dung_lien_tiep = 0
    st.session_state.anh_co_vu_hien_tai = None


def tinh_diem():
    """Số câu đã trả lời ĐÚNG trong lượt hiện tại."""
    return sum(1 for tt in st.session_state.cac_cau_da_tra_loi.values() if tt["dung"])


# Reset toàn bộ khi: lần đầu chạy, ĐỔI MÔN hoặc ĐỔI CHẾ ĐỘ
if ("mon_cu" not in st.session_state or st.session_state.mon_cu != ten_mon
        or "che_do_cu" not in st.session_state or st.session_state.che_do_cu != che_do):
    st.session_state.mon_cu = ten_mon
    st.session_state.che_do_cu = che_do
    tao_de_moi()

danh_sach_cau = st.session_state.danh_sach_cau

if not danh_sach_cau:
    st.info("Hiện tại bạn chưa có câu nào bị sai! Hãy chọn chế độ Thi thử bộ đề chung bên menu trái.")
else:
    if st.session_state.chi_so_cau >= len(danh_sach_cau):
        # ---------------- MÀN HÌNH HOÀN THÀNH ----------------
        diem = tinh_diem()
        if "50 câu" in che_do:
            st.balloons()
            st.success("🎉 Bạn đã hoàn thành đề 50 câu!")
            st.metric("Điểm số", f"{diem}/{len(danh_sach_cau)}")
            st.metric("Tỷ lệ đúng", f"{diem / len(danh_sach_cau) * 100:.1f}%")
        else:
            st.success("🎉 Bạn đã hoàn thành lượt câu hỏi này!")

        cot_1, cot_2 = st.columns(2)
        with cot_1:
            if st.button("🔄 Làm lại từ đầu"):
                tao_de_moi()
                st.rerun()
        with cot_2:
            if st.button("⬅️ Quay lại rà soát các câu"):
                st.session_state.chi_so_cau = len(danh_sach_cau) - 1
                st.rerun()
    else:
        chi_so = st.session_state.chi_so_cau
        cau_hien_tai = danh_sach_cau[chi_so]
        thong_tin = st.session_state.cac_cau_da_tra_loi.get(chi_so)
        da_tra_loi = thong_tin is not None  # câu này đã nộp bài chưa?

        if "50 câu" in che_do:
            st.progress((chi_so + 1) / len(danh_sach_cau))
            st.caption(f"Câu {chi_so + 1}/{len(danh_sach_cau)}")

        # ----- Cột trái: phần làm bài | Cột phải: ảnh cổ vũ -----
        cot_cau_hoi, cot_anh_co_vu = st.columns([3, 1])

        with cot_cau_hoi:
            st.subheader(f"Câu {chi_so + 1}: {cau_hien_tai['cau_hoi']}")
            cac_lua_chon = [f"{k}. {v}" for k, v in cau_hien_tai["phuong_an"].items()]

            # Nếu câu này đã trả lời rồi thì hiển thị lại đáp án đã chọn
            radio_index = None
            if da_tra_loi:
                ky_tu_da_chon = thong_tin["chon"]
                radio_index = next(
                    (i for i, lua_chon in enumerate(cac_lua_chon)
                     if lua_chon.startswith(f"{ky_tu_da_chon}.")),
                    None,
                )

            chon_lua = st.radio(
                "Chọn đáp án của bạn:",
                cac_lua_chon,
                index=radio_index,
                disabled=da_tra_loi,
            )

            # ---------- NỘP BÀI ----------
            if not da_tra_loi:
                if st.button("Nộp bài"):
                    if chon_lua is not None:
                        dap_an_user = chon_lua[0]
                        dung = dap_an_user == cau_hien_tai["dap_an_dung"]
                        st.session_state.cac_cau_da_tra_loi[chi_so] = {
                            "chon": dap_an_user,
                            "dung": dung,
                        }

                        if dung:
                            st.session_state.chuoi_dung_lien_tiep += 1
                            # Đúng 5 câu liên tục -> hiện 1 ảnh cổ vũ ngẫu nhiên
                            if st.session_state.chuoi_dung_lien_tiep >= 5:
                                if anh_co_vu:
                                    ten_anh = random.choice(anh_co_vu)
                                    st.session_state.anh_co_vu_hien_tai = os.path.join(THU_MUC_ANH, ten_anh)
                                st.session_state.chuoi_dung_lien_tiep = 0
                            # Luyện câu sai: làm đúng thì xóa câu đó khỏi danh sách sai
                            if "Luyện lại câu sai" in che_do and cau_hien_tai in cac_cau_sai_da_luu:
                                cac_cau_sai_da_luu.remove(cau_hien_tai)
                                local_storage.setItem(KHOI_CAU_SAI, json.dumps(cac_cau_sai_da_luu))
                        else:
                            st.session_state.chuoi_dung_lien_tiep = 0
                            # Thi thử: làm sai thì thêm câu đó vào danh sách câu sai
                            if "Luyện lại câu sai" not in che_do and cau_hien_tai not in cac_cau_sai_da_luu:
                                cac_cau_sai_da_luu.append(cau_hien_tai)
                                local_storage.setItem(KHOI_CAU_SAI, json.dumps(cac_cau_sai_da_luu))

                        st.rerun()
                    else:
                        st.warning("Vui lòng chọn một đáp án trước khi nộp bài!")

            # ---------- KẾT QUẢ SAU KHI ĐÃ NỘP ----------
            if da_tra_loi:
                if thong_tin["dung"]:
                    st.success("✓ Chính xác!")
                else:
                    st.error(f"✘ Sai rồi! Đáp án đúng là: {cau_hien_tai['dap_an_dung']}")
                st.info(f"**Giải thích:** {cau_hien_tai['giai_thich']}")

                if "50 câu" in che_do:
                    diem = tinh_diem()
                    st.metric("Điểm hiện tại", f"{diem}/{len(st.session_state.cac_cau_da_tra_loi)}")

            # ---------- ĐIỀU HƯỚNG: quay lại / tới mọi câu (đã làm hay chưa) ----------
            st.write("---")
            cot_nav_1, cot_nav_2, cot_nav_3 = st.columns(3)
            with cot_nav_1:
                nut_cau_truoc = st.button("⬅️ Câu trước", disabled=(chi_so == 0))
            with cot_nav_2:
                nut_cau_tiep = st.button("➡️ Câu tiếp theo")
            with cot_nav_3:
                nut_xao_bai = st.button("🔄 Xáo bài mới")

            if nut_cau_truoc:
                # Ảnh cổ vũ chỉ hiện ngay sau khi đạt 5 câu đúng liên tục;
                # bấm sang câu khác là mất, phải đúng 5 câu liên tục tiếp theo mới hiện lại.
                st.session_state.anh_co_vu_hien_tai = None
                st.session_state.chi_so_cau = chi_so - 1
                st.rerun()
            if nut_cau_tiep:
                # Ở câu cuối, bấm tiếp sẽ sang màn hình hoàn thành (có nút quay lại rà soát)
                st.session_state.anh_co_vu_hien_tai = None
                st.session_state.chi_so_cau = chi_so + 1
                st.rerun()
            if nut_xao_bai:
                tao_de_moi()
                st.rerun()

        # ----- Cột phải: ẢNH CỔ VŨ (chỉ hiện ảnh bất ngờ, không kèm chữ) -----
        with cot_anh_co_vu:
            if st.session_state.anh_co_vu_hien_tai:
                st.image(
                    st.session_state.anh_co_vu_hien_tai,
                    width="stretch",
                )

