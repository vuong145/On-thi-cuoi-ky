import json
import os
import random

import streamlit as st
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Ôn Thi Trắc Nghiệm & Tự Luận", page_icon="📚")
st.title("📚 Ôn Thi Trắc Nghiệm & Tự Luận")

# Bộ lưu trữ cục bộ trên trình duyệt của người dùng
local_storage = LocalStorage()

MON_HOC = {
    "Triết học": {
        "thu_muc": "Triet-Hoc",
        "file_json": "triet_data.json",
        "loai": "trac_nghiem",
    },
    "Luật kinh doanh": {
        "thu_muc": "Luat-Kinh-Doanh",
        "file_cau_hoi": "questions.json",
        "thu_muc_de_thi": "exams",
        "loai": "tu_luan",
    },
    "Toán cho DS": {
        "thu_muc": "Toan-cho-DS",
        "file_cau_hoi": "questions.json",
        "thu_muc_de_thi": "exams",
        "loai": "tu_luan",
    },
    "Xác suất thống kê": {
        "thu_muc": "Xac-Suat-Thong-Ke",
        "file_cau_hoi": "questions.json",
        "thu_muc_de_thi": "exams",
        "loai": "tu_luan",
    },
}

THU_MUC_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DINH_DANG_ANH = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
DINH_DANG_VIDEO = (".mp4", ".webm", ".ogg", ".mov")
DINH_DANG_HOP_LE = DINH_DANG_ANH + DINH_DANG_VIDEO

THU_MUC_ANH = os.path.join(THU_MUC_SCRIPT, "anh_co_vu")
THU_MUC_ANH_CO_VU = os.path.join(THU_MUC_ANH, "anh_co_vu")
THU_MUC_ANH_CHE_GIEU = os.path.join(THU_MUC_ANH, "anh_che_gieu")
os.makedirs(THU_MUC_ANH_CO_VU, exist_ok=True)
os.makedirs(THU_MUC_ANH_CHE_GIEU, exist_ok=True)

anh_co_vu = sorted(
    ten for ten in os.listdir(THU_MUC_ANH_CO_VU) if ten.lower().endswith(DINH_DANG_HOP_LE)
)
anh_che_gieu = sorted(
    ten for ten in os.listdir(THU_MUC_ANH_CHE_GIEU) if ten.lower().endswith(DINH_DANG_HOP_LE)
)


class LoiDuLieu(ValueError):
    """Lỗi dữ liệu đầu vào không hợp lệ."""


def reset_session(prefix):
    for key in list(st.session_state.keys()):
        if key.startswith(prefix):
            del st.session_state[key]


def tai_cau_sai_da_luu(khoa):
    du_lieu = local_storage.getItem(khoa)
    if not du_lieu:
        return []
    try:
        ket_qua = json.loads(du_lieu)
        return ket_qua if isinstance(ket_qua, list) else []
    except json.JSONDecodeError:
        return []


def luu_cau_sai(khoa, danh_sach_question_id):
    danh_sach_khong_trung = []
    da_thay = set()
    for qid in danh_sach_question_id:
        if qid and qid not in da_thay:
            da_thay.add(qid)
            danh_sach_khong_trung.append(qid)
    local_storage.setItem(khoa, json.dumps(danh_sach_khong_trung))


def tim_duong_dan_json(thu_muc, ten_file):
    cac_duong_dan = [
        os.path.join(THU_MUC_SCRIPT, thu_muc, ten_file),
        os.path.join(THU_MUC_SCRIPT, thu_muc.lower(), ten_file),
        os.path.join(THU_MUC_SCRIPT, ten_file),
        ten_file,
    ]
    for duong_dan in cac_duong_dan:
        if os.path.exists(duong_dan):
            return duong_dan
    raise FileNotFoundError(f"Không tìm thấy file '{ten_file}' trong thư mục môn '{thu_muc}'.")


