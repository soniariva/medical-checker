import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==================== 設定 ====================
# 請修改為你 Google Apps Script 的網址（如果不想儲存，可設為 None）
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxuoIJBs_MHy7XekB8RiOCtyiyiZghm22wS-8HRBv2IfZ9-dti9-1kMlo3PA0kNG4Ti/exec"   # 改為你的網址
SAVE_TO_SHEETS = True   # 是否儲存到 Google Sheets

# ==================== 儲存函數（靜默） ====================
def save_to_google_sheets(data):
    if not SAVE_TO_SHEETS or not WEBAPP_URL:
        return
    try:
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "risk": data.get("risk", ""),
            "budget": data.get("budget", 0),
            "has_medical": data.get("has_medical", ""),
            "company": data.get("company", ""),
            "inpatient_amount": data.get("inpatient_amount", 0),
            "surgery_amount": data.get("surgery_amount", 0),
            "cancer_amount": data.get("cancer_amount", 0),
            "critical_amount": data.get("critical_amount", 0),
            "accident_medical": data.get("accident_medical", 0),
            "accident_death": data.get("accident_death", 0),
            "monthly_expense": data.get("monthly_expense", 0),
            "mortgage": data.get("mortgage", 0),
            "total_income": data.get("total_income", 0)
        }
        requests.post(WEBAPP_URL, json=payload, timeout=5)
    except:
        pass   # 靜默失敗，不影響用戶體驗

# ==================== 頁面設定 ====================
st.set_page_config(page_title="15分鐘保險檢視", page_icon="🩺", layout="wide")
st.title("🩺 15分鐘保險檢視")
st.caption("輸入你嘅資料，系統會自動計算保障缺口")

# 初始化 session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

# 進度條
st.progress(st.session_state.step / 4)

# ==================== 第一步：基本資料 ====================
if st.session_state.step == 1:
    st.header("📋 第一步：基本資料")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名")
    with col2:
        phone = st.text_input("聯絡電話")
    date = st.date_input("檢視日期", datetime.today())
    
    if st.button("下一步 →"):
        if name:
            st.session_state.client_data["name"] = name
            st.session_state.client_data["phone"] = phone
            st.session_state.client_data["date"] = str(date)
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("請輸入姓名")

# ==================== 第二步：醫療保障 ====================
elif st.session_state.step == 2:
    st.header("🏥 醫療保障")
    risk = st.selectbox("最擔心嘅健康風險", ["癌症", "心臟病", "中風", "意外受傷", "其他"])
    budget = st.number_input("你認為住院一晚需要幾多預算？", min_value=0, step=500, value=1000)
    
    has_medical = st.radio("有冇買醫療保險？", ["有", "冇"], horizontal=True)
    company = ""
    inpatient = surgery = cancer = 0
    if has_medical == "有":
        company = st.text_input("保險公司名稱")
        col1, col2 = st.columns(2)
        with col1:
            inpatient = st.number_input("住院賠償 (每晚)", min_value=0, step=500)
            cancer = st.number_input("癌症治療賠償 (每年)", min_value=0, step=50000)
        with col2:
            surgery = st.number_input("手術賠償 (每次)", min_value=0, step=10000)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            st.session_state.client_data["risk"] = risk
            st.session_state.client_data["budget"] = budget
            st.session_state.client_data["has_medical"] = has_medical
            st.session_state.client_data["company"] = company
            st.session_state.client_data["inpatient"] = inpatient
            st.session_state.client_data["surgery"] = surgery
            st.session_state.client_data["cancer"] = cancer
            st.session_state.step = 3
            st.rerun()

# ==================== 第三步：危疾 + 意外 ====================
elif st.session_state.step == 3:
    st.header("❤️ 危疾保障")
    has_critical = st.radio("有冇買危疾保險？", ["有", "冇"], horizontal=True)
    critical_amount = 0
    if has_critical == "有":
        critical_amount = st.number_input("危疾一筆過賠償額", min_value=0, step=100000, value=0)
    
    st.divider()
    st.header("⚠️ 意外保障")
    has_accident = st.radio("有冇買意外保險？", ["有", "冇"], horizontal=True)
    accident_medical = 0
    accident_death = 0
    if has_accident == "有":
        col1, col2 = st.columns(2)
        with col1:
            accident_medical = st.number_input("意外醫療賠償 (每年)", min_value=0, step=10000)
        with col2:
            accident_death = st.number_input("意外身故/傷殘賠償", min_value=0, step=100000)
    
    st.divider()
    st.subheader("💰 家庭財務 (簡要)")
    monthly_expense = st.number_input("每月家庭開支 (HK$)", min_value=0, step=5000, value=0)
    mortgage = st.number_input("按揭貸款餘額 (HK$)", min_value=0, step=100000, value=0)
    annual_income = st.number_input("家庭年收入 (HK$)", min_value=0, step=50000, value=0)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            st.session_state.client_data["has_critical"] = has_critical
            st.session_state.client_data["critical_amount"] = critical_amount
            st.session_state.client_data["has_accident"] = has_accident
            st.session_state.client_data["accident_medical"] = accident_medical
            st.session_state.client_data["accident_death"] = accident_death
            st.session_state.client_data["monthly_expense"] = monthly_expense
            st.session_state.client_data["mortgage"] = mortgage
            st.session_state.client_data["annual_income"] = annual_income
            st.session_state.step = 4
            st.rerun()

