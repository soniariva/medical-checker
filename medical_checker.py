import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

def save_to_google_sheets(data):
    url = "https://script.google.com/macros/s/AKfycbxuoIJBs_MHy7XekB8RiOCtyiyiZghm22wS-8HRBv2IfZ9-dti9-1kMlo3PA0kNG4Ti/exec"
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
        "education_fund": data.get("edu_fund", 0),
        "life_insurance": data.get("life", 0),
        "monthly_expense": data.get("monthly_expense", 0),
        "mortgage": data.get("mortgage", 0),
        "total_income": data.get("total_income", 0)
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.success("✅ 报告已保存，Sonia 会跟进！")
        else:
            st.warning("⚠️ 保存失败，但你可以手动截图报告给我。")
    except:
        st.warning("⚠️ 网络问题，请稍后再试。")


# 頁面設定
st.set_page_config(page_title="15分鐘保險檢視", page_icon="🩺", layout="wide")

# 標題
st.title("🩺 15分鐘保險檢視")
st.caption("輸入你嘅數字，系統會自動計算保障缺口")

# ==================== 側邊欄：對比價目表（添加千位分隔符） ====================
with st.sidebar:
    st.header("💰 費用 vs 賠償 對比價目表")
    st.caption("以下係常見項目嘅參考費用")
    
    compare_type = st.radio(
        "揀選保障類型",
        ["醫療", "危疾", "意外"],
        horizontal=True
    )
    
    if compare_type == "醫療":
        compare_data = {
            "項目": ["專科門診", "住院 (大房/晚)", "住院 (半私家/晚)", 
                     "大型手術", "複雜手術", "標靶藥 (每月)", "MRI 掃描"],
            "實際費用 (HK$)": [800, 1200, 2500, 40000, 300000, 60000, 8000],
            "基本保單賠償 (HK$)": [0, 750, 1200, 25000, 50000, 0, 2000],
        }
        df_compare = pd.DataFrame(compare_data)
        df_compare["實際費用 (HK$)"] = df_compare["實際費用 (HK$)"].apply(lambda x: f"{x:,}")
        df_compare["基本保單賠償 (HK$)"] = df_compare["基本保單賠償 (HK$)"].apply(lambda x: f"{x:,}")
        df_compare["你要自付 (HK$)"] = (pd.to_numeric(df_compare["實際費用 (HK$)"].str.replace(",", "")) - 
                                         pd.to_numeric(df_compare["基本保單賠償 (HK$)"].str.replace(",", ""))).apply(lambda x: f"{x:,}")
        st.dataframe(df_compare, use_container_width=True)
        st.info("💡 醫療：住院、手術、癌症治療費用")
        
    elif compare_type == "危疾":
        compare_data = {
            "危疾項目": ["癌症", "心臟病", "中風", "腎衰竭", "主要器官移植"],
            "平均治療費用 (HK$)": [800000, 500000, 400000, 1000000, 1500000],
            "危疾賠償 (HK$)": [1000000, 1000000, 800000, 1000000, 1000000],
        }
        df_compare = pd.DataFrame(compare_data)
        df_compare["平均治療費用 (HK$)"] = df_compare["平均治療費用 (HK$)"].apply(lambda x: f"{x:,}")
        df_compare["危疾賠償 (HK$)"] = df_compare["危疾賠償 (HK$)"].apply(lambda x: f"{x:,}")
        df_compare["賠償後剩餘"] = (pd.to_numeric(df_compare["危疾賠償 (HK$)"].str.replace(",", "")) - 
                                      pd.to_numeric(df_compare["平均治療費用 (HK$)"].str.replace(",", ""))).apply(lambda x: f"{x:,}")
        st.dataframe(df_compare, use_container_width=True)
        st.info("💡 危疾：確診即賠一筆過，用於治療及生活開支")
        
    else:
        compare_data = {
            "意外項目": ["骨折住院", "燒燙傷治療", "意外手術", "永久傷殘", "意外身故"],
            "平均費用 (HK$)": [80000, 200000, 50000, 0, 0],
            "意外保險賠償 (HK$)": [50000, 100000, 50000, 1000000, 1000000],
        }
        df_compare = pd.DataFrame(compare_data)
        df_compare["平均費用 (HK$)"] = df_compare["平均費用 (HK$)"].apply(lambda x: f"{x:,}" if x > 0 else "0")
        df_compare["意外保險賠償 (HK$)"] = df_compare["意外保險賠償 (HK$)"].apply(lambda x: f"{x:,}")
        df_compare["你要自付 (HK$)"] = (pd.to_numeric(df_compare["平均費用 (HK$)"].str.replace(",", "")) - 
                                         pd.to_numeric(df_compare["意外保險賠償 (HK$)"].str.replace(",", ""))).apply(lambda x: f"{max(0, x):,}")
        st.dataframe(df_compare, use_container_width=True)
        st.info("💡 意外：因意外受傷引致嘅醫療費用及賠償")


