import streamlit as st
import pandas as pd
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="15分鐘醫療保險檢視", page_icon="🩺", layout="centered")

# 標題
st.title("🩺 15分鐘醫療保險檢視")
st.caption("輸入你嘅數字，系統會自動計算保障缺口")

# 初始化 session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

# 進度顯示
st.progress(st.session_state.step / 4)

# ==================== 第一步：基本資料 ====================
if st.session_state.step == 1:
    st.header("📋 第一步：基本資料")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("客人姓名")
    with col2:
        date = st.date_input("檢視日期", datetime.today())
    
    phone = st.text_input("聯絡電話")
    
    if st.button("下一步 →"):
        if name:
            st.session_state.client_data["name"] = name
            st.session_state.client_data["date"] = str(date)
            st.session_state.client_data["phone"] = phone
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("請輸入客人姓名")

# ==================== 第二步：5條問題 ====================
elif st.session_state.step == 2:
    st.header("📝 第二步：5條問題")
    
    st.info("以下問題會幫我了解你嘅需要同現時保障")
    
    # 問題1
    risk = st.selectbox(
        "1. 你而家最擔心嘅健康風險係咩？",
        ["癌症", "心臟病", "中風", "意外受傷", "其他"]
    )
    
    # 問題2
    budget = st.number_input("2. 如果突然要住院，你 budget 係幾多一晚？", min_value=0, step=500, value=1000)
    
    # 問題3
    has_insurance = st.radio("3. 你而家有冇買醫療保險？", ["有", "冇"], horizontal=True)
    
    company = ""
    if has_insurance == "有":
        company = st.text_input("邊間保險公司？")
    
    # 問題4
    inpatient_amount = 0
    if has_insurance == "有":
        inpatient_amount = st.number_input("4. 你份保單住院一晚賠幾多？", min_value=0, step=500, value=0)
    
    # 問題5
    cancer_cover = "冇"
    if has_insurance == "有":
        cancer_cover = st.radio("5. 你份保單有冇包癌症治療？", ["有", "冇", "唔知"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            st.session_state.client_data["risk"] = risk
            st.session_state.client_data["budget"] = budget
            st.session_state.client_data["has_insurance"] = has_insurance
            st.session_state.client_data["company"] = company
            st.session_state.client_data["inpatient_amount"] = inpatient_amount
            st.session_state.client_data["cancer_cover"] = cancer_cover
            st.session_state.step = 3
            st.rerun()

# ==================== 第三步：計算結果 ====================
elif st.session_state.step == 3:
    st.header("📊 第三步：保障缺口分析")
    
    data = st.session_state.client_data
    
    # 計算標準（$1,000/晚為基本標準）
    standard_inpatient = 1000
    standard_surgery = 100000
    standard_deductible = 10000
    
    # 計算缺口
    inpatient_gap = max(0, standard_inpatient - data["inpatient_amount"]) if data["has_insurance"] == "有" else standard_inpatient
    
    # 顯示結果表格
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("住院標準", f"${standard_inpatient:,}/晚")
        st.metric("手術標準", f"${standard_surgery:,}")
    with col2:
        if data["has_insurance"] == "有":
            st.metric("你現時住院", f"${data['inpatient_amount']:,}/晚", 
                     delta=f"差額 ${inpatient_gap:,}" if inpatient_gap > 0 else None,
                     delta_color="inverse" if inpatient_gap > 0 else "off")
            st.metric("癌症保障", data["cancer_cover"])
        else:
            st.warning("你現時未有醫療保險")
    
    # 總結缺口
    st.divider()
    st.subheader("🔍 主要缺口")
    
    gaps = []
    if data["has_insurance"] == "冇":
        gaps.append("完全沒有醫療保險")
    else:
        if inpatient_gap > 0:
            gaps.append(f"住院保障不足，每晚差額 ${inpatient_gap:,}")
        if data["cancer_cover"] != "有":
            gaps.append("缺乏癌症保障（標靶藥、化療）")
    
    if gaps:
        for gap in gaps:
            st.error(f"⚠️ {gap}")
    else:
        st.success("✅ 無明顯缺口，保障足夠")
    
    # 建議行動
    st.subheader("💡 建議行動")
    if data["has_insurance"] == "冇":
        st.info("建議：盡快建立基本醫療保障，可考慮自願醫保計劃")
    else:
        if inpatient_gap > 0 or data["cancer_cover"] != "有":
            st.info("建議：考慮升級現有計劃，填補以上缺口")
        else:
            st.success("建議：定期檢視，保持現有保障")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回修改"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("生成報告 →"):
            st.session_state.step = 4
            st.rerun()

# ==================== 第四步：生成報告 ====================
elif st.session_state.step == 4:
    st.header("📄 第四步：報告總結")
    
    data = st.session_state.client_data
    
    # 顯示報告內容
    st.markdown("### 醫療保險快速檢視報告")
    st.markdown(f"**客人姓名**：{data['name']}")
    st.markdown(f"**檢視日期**：{data['date']}")
    st.markdown("---")
    
    st.markdown("#### 一、你嘅保障現況")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"- 擔心風險：{data['risk']}")
        st.markdown(f"- 住院預算：${data['budget']:,}/晚")
    with col2:
        st.markdown(f"- 有冇保險：{data['has_insurance']}")
        if data['has_insurance'] == '有':
            st.markdown(f"- 保險公司：{data['company']}")
    
    st.markdown("#### 二、保障缺口")
    if data['has_insurance'] == '冇':
        st.warning("⚠️ 完全沒有醫療保險")
    else:
        inpatient_gap = max(0, 1000 - data['inpatient_amount'])
        if inpatient_gap > 0:
            st.warning(f"⚠️ 住院保障不足，每晚差額 ${inpatient_gap:,}")
        if data['cancer_cover'] != '有':
            st.warning("⚠️ 缺乏癌症保障")
    
    st.markdown("#### 三、建議行動")
    if data['has_insurance'] == '冇':
        st.info("建議盡快建立基本醫療保障")
    else:
        if inpatient_gap > 0 or data['cancer_cover'] != '有':
            st.info("建議升級現有計劃，填補保障缺口")
        else:
            st.success("保障足夠，建議每年檢視一次")
    
    st.markdown("---")
    st.markdown("*無壓力・唔使買・純粹幫你睇*")
    st.caption(f"顧問：淇錡")
    
    # 下載報告功能
    report_text = f"""
醫療快速檢視報告
客人：{data['name']}
日期：{data['date']}

一、保障現況
- 擔心風險：{data['risk']}
- 住院預算：${data['budget']:,}/晚
- 有冇保險：{data['has_insurance']}

二、缺口分析
{'- 完全沒有醫療保險' if data['has_insurance'] == '冇' else f'- 住院差額：${max(0, 1000 - data['inpatient_amount']):,}/晚'}

三、建議
{'建議盡快建立基本醫療保障' if data['has_insurance'] == '冇' else '建議檢視及升級保障'}
    """
    
    st.download_button(
        label="📥 下載報告 (TXT)",
        data=report_text,
        file_name=f"醫療報告_{data['name']}.txt",
        mime="text/plain"
    )
    
    if st.button("← 開始新檢視"):
        st.session_state.step = 1
        st.session_state.client_data = {}
        st.rerun()

