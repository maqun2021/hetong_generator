import pandas as pd
from docxtpl import DocxTemplate
from datetime import date
import streamlit as st
import io
import zipfile

st.set_page_config(page_title="KOC Contract Generator", layout="centered", page_icon="📝")

st.markdown("""
<style>
    .main {
        background-color: #f0f6fb;
        font-family: 'Segoe UI', sans-serif;
    }
    .title {
        font-size: 2.2em;
        font-weight: bold;
        color: #2563eb; /* 蓝色 */
    }
    .subtitle {
        font-size: 1.1em;
        color: #3b82f6; /* 浅蓝色 */
    }
    .stFileUploader > label {
        font-weight: 600;
        color: #2563eb;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font-size: 1.1em;
        font-weight: bold;
        margin-top: 1em;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="title">📄 KOC Contract Generator</div>', unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Built on Char's code 🤝, refined by keke 🎉</div>", unsafe_allow_html=True)

st.markdown("---")

# Upload section
col1, col2 = st.columns(2)
with col1:
    uploaded_csv = st.file_uploader("📑 Upload CSV File", type=["csv"])
with col2:
    uploaded_template = st.file_uploader("📄 Upload Word Template (.docx)", type=["docx"])

generate = st.button("🚀 Generate Contracts")

# Process files
if uploaded_csv and uploaded_template and generate:
    st.success("✅ Files uploaded successfully!")
    df = pd.read_csv(uploaded_csv, keep_default_na=False, dtype=str)
    df.columns = df.columns.str.strip()
    today = date.today().isoformat()
    zip_buffer = io.BytesIO()

    # 找到最后一个有效Name的索引
    last_valid_index = df['Name'].apply(lambda x: str(x).strip() != '').to_numpy().nonzero()[0]
    if len(last_valid_index) > 0:
        last_valid_index = last_valid_index[-1]
    else:
        last_valid_index = -1  # 没有有效数据

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        # 只遍历第3行到最后一个有效数据行
        for index, row in df.iloc[2:last_valid_index+1].iterrows():
            name_value = row['Name'] if 'Name' in row else ''
            if str(name_value).strip() == "":
                continue  # 跳过空行
            else:
                try:
                    template = DocxTemplate(uploaded_template)
                    video_rate_value = row['Video Rate'] if 'Video Rate' in row else ''
                    is_video_rate_empty = False
                    try:
                        is_video_rate_empty = bool(pd.isna(video_rate_value)) or str(video_rate_value).strip() == ""
                    except Exception:
                        is_video_rate_empty = str(video_rate_value).strip() == ""
                    context = {
                        'your_name':row['Your Name'],
                        'your_email':row['Your Email'],
                        'your_other_contact':row['Your Contact'],                  
                        'Influencer_name': row['Name'],
                        'Influencer_email': row['Email'],
                        'Influencer_contact': row['Contact'],
                        'Influencer_address': row['Address'],
                        'platform': str(row['Platform']).replace('&', '＆'),
                        'platform_username': row['Platform username'],
                        'Influencer_links': row['Links'],
                        'promotion_date': row['English date version'],
                        'video_rate': "{:.2f}".format(float(video_rate_value)) if not is_video_rate_empty else "",
                        'video_number':row['Estimated Videos'],
                        'bonus_info': row['bonus information'],
                        'payment_method': row['Payment method'],
                        'payment_information': row['Payment Info'],
                        'payment_charges': row['Payment Charges']
                    }
                    template.render(context)

                    safe_name = str(row['Name']).replace(" ", "_").replace("/", "-")
                    filename = f'FW-ARETIS_{safe_name}_{today}.docx'

                    doc_stream = io.BytesIO()
                    template.save(doc_stream)
                    doc_stream.seek(0)

                    zip_file.writestr(filename, doc_stream.read())

                except Exception as e:
                    st.error(f"❌ Error processing {row.get('Name', f'Row {index}')} (row {index}): {e}")

    zip_buffer.seek(0)
    st.markdown("### ✅ All contracts generated!")
    st.download_button("📥 Download ZIP of All Contracts", zip_buffer, file_name=f"KOC_Contracts_{today}.zip", mime="application/zip")

else:
    st.info("⬆️ Upload both files above to get started, then click Generate.")