# ==================== 主頁面 ====================
if "step" not in st.session_state:
    st.session_state.step = 1
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

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

# ==================== 第二步：輸入現有保單銀碼（與市場費用並列） ====================
elif st.session_state.step == 2:
    st.header("📝 第二步：輸入你現有保單嘅保障額")
    st.info("下表左邊係市場參考費用，右邊請輸入你份保單嘅賠償金額（如無該項保障，請填 0）")
    
    # 市場參考費用
    market = {
        "住院 (大房/晚)": 1200,
        "大型手術 (每次)": 40000,
        "癌症治療 (每年)": 720000,
        "危疾一筆過賠償": 800000,
        "意外醫療 (每年)": 50000,
        "意外身故/傷殘": 1000000
    }
    
    # 建立輸入表格
    st.subheader("🏥 醫療保障")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown("**保障項目**")
        st.text("住院 (大房/晚)")
        st.text("大型手術 (每次)")
        st.text("癌症治療 (每年)")
    with col2:
        st.markdown("**市場參考費用**")
        st.text(f"HK$ {market['住院 (大房/晚)']:,}")
        st.text(f"HK$ {market['大型手術 (每次)']:,}")
        st.text(f"HK$ {market['癌症治療 (每年)']:,}")
    with col3:
        st.markdown("**你現有賠償 (HK$)**")
        inpatient = st.number_input("住院賠償", min_value=0, step=500, value=0, label_visibility="collapsed", key="inpatient")
        surgery = st.number_input("手術賠償", min_value=0, step=10000, value=0, label_visibility="collapsed", key="surgery")
        cancer = st.number_input("癌症治療賠償", min_value=0, step=50000, value=0, label_visibility="collapsed", key="cancer")
    
    st.divider()
    st.subheader("❤️ 危疾保障")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown("**保障項目**")
        st.text("危疾一筆過賠償")
    with col2:
        st.markdown("**市場參考費用**")
        st.text(f"HK$ {market['危疾一筆過賠償']:,}")
    with col3:
        critical = st.number_input("危疾賠償", min_value=0, step=100000, value=0, label_visibility="collapsed", key="critical")
    
    st.divider()
    st.subheader("⚠️ 意外保障")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown("**保障項目**")
        st.text("意外醫療 (每年)")
        st.text("意外身故/傷殘")
    with col2:
        st.markdown("**市場參考費用**")
        st.text(f"HK$ {market['意外醫療 (每年)']:,}")
        st.text(f"HK$ {market['意外身故/傷殘']:,}")
    with col3:
        accident_med = st.number_input("意外醫療賠償", min_value=0, step=10000, value=0, label_visibility="collapsed", key="accident_med")
        accident_death = st.number_input("意外身故賠償", min_value=0, step=100000, value=0, label_visibility="collapsed", key="accident_death")
    
    # 其他資料
    risk = st.selectbox("最擔心嘅健康風險", ["癌症", "心臟病", "中風", "意外受傷", "其他"])
    budget = st.number_input("你認為住院一晚需要幾多預算？", min_value=0, step=500, value=1000)
    has_medical = st.radio("有冇買醫療保險？", ["有", "冇"], horizontal=True)
    company = ""
    if has_medical == "有":
        company = st.text_input("保險公司名稱")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("下一步 →"):
            # 儲存所有數據
            st.session_state.client_data["risk"] = risk
            st.session_state.client_data["budget"] = budget
            st.session_state.client_data["has_medical"] = has_medical
            st.session_state.client_data["company"] = company
            st.session_state.client_data["inpatient_amount"] = inpatient
            st.session_state.client_data["surgery_amount"] = surgery
            st.session_state.client_data["cancer_amount"] = cancer
            st.session_state.client_data["critical_amount"] = critical
            st.session_state.client_data["accident_medical"] = accident_med
            st.session_state.client_data["accident_death"] = accident_death
            st.session_state.step = 3
            st.rerun()

