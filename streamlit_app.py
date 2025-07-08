

import pandas as pd
from docxtpl import DocxTemplate
from datetime import date
import streamlit as st
import io
import zipfile
import re

st.set_page_config(page_title="Enhanced KOC Contract Generator", layout="wide", page_icon="📝")

st.markdown("""
<style>
    .main {
        background-color: #f0f6fb;
        font-family: 'Segoe UI', sans-serif;
    }
    .title {
        font-size: 2.2em;
        font-weight: bold;
        color: #2563eb;
    }
    .subtitle {
        font-size: 1.1em;
        color: #3b82f6;
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
    .summary-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .summary-title {
        font-weight: bold;
        color: #2563eb;
        margin-bottom: 10px;
    }
    .pair-info {
        background-color: #e8f4fd;
        border-left: 4px solid #2563eb;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="title">📄 Enhanced KOC Contract Generator</div>', unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Generate Contracts + Summaries in Perfect Pairs 🚀</div>", unsafe_allow_html=True)

st.markdown("---")

# Upload section
col1, col2 = st.columns(2)
with col1:
    uploaded_csv = st.file_uploader("📑 Upload CSV File", type=["csv"])
with col2:
    uploaded_template = st.file_uploader("📄 Upload Word Template (.docx)", type=["docx"])

# 生成选项简化为两种
st.markdown("### 生成选项")
generate_mode = st.radio(
    "请选择生成模式：",
    ["只批量生成合同（仅合同文件）", "合同及配对的基本内容（合同+概括配对输出）"],
    index=1
)

# 生成按钮
generate = st.button("🚀 Generate")

# 生成选项逻辑
if generate_mode == "只批量生成合同（仅合同文件）":
    generate_contracts = True
    generate_summaries = False
    output_mode = "配对输出"
else:
    generate_contracts = True
    generate_summaries = True
    output_mode = "配对输出"

def generate_contract_summary(row):
    """生成合同基本内容概括 - 使用中文字段"""
    try:
        kol_name = str(row.get('Party B Name', '')).strip()
        nickname = str(row.get('Main Platform nickname', '')).strip()
        platform = str(row.get('Platform', '')).strip()
        video_rate = str(row.get('Video Rate', '')).strip()
        video_number = str(row.get('Estimated Videos', '')).strip()
        promotion_date = str(row.get('Chinese date version', '')).strip()
        payment_text = str(row.get('chinese payment version', '')).strip()
        bonus_info = str(row.get('bonus information', '')).strip()
        statement = str(row.get('Statement', '')).strip()
        actual_video_number = str(row.get('No. of Posted Videos', '')).strip()

        platforms = platform.replace('&', ' & ')
        try:
            video_rate_clean = "{:.0f}".format(float(video_rate)) if video_rate else "0"
        except:
            video_rate_clean = video_rate

        # 奖励机制：只要有内容就插入一句中文提示，无内容就不插入
        bonus_text = ""
        if bonus_info:
            bonus_text = "\n3. 有奖励机制，合同中有根据播放量制定的详细奖励机制，具体参见合同。"

        if not payment_text:
            payment_text = "视频上线后 Net 30 days/video"

        koc_display_name = nickname if nickname else kol_name

        # 根据statement判断履行状态，选择不同的时间表述
        if statement == "已履行完毕":
            line2 = f"2. 单支视频金额${video_rate_clean}，签约 {video_number} 期视频，实际上线视频数量为 {actual_video_number} 支，视频上线时间为 {promotion_date}。"
        else:
            line2 = f"2. 单支视频金额${video_rate_clean}，签约 {video_number} 期视频，视频预计上线时间为 {promotion_date}。"
        
        summary = f'''合作事项：\n1. 海外KOC（{koc_display_name}），发布平台{platforms}。\n{line2}{bonus_text}\n\n权利义务：(重点highlight)\n1. 未经甲方同意，乙方不得删除视频，内容永久保留，否则支付甲方50%的费用。\n2. 乙方发布未经批准/错误版本视频，甲方可以选择补偿方式（删除重发、另行协商补偿、终止合作拒绝付款）。\n\n付款条件：\n{payment_text}'''
        return summary
    except Exception as e:
        return f"生成概括时出错: {str(e)}"

def process_data(df, uploaded_template, generate_contracts, generate_summaries, output_mode):
    """处理数据并生成文件 - 精确配对输出"""
    today = date.today().isoformat()
    zip_buffer = io.BytesIO()
    summaries = []
    contract_files = []
    
    # 找到最后一个有效Name的索引
    last_valid_index = df['Party B Name'].apply(lambda x: str(x).strip() != '').to_numpy().nonzero()[0]
    if len(last_valid_index) > 0:
        last_valid_index = last_valid_index[-1]
    else:
        last_valid_index = -1
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        # 只遍历第3行到最后一个有效数据行
        for index, row in df.iloc[2:last_valid_index+1].iterrows():
            name_value = row['Party B Name'] if 'Party B Name' in row else ''
            if str(name_value).strip() == "":
                continue  # 跳过空行
            
            try:
                safe_name = str(row['Party B Name']).replace(" ", "_").replace("/", "-")
                
                # 生成合同文件
                if generate_contracts:
                    template = DocxTemplate(uploaded_template)
                    video_rate_value = row['Video Rate'] if 'Video Rate' in row else ''
                    is_video_rate_empty = False
                    try:
                        is_video_rate_empty = bool(pd.isna(video_rate_value)) or str(video_rate_value).strip() == ""
                    except Exception:
                        is_video_rate_empty = str(video_rate_value).strip() == ""
                    
                    context = {
                    
                        'Influencer_name': row['Party B Name'],
                        'Influencer_email': row['Email'],
                        'Influencer_contact': "N/A" if pd.isna(row['Contact']) or str(row['Contact']).strip() == "" else row['Contact'],
                        'Influencer_address': row['Address'],
                        'platform': str(row['Platform']).replace('&', '＆'),
                        'platform_username': row['Platform username'],
                        'Influencer_links': row['Links'],
                        'promotion_date': row['English date version'],
                        'video_rate': "{:.2f}".format(float(video_rate_value)) if not is_video_rate_empty else "",
                        'video_number': row['Estimated Videos'],
                        'bonus_info': row['bonus information'],
                        'payment_method': row['Payment method'],
                        'payment_information': row['Payment Info'],
                        'payment_charges': row['Payment Charges']
                    }
                    template.render(context)
                    
                    # 合同文件命名 - 统一格式，不包含nickname
                    contract_filename = f'FW-ARETIS_{name_value}_{today}.docx'
                    contract_files.append(contract_filename)
                    
                    doc_stream = io.BytesIO()
                    template.save(doc_stream)
                    doc_stream.seek(0)
                    
                    zip_file.writestr(contract_filename, doc_stream.read())
                
                # 生成内容概括
                if generate_summaries:
                    summary = generate_contract_summary(row)
                    summaries.append({
                        'name': str(row['Party B Name']).strip(),
                        'summary': summary,
                        'filename': f'Summary_{safe_name}_{today}.txt'
                    })
                    
                    nickname = str(row.get('Main Platform nickname', '')).strip()
                    # 概括文件命名 - 统一格式
                    summary_filename = f'{name_value}_{nickname}_summary.txt'
                    
                    # 根据输出模式保存概括文件
                    if output_mode in ["配对输出", "单独文件"]:
                        zip_file.writestr(summary_filename, summary)
                
            except Exception as e:
                st.error(f"❌ Error processing {row.get('Party B Name', f'Row {index}')} (row {index}): {e}")
    
    # 如果需要合并输出，创建合并的概括文件
    if generate_summaries and output_mode == "合并文件" and summaries:
        combined_summary = ""
        for i, item in enumerate(summaries, 1):
            combined_summary += f"=== {item['name']} ===\n"
            combined_summary += item['summary']
            combined_summary += "\n\n"
        
        combined_filename = f'All_Summaries_{today}.txt'
        zip_file.writestr(combined_filename, combined_summary)
    
    return zip_buffer, summaries, contract_files

# Process files
if uploaded_csv and uploaded_template and generate:
    if not generate_contracts and not generate_summaries:
        st.warning("请至少选择一个生成选项！")
    else:
        st.success("✅ Files uploaded successfully!")
        df = pd.read_csv(uploaded_csv, keep_default_na=False, dtype=str)
        df.columns = df.columns.str.strip()
        
        # 显示处理进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            zip_buffer, summaries, contract_files = process_data(df, uploaded_template, generate_contracts, generate_summaries, output_mode)
            progress_bar.progress(100)
            status_text.text("✅ 处理完成！")
            
            zip_buffer.seek(0)
            
            # 显示生成结果
            st.markdown("### ✅ Generation Complete!")
            
            if generate_contracts:
                st.success(f"📄 Generated {len(contract_files)} contract files")
            
            if generate_summaries:
                st.success(f"📝 Generated {len(summaries)} summary files")
            
            # 下载按钮
            download_filename = f"KOC_Output_{date.today().isoformat()}.zip"
            st.download_button(
                "📥 Download All Files", 
                zip_buffer, 
                file_name=download_filename, 
                mime="application/zip"
            )
        
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")

else:
    st.info("⬆️ Upload both files above to get started, then click Generate.")
