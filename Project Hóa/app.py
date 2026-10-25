import os
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Công thức nước hoa mùa thu", page_icon="🍂", layout="wide")

LIMITS_FILE = "ingredient_limits_autumn.csv"

# Bảng công thức do nhóm cung cấp; không tự động xác nhận đây là giới hạn an toàn.
FORMULAS = {
    "Mẫu A": {"Sweet orange": 3.0, "Bergamot": 2.0, "Vanilla accord": 5.0, "Dung môi": 90.0},
    "Mẫu B": {"Sweet orange": 3.0, "Bergamot": 2.0, "Vanilla accord": 2.0, "Dung môi": 93.0},
    "Mẫu C": {"Sweet orange": 2.5, "Bergamot": 1.5, "Vanilla accord": 5.0, "Dung môi": 91.0},
    "Mẫu B2": {"Sweet orange": 1.75, "Bergamot": 2.25, "Vanilla accord": 3.0, "Dung môi": 93.0},
}

DEFAULT_LIMITS = pd.DataFrame([
    {"ingredient": "Sweet orange", "max_pct": 3.0, "basis": "finished", "source": "Bảng công thức A/B/C/B2 do nhóm cung cấp", "notes": "Giới hạn theo bảng nhóm; chưa được xác minh độc lập như giới hạn an toàn."},
    {"ingredient": "Bergamot", "max_pct": 4.0, "basis": "finished", "source": "Bảng công thức A/B/C/B2 do nhóm cung cấp", "notes": "Giới hạn Bergamot được nhóm đặt là 4%."},
    {"ingredient": "Vanilla accord", "max_pct": 5.0, "basis": "finished", "source": "Bảng công thức A/B/C/B2 do nhóm cung cấp", "notes": "Accord là hỗn hợp hương; giới hạn thực tế cần theo hồ sơ nhà cung cấp."},
    {"ingredient": "Dung môi", "max_pct": 100.0, "basis": "finished", "source": "Bảng công thức A/B/C/B2 do nhóm cung cấp", "notes": "Giá trị trong bảng nhóm; cần xác nhận loại dung môi với giáo viên."},
])

if os.path.exists(LIMITS_FILE):
    try:
        limits_df = pd.read_csv(LIMITS_FILE)
    except Exception:
        limits_df = DEFAULT_LIMITS.copy()
else:
    limits_df = DEFAULT_LIMITS.copy()