# ==================== 第三步：分析缺口 ====================
elif st.session_state.step == 3:
    st.header("📊 第三步：保障缺口分析")
    data = st.session_state.client_data
    
    # 市場參考費用（與第二步一致）
    market_inpatient = 1200
    market_surgery = 40000
    market_cancer = 720000
    market_critical = 800000
    market_acc_med = 50000
    market_acc_death = 1000000
    
    # 計算差額
    inpatient_gap = max(0, market_inpatient - data["inpatient_amount"])
    surgery_gap = max(0, market_surgery - data["surgery_amount"])
    cancer_gap = max(0, market_cancer - data["cancer_amount"])
    critical_gap = max(0, market_critical - data["critical_amount"])
    acc_med_gap = max(0, market_acc_med - data["accident_medical"])
    acc_death_gap = max(0, market_acc_death - data["accident_death"])
    
    # 顯示對比表格
    st.markdown("### 市場費用 vs 你現有保障")
    compare_df = pd.DataFrame({
        "保障項目": ["住院 (每晚)", "大型手術 (每次)", "癌症治療 (每年)", "危疾 (一筆過)", "意外醫療 (每年)", "意外身故/傷殘"],
        "市場參考費用": [f"${market_inpatient:,}", f"${market_surgery:,}", f"${market_cancer:,}", f"${market_critical:,}", f"${market_acc_med:,}", f"${market_acc_death:,}"],
        "你現有賠償": [f"${data['inpatient_amount']:,}", f"${data['surgery_amount']:,}", f"${data['cancer_amount']:,}", 
                       f"${data['critical_amount']:,}", f"${data['accident_medical']:,}", f"${data['accident_death']:,}"],
        "差額 (不足)": [f"${inpatient_gap:,}", f"${surgery_gap:,}", f"${cancer_gap:,}", 
                        f"${critical_gap:,}", f"${acc_med_gap:,}", f"${acc_death_gap:,}"]
    })
    st.dataframe(compare_df, use_container_width=True)
    
    # 主要缺口
    st.divider()
    st.subheader("🔍 主要缺口")
    gaps = []
    if inpatient_gap > 0:
        gaps.append(f"住院保障不足，每晚差額 ${inpatient_gap:,}")
    if surgery_gap > 0:
        gaps.append(f"手術保障不足，每次差額 ${surgery_gap:,}")
    if cancer_gap > 0:
        gaps.append(f"癌症治療保障不足，每年差額 ${cancer_gap:,}")
    if critical_gap > 0:
        gaps.append(f"危疾保障不足，一筆過差額 ${critical_gap:,}")
    if acc_med_gap > 0:
        gaps.append(f"意外醫療保障不足，每年差額 ${acc_med_gap:,}")
    if acc_death_gap > 0:
        gaps.append(f"意外身故保障不足，差額 ${acc_death_gap:,}")
    
    if gaps:
        for g in gaps:
            st.error(f"⚠️ {g}")
    else:
        st.success("✅ 所有保障均達到市場參考水平，無明顯缺口")
    
    # 建議行動
    st.subheader("💡 建議行動")
    recommendations = []
    if data["inpatient_amount"] == 0 and data["surgery_amount"] == 0 and data["cancer_amount"] == 0:
        recommendations.append("完全沒有醫療保險，建議立即配置自願醫保靈活計劃")
    else:
        if inpatient_gap > 0 or surgery_gap > 0 or cancer_gap > 0:
            recommendations.append("升級醫療保險，提高住院、手術及癌症治療賠償額")
    if data["critical_amount"] == 0:
        recommendations.append("完全沒有危疾保險，建議添置，保額最少 $1,000,000")
    elif critical_gap > 0:
        recommendations.append("增加危疾保額至 $1,000,000 或以上")
    if data["accident_medical"] == 0 and data["accident_death"] == 0:
        recommendations.append("完全沒有意外保險，建議添置")
    else:
        if acc_med_gap > 0 or acc_death_gap > 0:
            recommendations.append("加強意外保險，提高醫療及身故賠償")
    
    for rec in recommendations:
        st.info(f"📌 {rec}")
    
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
    
    # 重新計算（與第三步相同）
    market_inpatient = 1200
    market_surgery = 40000
    market_cancer = 720000
    market_critical = 800000
    market_acc_med = 50000
    market_acc_death = 1000000
    
    inpatient_gap = max(0, market_inpatient - data["inpatient_amount"])
    surgery_gap = max(0, market_surgery - data["surgery_amount"])
    cancer_gap = max(0, market_cancer - data["cancer_amount"])
    critical_gap = max(0, market_critical - data["critical_amount"])
    acc_med_gap = max(0, market_acc_med - data["accident_medical"])
    acc_death_gap = max(0, market_acc_death - data["accident_death"])
    
    st.markdown("### 保險快速檢視報告")
    st.markdown(f"**客人姓名**：{data['name']}")
    st.markdown(f"**檢視日期**：{data['date']}")
    st.markdown("---")
    
    st.markdown("#### 一、醫療保障對比")
    st.markdown(f"- **住院**：現有 HK$ {data['inpatient_amount']:,}/晚，市場參考 HK$ {market_inpatient:,}，**差額 HK$ {inpatient_gap:,}/晚**")
    st.markdown(f"- **手術**：現有 HK$ {data['surgery_amount']:,}/次，市場參考 HK$ {market_surgery:,}，**差額 HK$ {surgery_gap:,}/次**")
    st.markdown(f"- **癌症治療**：現有 HK$ {data['cancer_amount']:,}/年，市場參考 HK$ {market_cancer:,}，**差額 HK$ {cancer_gap:,}/年**")
    
    st.markdown("#### 二、危疾保障對比")
    st.markdown(f"- 現有賠償：HK$ {data['critical_amount']:,}，市場參考治療費 HK$ {market_critical:,}，**差額 HK$ {critical_gap:,}**")
    
    st.markdown("#### 三、意外保障對比")
    st.markdown(f"- **意外醫療**：現有 HK$ {data['accident_medical']:,}/年，市場參考 HK$ {market_acc_med:,}，**差額 HK$ {acc_med_gap:,}/年**")
    st.markdown(f"- **意外身故/傷殘**：現有 HK$ {data['accident_death']:,}，市場參考 HK$ {market_acc_death:,}，**差額 HK$ {acc_death_gap:,}**")
    
    st.markdown("---")
    st.markdown("*無壓力・唔使買・純粹幫你睇*")
    st.caption("顧問：Sonia")
    
    # 下載報告
    report_text = f"""
保險快速檢視報告
客人：{data['name']}
日期：{data['date']}

一、醫療保障
- 住院：現有 HK$ {data['inpatient_amount']:,}/晚，市場 HK$ {market_inpatient:,}，差額 HK$ {inpatient_gap:,}
- 手術：現有 HK$ {data['surgery_amount']:,}/次，市場 HK$ {market_surgery:,}，差額 HK$ {surgery_gap:,}
- 癌症治療：現有 HK$ {data['cancer_amount']:,}/年，市場 HK$ {market_cancer:,}，差額 HK$ {cancer_gap:,}

二、危疾保障
- 現有 HK$ {data['critical_amount']:,}，市場參考 HK$ {market_critical:,}，差額 HK$ {critical_gap:,}

三、意外保障
- 意外醫療：現有 HK$ {data['accident_medical']:,}/年，市場 HK$ {market_acc_med:,}，差額 HK$ {acc_med_gap:,}
- 意外身故：現有 HK$ {data['accident_death']:,}，市場 HK$ {market_acc_death:,}，差額 HK$ {acc_death_gap:,}

---
無壓力・唔使買・純粹幫你睇
顧問：Sonia
    """
    
    st.download_button(
        label="📥 下載報告 (TXT)",
        data=report_text,
        file_name=f"保險報告_{data['name']}.txt",
        mime="text/plain"
    )