def doc_json_file(duong_dan):
    try:
        with open(duong_dan, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as loi:
        raise LoiDuLieu(
            f"File JSON không hợp lệ: {duong_dan} (dòng {loi.lineno}, cột {loi.colno})."
        ) from loi


@st.cache_data
def tai_ngan_hang_trac_nghiem(thu_muc, file_json):
    duong_dan = tim_duong_dan_json(thu_muc, file_json)
    du_lieu = doc_json_file(duong_dan)
    if not isinstance(du_lieu, list):
        raise LoiDuLieu(f"Ngân hàng trắc nghiệm phải là danh sách trong file: {duong_dan}")
    return du_lieu


@st.cache_data
def tai_ngan_hang_tu_luan(thu_muc, file_cau_hoi):
    duong_dan = tim_duong_dan_json(thu_muc, file_cau_hoi)
    du_lieu = doc_json_file(duong_dan)
    if not isinstance(du_lieu, list):
        raise LoiDuLieu(f"Ngân hàng câu hỏi tự luận phải là danh sách trong file: {duong_dan}")
    return du_lieu


@st.cache_data
def tai_danh_sach_de_thi(thu_muc, thu_muc_de_thi):
    duong_dan_de = os.path.join(THU_MUC_SCRIPT, thu_muc, thu_muc_de_thi)
    if not os.path.isdir(duong_dan_de):
        raise FileNotFoundError(f"Không tìm thấy thư mục đề thi: {duong_dan_de}")

    danh_sach_de = []
    for ten_file in sorted(os.listdir(duong_dan_de)):
        if not ten_file.lower().endswith(".json"):
            continue
        duong_dan = os.path.join(duong_dan_de, ten_file)
        de_thi = doc_json_file(duong_dan)
        if not isinstance(de_thi, dict) or not isinstance(de_thi.get("cau_hoi"), list):
            raise LoiDuLieu(
                f"File đề không đúng định dạng (cần object có trường 'cau_hoi' là list): {duong_dan}"
            )
        de_thi["__file__"] = ten_file
        danh_sach_de.append(de_thi)

    if not danh_sach_de:
        raise LoiDuLieu(f"Không có file đề JSON hợp lệ trong thư mục: {duong_dan_de}")

    return danh_sach_de


def tao_anh_xa_cau_hoi(cau_hoi_list):
    cau_hoi_theo_id = {}
    for cau in cau_hoi_list:
        question_id = cau.get("id")
        if not question_id:
            continue
        cau_hoi_theo_id[question_id] = cau
    return cau_hoi_theo_id


def dung_danh_sach_cau_tu_de(de_thi, cau_hoi_theo_id):
    danh_sach_cau = []
    loi_question_id = []

    for i, muc_cau in enumerate(de_thi.get("cau_hoi", []), start=1):
        question_id = muc_cau.get("question_id")
        cau_goc = cau_hoi_theo_id.get(question_id)
        if cau_goc is None:
            loi_question_id.append(question_id)
            continue

        cau_gop = dict(cau_goc)
        cau_gop["question_id"] = question_id
        cau_gop["diem_de"] = muc_cau.get("diem", cau_goc.get("diem", 0))
        cau_gop["thu_tu"] = muc_cau.get("thu_tu", i)
        danh_sach_cau.append(cau_gop)

    danh_sach_cau.sort(key=lambda item: item.get("thu_tu", 0))
    return danh_sach_cau, loi_question_id


def hien_thi_dap_an_goi_y(cau_hoi):
    st.info(f"**Đáp án gợi ý:** {cau_hoi.get('dap_an_goi_y', 'Chưa có đáp án gợi ý.')}" )

    cac_y_chinh = cau_hoi.get("cac_y_chinh", [])
    if cac_y_chinh:
        st.markdown("**Các ý chính cần có:**")
        for y in cac_y_chinh:
            st.markdown(f"- {y}")

    tu_khoa = cau_hoi.get("tu_khoa", [])
    if tu_khoa:
        st.markdown(f"**Từ khóa:** {', '.join(tu_khoa)}")

    tai_lieu = cau_hoi.get("tai_lieu_tham_khao")
    if tai_lieu:
        st.caption(f"Tài liệu tham khảo: {tai_lieu}")


def tinh_tong_diem_tu_cham(cac_key_diem):
    return sum(float(st.session_state.get(key, 0.0) or 0.0) for key in cac_key_diem)


def render_trac_nghiem(ten_mon, thong_tin_mon):
    khoi_cau_sai = f"cac_cau_sai_{thong_tin_mon['thu_muc'].lower()}"

    cac_cau_sai_da_luu = local_storage.getItem(khoi_cau_sai)
    if cac_cau_sai_da_luu is None:
        du_lieu_cu = local_storage.getItem("cac_cau_sai")
        if du_lieu_cu is not None:
            cac_cau_sai_da_luu = du_lieu_cu
    if cac_cau_sai_da_luu is None:
        cac_cau_sai_da_luu = []
    else:
        cac_cau_sai_da_luu = json.loads(cac_cau_sai_da_luu)

    st.sidebar.header("Chế độ học")
    che_do = st.sidebar.radio(
        "Bạn muốn làm gì?",
        ["Thi thử vô tận", "Thi thử 50 câu", f"Luyện lại câu sai ({len(cac_cau_sai_da_luu)} câu)"],
        key="che_do_trac_nghiem_radio",
    )

    try:
        ngan_hang = tai_ngan_hang_trac_nghiem(thong_tin_mon["thu_muc"], thong_tin_mon["file_json"])
    except (FileNotFoundError, LoiDuLieu) as loi:
        st.error(str(loi))
        st.stop()

    def tao_de_moi():
        if "50 câu" in che_do:
            st.session_state.danh_sach_cau = random.sample(ngan_hang, min(50, len(ngan_hang)))
        elif "vô tận" in che_do:
            st.session_state.danh_sach_cau = random.sample(ngan_hang, len(ngan_hang))
        else:
            st.session_state.danh_sach_cau = random.sample(cac_cau_sai_da_luu, len(cac_cau_sai_da_luu))
        st.session_state.chi_so_cau = 0
        st.session_state.cac_cau_da_tra_loi = {}
        st.session_state.chuoi_dung_lien_tiep = 0
        st.session_state.chuoi_sai_lien_tiep = 0
        st.session_state.anh_co_vu_hien_tai = None
        st.session_state.anh_che_gieu_hien_tai = None

    def tinh_diem():
        return sum(1 for tt in st.session_state.cac_cau_da_tra_loi.values() if tt["dung"])

    if (
        "mon_cu" not in st.session_state
        or st.session_state.mon_cu != ten_mon
        or "che_do_cu" not in st.session_state
        or st.session_state.che_do_cu != che_do
    ):
        st.session_state.mon_cu = ten_mon
        st.session_state.che_do_cu = che_do
        tao_de_moi()

    danh_sach_cau = st.session_state.danh_sach_cau

    if not danh_sach_cau:
        st.info("Hiện tại bạn chưa có câu nào bị sai! Hãy chọn chế độ Thi thử bộ đề chung bên menu trái.")
        return

    if st.session_state.chi_so_cau >= len(danh_sach_cau):
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
        return

    chi_so = st.session_state.chi_so_cau
    cau_hien_tai = danh_sach_cau[chi_so]
    thong_tin = st.session_state.cac_cau_da_tra_loi.get(chi_so)
    da_tra_loi = thong_tin is not None

    if "50 câu" in che_do:
        st.progress((chi_so + 1) / len(danh_sach_cau))
        st.caption(f"Câu {chi_so + 1}/{len(danh_sach_cau)}")

    cot_cau_hoi, cot_anh = st.columns([3, 1])

    with cot_cau_hoi:
        st.subheader(f"Câu {chi_so + 1}: {cau_hien_tai['cau_hoi']}")
        cac_lua_chon = [f"{k}. {v}" for k, v in cau_hien_tai["phuong_an"].items()]

        radio_index = None
        if da_tra_loi:
            ky_tu_da_chon = thong_tin["chon"]
            radio_index = next(
                (i for i, lua_chon in enumerate(cac_lua_chon) if lua_chon.startswith(f"{ky_tu_da_chon}.")),
                None,
            )

        chon_lua = st.radio(
            "Chọn đáp án của bạn:",
            cac_lua_chon,
            index=radio_index,
            disabled=da_tra_loi,
        )

        if not da_tra_loi and st.button("Nộp bài"):
            if chon_lua is None:
                st.warning("Vui lòng chọn một đáp án trước khi nộp bài!")
            else:
                dap_an_user = chon_lua[0]
                dung = dap_an_user == cau_hien_tai["dap_an_dung"]
                st.session_state.cac_cau_da_tra_loi[chi_so] = {"chon": dap_an_user, "dung": dung}

                if dung:
                    st.session_state.chuoi_dung_lien_tiep += 1
                    st.session_state.chuoi_sai_lien_tiep = 0
                    st.session_state.anh_che_gieu_hien_tai = None
                    if st.session_state.chuoi_dung_lien_tiep >= 5:
                        if anh_co_vu:
                            ten_anh = random.choice(anh_co_vu)
                            st.session_state.anh_co_vu_hien_tai = os.path.join(THU_MUC_ANH_CO_VU, ten_anh)
                        st.session_state.chuoi_dung_lien_tiep = 0
                    if "Luyện lại câu sai" in che_do and cau_hien_tai in cac_cau_sai_da_luu:
                        cac_cau_sai_da_luu.remove(cau_hien_tai)
                        local_storage.setItem(khoi_cau_sai, json.dumps(cac_cau_sai_da_luu))
                else:
                    st.session_state.chuoi_dung_lien_tiep = 0
                    st.session_state.chuoi_sai_lien_tiep += 1
                    st.session_state.anh_co_vu_hien_tai = None
                    if st.session_state.chuoi_sai_lien_tiep >= 3:
                        if anh_che_gieu:
                            ten_anh = random.choice(anh_che_gieu)
                            st.session_state.anh_che_gieu_hien_tai = os.path.join(THU_MUC_ANH_CHE_GIEU, ten_anh)
                        st.session_state.chuoi_sai_lien_tiep = 0
                    if "Luyện lại câu sai" not in che_do and cau_hien_tai not in cac_cau_sai_da_luu:
                        cac_cau_sai_da_luu.append(cau_hien_tai)
                        local_storage.setItem(khoi_cau_sai, json.dumps(cac_cau_sai_da_luu))

                st.rerun()

        if da_tra_loi:
            if thong_tin["dung"]:
                st.success("✓ Chính xác!")
            else:
                st.error(f"✘ Sai rồi! Đáp án đúng là: {cau_hien_tai['dap_an_dung']}")
            st.info(f"**Giải thích:** {cau_hien_tai['giai_thich']}")

            if "50 câu" in che_do:
                diem = tinh_diem()
                st.metric("Điểm hiện tại", f"{diem}/{len(st.session_state.cac_cau_da_tra_loi)}")

        st.write("---")
        cot_nav_1, cot_nav_2, cot_nav_3 = st.columns(3)
        with cot_nav_1:
            nut_cau_truoc = st.button("⬅️ Câu trước", disabled=(chi_so == 0))
        with cot_nav_2:
            nut_cau_tiep = st.button("➡️ Câu tiếp theo")
        with cot_nav_3:
            nut_xao_bai = st.button("🔄 Xáo bài mới")

        if nut_cau_truoc:
            st.session_state.anh_co_vu_hien_tai = None
            st.session_state.anh_che_gieu_hien_tai = None
            st.session_state.chi_so_cau = chi_so - 1
            st.rerun()
        if nut_cau_tiep:
            st.session_state.anh_co_vu_hien_tai = None
            st.session_state.anh_che_gieu_hien_tai = None
            st.session_state.chi_so_cau = chi_so + 1
            st.rerun()
        if nut_xao_bai:
            tao_de_moi()
            st.rerun()

    with cot_anh:
        anh_bat_ngo = st.session_state.anh_co_vu_hien_tai or st.session_state.anh_che_gieu_hien_tai
        if anh_bat_ngo:
            if anh_bat_ngo.lower().endswith(DINH_DANG_VIDEO):
                st.video(anh_bat_ngo, autoplay=True, loop=True)
            else:
                st.image(anh_bat_ngo, width="stretch")


def render_tu_luan(ten_mon, thong_tin_mon):
    khoi_cau_sai = f"cac_cau_sai_{thong_tin_mon['thu_muc'].lower()}"
    cac_question_id_sai = tai_cau_sai_da_luu(khoi_cau_sai)

    st.sidebar.header("Chế độ học")
    che_do = st.sidebar.radio(
        "Bạn muốn làm gì?",
        ["Làm một đề đầy đủ", "Luyện từng câu", f"Luyện lại câu sai ({len(cac_question_id_sai)} câu)"],
        key="che_do_tu_luan_radio",
    )

    try:
        ngan_hang = tai_ngan_hang_tu_luan(thong_tin_mon["thu_muc"], thong_tin_mon["file_cau_hoi"])
    except (FileNotFoundError, LoiDuLieu) as loi:
        st.error(str(loi))
        st.stop()

    cau_hoi_theo_id = tao_anh_xa_cau_hoi(ngan_hang)
    if not cau_hoi_theo_id:
        st.error("Ngân hàng câu hỏi trống hoặc thiếu trường 'id'.")
        st.stop()

    if che_do == "Làm một đề đầy đủ":
        try:
            danh_sach_de = tai_danh_sach_de_thi(thong_tin_mon["thu_muc"], thong_tin_mon["thu_muc_de_thi"])
        except (FileNotFoundError, LoiDuLieu) as loi:
            st.error(str(loi))
            st.stop()

        lua_chon_de = {f"{de.get('ten_de', de.get('__file__', 'Đề'))}": de for de in danh_sach_de}
        ten_de = st.selectbox("Chọn đề tự luận:", list(lua_chon_de.keys()), key="essay_exam_select")
        de_thi = lua_chon_de[ten_de]

        context = f"{ten_mon}|{che_do}|{de_thi.get('id', de_thi.get('__file__', ''))}"
        if st.session_state.get("essay_context") != context:
            reset_session("essay_")
            st.session_state.essay_context = context
            st.session_state.essay_submitted_all = False

        danh_sach_cau, loi_question_id = dung_danh_sach_cau_tu_de(de_thi, cau_hoi_theo_id)
        if loi_question_id:
            st.error(
                "Các question_id trong đề không tồn tại trong ngân hàng câu hỏi: "
                + ", ".join(str(item) for item in loi_question_id if item)
            )
        if not danh_sach_cau:
            st.warning("Đề hiện tại không có câu hỏi hợp lệ để hiển thị.")
            st.stop()

        st.subheader(de_thi.get("ten_de", "Đề tự luận"))
        st.caption(de_thi.get("mo_ta", ""))

        cot_info_1, cot_info_2 = st.columns(2)
        with cot_info_1:
            st.write(f"⏱️ Thời gian: **{de_thi.get('thoi_gian_phut', 'N/A')} phút**")
        with cot_info_2:
            tong_diem_de = de_thi.get("tong_diem")
            if tong_diem_de is None:
                tong_diem_de = sum(float(cau.get("diem_de", 0) or 0) for cau in danh_sach_cau)
            st.write(f"🎯 Tổng điểm đề: **{tong_diem_de}**")

        cac_key_diem = []
        for index, cau in enumerate(danh_sach_cau, start=1):
            st.markdown(f"### Câu {index} ({cau.get('diem_de', 0)} điểm)")
            st.write(cau.get("cau_hoi", ""))
            st.text_area(
                "Câu trả lời của bạn:",
                key=f"essay_answer_{index}",
                height=140,
            )

        if st.button("Nộp toàn bộ bài", key="essay_submit_all"):
            st.session_state.essay_submitted_all = True
            st.rerun()

        if st.session_state.get("essay_submitted_all"):
            st.success("Bạn đã nộp bài. Hãy tự đối chiếu đáp án gợi ý và tự chấm điểm từng câu.")
            chon_cau_sai = []
            for index, cau in enumerate(danh_sach_cau, start=1):
                st.markdown(f"#### Đáp án tham khảo - Câu {index}")
                hien_thi_dap_an_goi_y(cau)
                diem_toi_da = float(cau.get("diem_de", 0) or 0)
                diem_key = f"essay_score_{index}"
                cac_key_diem.append(diem_key)
                st.number_input(
                    f"Điểm tự chấm câu {index}",
                    min_value=0.0,
                    max_value=diem_toi_da,
                    step=0.25,
                    key=diem_key,
                )
                question_id = cau.get("question_id")
                mac_dinh_cau_sai = question_id in cac_question_id_sai
                danh_dau = st.checkbox(
                    f"Đánh dấu câu {index} là câu sai/cần luyện lại",
                    value=mac_dinh_cau_sai,
                    key=f"essay_wrong_mark_{index}",
                )
                if danh_dau and question_id:
                    chon_cau_sai.append(question_id)

            st.metric("Tổng điểm tự chấm", f"{tinh_tong_diem_tu_cham(cac_key_diem):.2f}")
            if st.button("Lưu danh sách câu sai", key="essay_save_wrong"):
                luu_cau_sai(khoi_cau_sai, chon_cau_sai)
                st.success("Đã cập nhật danh sách câu sai cho môn hiện tại.")

        return

    # Luyện từng câu / Luyện lại câu sai
    if "Luyện lại câu sai" in che_do:
        tap_cau_sai = set(cac_question_id_sai)
        danh_sach_cau = [cau for cau in ngan_hang if cau.get("id") in tap_cau_sai]
    else:
        danh_sach_cau = list(ngan_hang)

    context = f"{ten_mon}|{che_do}"
    if st.session_state.get("essay_context") != context:
        reset_session("essay_")
        st.session_state.essay_context = context
        st.session_state.essay_index = 0

    if not danh_sach_cau:
        if "Luyện lại câu sai" in che_do:
            st.info("Hiện chưa có câu sai nào được lưu cho môn này.")
        else:
            st.warning("Ngân hàng câu hỏi trống.")
        st.stop()

    if st.session_state.essay_index >= len(danh_sach_cau):
        st.session_state.essay_index = len(danh_sach_cau) - 1

    chi_so = st.session_state.essay_index
    cau_hien_tai = danh_sach_cau[chi_so]

    st.progress((chi_so + 1) / len(danh_sach_cau))
    st.caption(f"Câu {chi_so + 1}/{len(danh_sach_cau)}")

    st.subheader(f"Câu hỏi {chi_so + 1}")
    st.write(cau_hien_tai.get("cau_hoi", ""))
    st.text_area(
        "Câu trả lời của bạn:",
        key=f"essay_single_answer_{chi_so}",
        height=180,
    )

    submitted_key = f"essay_single_submitted_{chi_so}"
    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    if not st.session_state[submitted_key]:
        if st.button("Nộp câu trả lời", key=f"essay_submit_one_{chi_so}"):
            st.session_state[submitted_key] = True
            st.rerun()

    if st.session_state[submitted_key]:
        st.success("Bạn đã nộp câu này. Hãy tự đối chiếu và tự chấm.")
        hien_thi_dap_an_goi_y(cau_hien_tai)
        diem_toi_da = float(cau_hien_tai.get("diem", 0) or 0)
        st.number_input(
            "Điểm tự chấm câu hiện tại",
            min_value=0.0,
            max_value=diem_toi_da,
            step=0.25,
            key=f"essay_single_score_{chi_so}",
        )
        question_id = cau_hien_tai.get("id")
        danh_sach_sai_hien_tai = tai_cau_sai_da_luu(khoi_cau_sai)
        da_danh_dau_sai = question_id in danh_sach_sai_hien_tai
        nut_nhan = "✅ Bỏ đánh dấu câu sai" if da_danh_dau_sai else "❌ Đánh dấu là câu sai"
        if st.button(nut_nhan, key=f"essay_toggle_wrong_{chi_so}"):
            if da_danh_dau_sai:
                danh_sach_sai_hien_tai = [qid for qid in danh_sach_sai_hien_tai if qid != question_id]
                luu_cau_sai(khoi_cau_sai, danh_sach_sai_hien_tai)
            else:
                danh_sach_sai_hien_tai.append(question_id)
                luu_cau_sai(khoi_cau_sai, danh_sach_sai_hien_tai)
            st.rerun()

    cot_1, cot_2, cot_3 = st.columns(3)
    with cot_1:
        if st.button("⬅️ Câu trước", disabled=(chi_so == 0), key="essay_prev"):
            st.session_state.essay_index = chi_so - 1
            st.rerun()
    with cot_2:
        if st.button("➡️ Câu tiếp theo", disabled=(chi_so >= len(danh_sach_cau) - 1), key="essay_next"):
            st.session_state.essay_index = chi_so + 1
            st.rerun()
    with cot_3:
        if st.button("🎲 Câu ngẫu nhiên", key="essay_random"):
            st.session_state.essay_index = random.randint(0, len(danh_sach_cau) - 1)
            st.rerun()


# ---------------- MENU CHỌN MÔN HỌC (bên trái) ----------------
st.sidebar.header("Môn học")
ten_mon = st.sidebar.selectbox("Chọn môn cần ôn tập:", list(MON_HOC.keys()))
thong_tin_mon = MON_HOC[ten_mon]
st.sidebar.caption(f"📖 Đang ôn: **{ten_mon}**")

if thong_tin_mon.get("loai") == "tu_luan":
    render_tu_luan(ten_mon, thong_tin_mon)
else:
    render_trac_nghiem(ten_mon, thong_tin_mon)