# Palette kem, nâu, cam lá phong và xanh rêu; sửa màu chữ trên các widget Streamlit.
st.markdown("""
<style>
    :root { color-scheme: light; }
    .stApp {
        background: radial-gradient(ellipse at 8% 4%, #fffaf0 0%, transparent 34%),
                    linear-gradient(180deg, #fbf5e9 0%, #f5ecdd 52%, #fbf6ed 100%);
        color: #4b3423;
    }
    [data-testid="stHeader"] { background: rgba(251, 245, 233, .88); }
    .block-container { max-width: 1320px; padding-top: 1.4rem; padding-bottom: 3rem; }
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stWidgetLabel"] { color: #573b27 !important; }
    h1 { letter-spacing: -.035em; }
    h2, h3 { font-weight: 700; }
    [data-testid="stDataFrame"] {
        background: #fffaf2; border: 1px solid #ead8bf; border-radius: 14px; overflow: hidden;
    }
    /* Warm styling for selectbox and number input: override dark Streamlit/BaseWeb defaults. */
    [data-testid="stSelectbox"], [data-testid="stNumberInput"] {
        background: #fffaf2 !important; border: 1px solid #e5d2b8 !important;
        border-radius: 14px !important; padding: 8px 10px !important;
        box-shadow: 0 3px 12px rgba(93, 65, 40, .045);
    }
    [data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label {
        color: #65462e !important; font-weight: 650 !important;
    }
    [data-testid="stNumberInput"] input {
        background: #f5ead9 !important; color: #573b27 !important;
        -webkit-text-fill-color: #573b27 !important; border-color: #dfc9ac !important;
        border-radius: 9px !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        background-color: #f5ead9 !important;
        background-image: none !important;
        border: 1px solid #dfc9ac !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        min-height: 44px !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    div[data-baseweb="select"] [role="combobox"],
    div[data-baseweb="select"] span {
        color: #573b27 !important;
        -webkit-text-fill-color: #573b27 !important;
    }
    [data-testid="stSelectbox"] svg, div[data-baseweb="select"] svg {
        fill: #805a39 !important; color: #805a39 !important;
    }
    /* Dropdown menu options */
    div[data-baseweb="popover"] [role="listbox"],
    div[data-baseweb="popover"] ul {
        background: #fffaf2 !important; border: 1px solid #e5d2b8 !important;
    }
    div[data-baseweb="popover"] [role="option"] {
        background: #fffaf2 !important; color: #573b27 !important;
    }
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [aria-selected="true"] {
        background: #eee0c9 !important; color: #573b27 !important;
    }
    [data-testid="stSlider"] {
        background: rgba(255, 251, 244, .9); padding: 15px 18px 8px;
        border-radius: 16px; border: 1px solid #ead9c2; box-shadow: 0 4px 14px rgba(93, 65, 40, .045);
        margin-bottom: 8px;
    }
    [data-testid="stSlider"] [data-testid="stWidgetLabel"] { font-weight: 650; color: #65462e !important; }
    [data-testid="stSlider"] label, [data-testid="stSlider"] p { color: #65462e !important; }
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: #806b57 !important; }
    /* Streamlit buttons: force both the button and its inner paragraph/span to white. */
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stButton"] button *,
    div[data-testid="stDownloadButton"] button * {
        background-color: #8b5a35;
        color: #fffaf2 !important;
        -webkit-text-fill-color: #fffaf2 !important;
        border-color: #8b5a35;
        border-radius: 11px;
        font-weight: 650;
        transition: all .15s ease;
    }
    div[data-testid="stButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stButton"] button:hover *,
    div[data-testid="stDownloadButton"] button:hover * {
        background-color: #6e472c;
        color: #fffaf2 !important;
        -webkit-text-fill-color: #fffaf2 !important;
        border-color: #6e472c;
    }
    [data-testid="stAlert"] { border-radius: 13px; }
    .autumn-banner {
        position: relative; overflow: hidden;
        background: linear-gradient(112deg, #fff8ec 0%, #f3e2c8 58%, #e8d1ae 100%);
        border: 1px solid #ead7bd; color: #573b27; padding: 1.45rem 1.65rem;
        border-radius: 22px; margin: .2rem 0 1.5rem;
        box-shadow: 0 8px 24px rgba(89, 59, 39, .08);
    }
    .autumn-banner h1 { color: #573b27 !important; margin: 0 0 .4rem; font-size: 2.15rem; }
    .autumn-banner p { color: #806449 !important; margin: 0; font-size: 1rem; }
    .section-heading { display: flex; align-items: center; gap: 12px; margin: .6rem 0 .2rem; }
    .section-heading h2 { margin: 0; font-size: 1.65rem; color: #573b27 !important; }
    .section-heading .leaf { font-size: 1.65rem; }
    .section-heading .line { flex: 1; height: 1px; background: #ddc9ae; margin-left: 8px; }
    .section-caption { color: #806b57 !important; margin: .35rem 0 1rem; }
    .formula-summary {
        display: flex; align-items: center; gap: 14px; background: #edf1df;
        border: 1px solid #d5dfbd; color: #4f7040; padding: 1rem 1.25rem;
        border-radius: 17px; margin: .5rem 0 1rem; font-size: 1.08rem;
    }
    .summary-check { display: inline-flex; align-items: center; justify-content: center;
        width: 38px; height: 38px; border-radius: 50%; background: #91aa73; color: white; font-size: 1.3rem; flex-shrink: 0; }
    .summary-warning { background: #fbebd7; border-color: #ecd0a7; color: #925b25; }
    .botanical-row { display: flex; justify-content: space-between; align-items: center; color: #9a794a; font-size: 1.25rem; margin: .15rem 0 .35rem; }
    hr { border-color: #e7d7c3; }
    @media (max-width: 700px) {
        .autumn-banner h1 { font-size: 1.6rem; }
    }
</style>
<div class="autumn-banner">
  <h1>🍂 Công thức nước hoa · Mùa thu</h1>
  <p>Điều chỉnh tỷ lệ nguyên liệu, kiểm tra tổng công thức và quy đổi thể tích theo mẻ pha.</p>
</div>
""", unsafe_allow_html=True)