# ==================== 第四步：報告 + 儲存按鈕 ====================
elif st.session_state.step == 4:
    st.header("📄 保險快速檢視報告")
    data = st.session_state.client_data
    
    # 計算建議值
    recommended_life = data.get("monthly_expense", 0) * 12 * 10 + data.get("mortgage", 0)
    
    # 顯示報告摘要
    st.markdown(f"**姓名**：{data['name']}  &nbsp;&nbsp; **日期**：{data['date']}")
    st.markdown("---")
    
    st.markdown("#### 🏥 醫療保障")
    st.markdown(f"- 住院：現有 HK$ {data['inpatient']:,}/晚（參考 HK$ 1,200/晚）")
    st.markdown(f"- 手術：現有 HK$ {data['surgery']:,}/次（參考 HK$ 40,000/次）")
    st.markdown(f"- 癌症治療：現有 HK$ {data['cancer']:,}/年（參考 HK$ 720,000/年）")
    
    st.markdown("#### ❤️ 危疾保障")
    st.markdown(f"- 危疾一筆過：HK$ {data['critical_amount']:,}（參考 HK$ 1,000,000）")
    
    st.markdown("#### ⚠️ 意外保障")
    st.markdown(f"- 意外醫療：HK$ {data['accident_medical']:,}/年（參考 HK$ 50,000/年）")
    st.markdown(f"- 意外身故：HK$ {data['accident_death']:,}（參考 HK$ 1,000,000）")
    
    st.markdown("#### 💰 人壽需求（粗略）")
    st.markdown(f"- 建議人壽保額：HK$ {recommended_life:,.0f}（10年生活費＋房貸）")
    if data.get("life", 0) > 0:
        st.markdown(f"- 現有人壽：HK$ {data['life']:,}")
    else:
        st.markdown("- 現有人壽：未有資料")
    
    st.markdown("---")
    st.caption("以上數字僅供參考，實際保障需按個人情況調整。")
    
    # 準備報告文字（用於下載）
    report_text = f"""
15分鐘保險檢視報告
姓名：{data['name']}
日期：{data['date']}

醫療保障
- 住院賠償：HK$ {data['inpatient']:,}/晚
- 手術賠償：HK$ {data['surgery']:,}/次
- 癌症治療：HK$ {data['cancer']:,}/年

危疾保障：HK$ {data['critical_amount']:,}

意外保障
- 醫療：HK$ {data['accident_medical']:,}/年
- 身故/傷殘：HK$ {data['accident_death']:,}

人壽需求：建議 HK$ {recommended_life:,.0f}

--- 
無壓力・唔使買・純粹幫你睇
    """
    
    # 只有一個按鈕：儲蓄記錄
    if st.button("💾 儲蓄記錄"):
        # 1. 下載報告
        st.download_button(
            label="📥 按此下載報告",
            data=report_text,
            file_name=f"保險報告_{data['name']}.txt",
            mime="text/plain",
            key="download_unique"
        )
        # 2. 儲存到 Google Sheets（靜默）
        save_data = {
            "name": data.get("name"),
            "phone": data.get("phone"),
            "risk": data.get("risk"),
            "budget": data.get("budget"),
            "has_medical": data.get("has_medical"),
            "company": data.get("company"),
            "inpatient_amount": data.get("inpatient"),
            "surgery_amount": data.get("surgery"),
            "cancer_amount": data.get("cancer"),
            "critical_amount": data.get("critical_amount"),
            "accident_medical": data.get("accident_medical"),
            "accident_death": data.get("accident_death"),
            "monthly_expense": data.get("monthly_expense"),
            "mortgage": data.get("mortgage"),
            "total_income": data.get("annual_income", 0)
        }
        save_to_google_sheets(save_data)
        # 顯示簡短提示（可選，但不會提到 Sonia）
        st.success("報告已下載，多謝使用！")
        # 自動重設或提供重新開始的按鈕
        if st.button("🔄 開始新檢視"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