# 新加入嘅提交按鈕
if st.button("📤 提交並儲存記錄"):
    # 收集所有數據
    all_data = {
        "name": st.session_state.client_data.get("name"),
        "phone": st.session_state.client_data.get("phone"),
        "risk": st.session_state.client_data.get("risk"),
        "budget": st.session_state.client_data.get("budget"),
        "has_medical": st.session_state.client_data.get("has_medical"),
        "company": st.session_state.client_data.get("company"),
        "inpatient_amount": st.session_state.client_data.get("inpatient_amount"),
        "surgery_amount": st.session_state.client_data.get("surgery_amount"),
        "cancer_amount": st.session_state.client_data.get("cancer_amount"),
        "critical_amount": st.session_state.client_data.get("critical_amount"),
        "accident_medical": st.session_state.client_data.get("accident_medical"),
        "accident_death": st.session_state.client_data.get("accident_death"),
        "edu_fund": st.session_state.client_data.get("edu_fund"),
        "life": st.session_state.client_data.get("life"),
        "monthly_expense": st.session_state.client_data.get("monthly_expense"),
        "mortgage": st.session_state.client_data.get("mortgage"),
        "total_income": st.session_state.client_data.get("annual_income", 0) + st.session_state.client_data.get("spouse_income", 0)
    }
    save_to_google_sheets(all_data)

    if st.button("← 開始新檢視"):
        st.session_state.step = 1
        st.session_state.client_data = {}
        st.rerun()