# Mục 1: ẩn cột notes để bảng gọn, không hiển thị dòng ghi chú dài.
st.markdown('<div class="section-heading"><span class="leaf">🌿</span><h2>1. Dữ liệu giới hạn</h2><span class="line"></span><span class="leaf">🍂</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Giới hạn tối đa đang áp dụng cho từng thành phần trong ứng dụng.</div>', unsafe_allow_html=True)
limits_display = limits_df.drop(columns=["notes"], errors="ignore").rename(columns={
    "ingredient": "Thành phần",
    "max_pct": "Giới hạn tối đa (%)",
    "basis": "Cơ sở tỷ lệ",
    "source": "Nguồn dữ liệu",
})
st.dataframe(limits_display, use_container_width=True, hide_index=True)
st.download_button(
    "🍂 Tải bảng giới hạn CSV",
    data=limits_df.drop(columns=["notes"], errors="ignore").to_csv(index=False).encode("utf-8-sig"),
    file_name=LIMITS_FILE,
    mime="text/csv",
)

st.divider()
st.markdown('<div class="section-heading"><span class="leaf">🍁</span><h2>2. Điều chỉnh công thức</h2><span class="line"></span><span class="leaf">🌱</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Chọn mẫu và thay đổi thanh trượt. Mỗi thanh trượt sẽ dừng tại giới hạn tối đa của nguyên liệu.</div>', unsafe_allow_html=True)

formula_name = st.selectbox("🧪 Chọn mẫu", list(FORMULAS.keys()))
original = FORMULAS[formula_name]
batch_ml = st.number_input("🧴 Thể tích mẻ để quy đổi (mL)", min_value=1.0, max_value=500.0, value=5.0, step=1.0)

limit_lookup = {}
for _, row in limits_df.iterrows():
    try:
        if pd.notna(row.get("max_pct")):
            limit_lookup[str(row["ingredient"]).strip().casefold()] = float(row["max_pct"])
    except (TypeError, ValueError):
        pass

ingredient_icons = {
    "Sweet orange": "🍊",
    "Bergamot": "🍈",
    "Vanilla accord": "🌼",
    "Dung môi": "⚗️",
}
values = {}
cols = st.columns(2, gap="large")
for i, (ingredient, default) in enumerate(original.items()):
    max_allowed = max(0.0, float(limit_lookup.get(ingredient.casefold(), 100.0)))
    with cols[i % 2]:
        values[ingredient] = st.slider(
            f"{ingredient_icons.get(ingredient, '🍂')}  {ingredient}  ·  Tối đa {max_allowed:.2f}%",
            min_value=0.0,
            max_value=max_allowed,
            value=min(float(default), max_allowed),
            step=0.25 if ingredient != "Dung môi" else 0.5,
            key=f"{formula_name}_{ingredient}",
        )

total = sum(values.values())
if abs(total - 100.0) < 0.01:
    st.markdown(f'<div class="formula-summary"><span class="summary-check">✓</span><span><strong>Tổng tỷ lệ hiện tại: {total:.2f}%</strong> — Hợp lệ về mặt số học.</span><span style="margin-left:auto;font-size:1.5rem">🍂</span></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="formula-summary summary-warning"><span class="summary-check" style="background:#c28b4d">!</span><span><strong>Tổng tỷ lệ hiện tại: {total:.2f}%</strong> — Cần điều chỉnh để tổng bằng 100%.</span><span style="margin-left:auto;font-size:1.5rem">🍁</span></div>', unsafe_allow_html=True)

rows = []
for ingredient, pct in values.items():
    limit = limit_lookup.get(ingredient.casefold())
    rows.append({
        "Mẫu": formula_name,
        "Thành phần": ingredient,
        "Tỷ lệ (%)": round(pct, 3),
        "Thể tích (mL)": round(batch_ml * pct / 100.0, 4),
        "Giới hạn trong bảng (%)": limit,
        "Trạng thái": "Chưa có giới hạn" if limit is None else ("Vượt giới hạn" if pct > limit + 1e-9 else "Đạt theo bảng nhóm"),
    })
result_df = pd.DataFrame(rows)

st.divider()
st.markdown('<div class="section-heading"><span class="leaf">🌾</span><h2>3. Bảng tỷ lệ và quy đổi mL</h2><span class="line"></span><span class="leaf">🍃</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Thể tích được tính tự động từ tỷ lệ phần trăm và thể tích mẻ đã chọn.</div>', unsafe_allow_html=True)
st.dataframe(result_df, use_container_width=True, hide_index=True)
st.download_button(
    "⬇️ Xuất công thức hiện tại (CSV)",
    data=result_df.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"cong_thuc_mua_thu_{formula_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    disabled=abs(total - 100.0) >= 0.01,
)

