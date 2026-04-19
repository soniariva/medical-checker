import streamlit as st
import pandas as pd
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="15分鐘保險檢視", page_icon="🩺", layout="wide")

# 標題
st.title("🩺 15分鐘保險檢視")
st.caption("輸入你嘅數字，系統會自動計算保障缺口")

# ==================== 側邊欄：對比價目表 ====================
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
        df_compare["你要自付 (HK$)"] = df_compare["實際費用 (HK$)"] - df_compare["基本保單賠償 (HK$)"]
        st.dataframe(df_compare, use_container_width=True)
        st.info("💡 醫療：住院、手術、癌症治療費用")
        
    elif compare_type == "危疾":
        compare_data = {
            "危疾項目": ["癌症", "心臟病", "中風", "腎衰竭", "主要器官移植"],
            "平均治療費用 (HK$)": [800000, 500000, 400000, 1000000, 1500000],
            "危疾賠償 (HK$)": [1000000, 1000000, 800000, 1000000, 1000000],
        }
        df_compare = pd.DataFrame(compare_data)
        df_compare["賠償後剩餘"] = df_compare["危疾賠償 (HK$)"] - df_compare["平均治療費用 (HK$)"]
        st.dataframe(df_compare, use_container_width=True)
        st.info("💡 危疾：確診即賠一筆過，用於治療及生活開支")
        
    else:
        compare_data = {
            "意外項目": ["骨折住院", "燒燙傷治療", "意外手術", "永久傷殘", "意外身故"],
            "平均費用 (HK$)": [80000, 200000, 50000, 0, 0],
            "意外保險賠償 (HK$)": [50000, 100000, 50000, 1000000, 1000000],
        }
        df_compare = pd.DataFrame(compare_data)
        df_compare["你要自付 (HK$)"] = df_compare["平均費用 (HK$)"] - df_compare["意外保險賠償 (HK$)"]
        df_compare.loc[df_compare["你要自付 (HK$)"] < 0, "你要自付 (HK$)"] = 0
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

# ==================== 第二步：輸入現有保障額 ====================
elif st.session_state.step == 2:
    st.header("📝 第二步：輸入你現有保單嘅保障額")
    st.info("請填寫你現有保險計劃嘅賠償金額，如果冇該項保障，請留空或輸入 0")
    
    # ----- 醫療保障 -----
    st.subheader("🏥 醫療保障")
    col1, col2 = st.columns(2)
    with col1:
        risk = st.selectbox(
            "最擔心嘅健康風險",
            ["癌症", "心臟病", "中風", "意外受傷", "其他"]
        )
    with col2:
        budget = st.number_input("你認為住院一晚需要幾多預算？", min_value=0, step=500, value=1000)
    
    has_medical = st.radio("有冇買醫療保險？", ["有", "冇"], horizontal=True)
    
    company = ""
    inpatient_amount = 0
    surgery_amount = 0
    cancer_amount = 0
    if has_medical == "有":
        company = st.text_input("保險公司名稱")
        col_a, col_b = st.columns(2)
        with col_a:
            inpatient_amount = st.number_input("住院賠償額 (每晚)", min_value=0, step=500, value=0)
            surgery_amount = st.number_input("手術賠償額 (每次)", min_value=0, step=10000, value=0)
        with col_b:
            cancer_amount = st.number_input("癌症治療賠償額 (每年)", min_value=0, step=50000, value=0,
                                            help="例如標靶藥、化療、電療等每年最高賠償")
    
    st.divider()
    
    # ----- 危疾保障 -----
    st.subheader("❤️ 危疾保障")
    has_critical = st.radio("有冇買危疾保險？", ["有", "冇"], horizontal=True)
    critical_amount = 0
    if has_critical == "有":
        critical_amount = st.number_input("危疾一筆過賠償額", min_value=0, step=100000, value=0, format="%d")
    
    st.divider()
    
    # ----- 意外保障 -----
    st.subheader("⚠️ 意外保障")
    has_accident = st.radio("有冇買意外保險？", ["有", "冇"], horizontal=True)
    accident_medical = 0
    accident_death = 0
    if has_accident == "有":
        col1, col2 = st.columns(2)
        with col1:
            accident_medical = st.number_input("意外醫療賠償 (每年)", min_value=0, step=10000, value=0)
        with col2:
            accident_death = st.number_input("意外身故/永久傷殘賠償", min_value=0, step=100000, value=0)
    
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
            st.session_state.client_data["inpatient_amount"] = inpatient_amount
            st.session_state.client_data["surgery_amount"] = surgery_amount
            st.session_state.client_data["cancer_amount"] = cancer_amount
            st.session_state.client_data["has_critical"] = has_critical
            st.session_state.client_data["critical_amount"] = critical_amount
            st.session_state.client_data["has_accident"] = has_accident
            st.session_state.client_data["accident_medical"] = accident_medical
            st.session_state.client_data["accident_death"] = accident_death
            st.session_state.step = 3
            st.rerun()

# ==================== 第三步：分析缺口 ====================
elif st.session_state.step == 3:
    st.header("📊 第三步：保障缺口分析")
    
    data = st.session_state.client_data
    
    # 市場參考費用（取自側邊欄）
    market_inpatient = 1200      # 大房每晚
    market_surgery = 40000       # 大型手術
    market_cancer_yearly = 720000  # 標靶藥每月6萬 x12
    market_critical = 800000     # 癌症平均治療費（危疾可對比）
    market_accident_medical = 50000   # 意外醫療每年參考
    market_accident_death = 1000000   # 意外身故參考
    
    # 計算差額（正數表示不足）
    inpatient_gap = max(0, market_inpatient - data["inpatient_amount"]) if data["has_medical"] == "有" else market_inpatient
    surgery_gap = max(0, market_surgery - data["surgery_amount"]) if data["has_medical"] == "有" else market_surgery
    cancer_gap = max(0, market_cancer_yearly - data["cancer_amount"]) if data["has_medical"] == "有" else market_cancer_yearly
    critical_gap = max(0, market_critical - data["critical_amount"]) if data["has_critical"] == "有" else market_critical
    accident_medical_gap = max(0, market_accident_medical - data["accident_medical"]) if data["has_accident"] == "有" else market_accident_medical
    accident_death_gap = max(0, market_accident_death - data["accident_death"]) if data["has_accident"] == "有" else market_accident_death
    
    # 顯示分頁
    tab1, tab2, tab3 = st.tabs(["🏥 醫療", "❤️ 危疾", "⚠️ 意外"])
    
    with tab1:
        st.markdown("**市場參考費用**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("住院 (大房/晚)", f"HK$ {market_inpatient:,}")
            st.metric("大型手術 (每次)", f"HK$ {market_surgery:,}")
        with col2:
            st.metric("癌症治療 (每年)", f"HK$ {market_cancer_yearly:,}")
        
        st.markdown("**你現有保障**")
        if data["has_medical"] == "有":
            col1, col2 = st.columns(2)
            with col1:
                st.metric("住院賠償", f"HK$ {data['inpatient_amount']:,}",
                         delta=f"差額 HK$ {inpatient_gap:,}" if inpatient_gap > 0 else "足夠",
                         delta_color="inverse" if inpatient_gap > 0 else "off")
                st.metric("手術賠償", f"HK$ {data['surgery_amount']:,}",
                         delta=f"差額 HK$ {surgery_gap:,}" if surgery_gap > 0 else "足夠",
                         delta_color="inverse" if surgery_gap > 0 else "off")
            with col2:
                st.metric("癌症治療賠償", f"HK$ {data['cancer_amount']:,}",
                         delta=f"差額 HK$ {cancer_gap:,}" if cancer_gap > 0 else "足夠",
                         delta_color="inverse" if cancer_gap > 0 else "off")
        else:
            st.warning("未有醫療保險，以上全數為缺口")
    
    with tab2:
        st.metric("市場參考 (癌症平均治療費)", f"HK$ {market_critical:,}")
        if data["has_critical"] == "有":
            st.metric("你現有危疾賠償", f"HK$ {data['critical_amount']:,}",
                     delta=f"差額 HK$ {critical_gap:,}" if critical_gap > 0 else "足夠",
                     delta_color="inverse" if critical_gap > 0 else "off")
        else:
            st.warning("未有危疾保險，缺口為 HK$ {:,}".format(market_critical))
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("意外醫療 (每年)", f"HK$ {market_accident_medical:,}")
            if data["has_accident"] == "有":
                st.metric("你現有意外醫療", f"HK$ {data['accident_medical']:,}",
                         delta=f"差額 HK$ {accident_medical_gap:,}" if accident_medical_gap > 0 else "足夠",
                         delta_color="inverse" if accident_medical_gap > 0 else "off")
            else:
                st.warning("未有意外醫療保障")
        with col2:
            st.metric("意外身故/傷殘", f"HK$ {market_accident_death:,}")
            if data["has_accident"] == "有":
                st.metric("你現有意外身故賠償", f"HK$ {data['accident_death']:,}",
                         delta=f"差額 HK$ {accident_death_gap:,}" if accident_death_gap > 0 else "足夠",
                         delta_color="inverse" if accident_death_gap > 0 else "off")
            else:
                st.warning("未有意外身故保障")
    
    # 總結缺口
    st.divider()
    st.subheader("🔍 主要缺口")
    gaps = []
    if data["has_medical"] == "冇":
        gaps.append("完全沒有醫療保險，住院、手術、癌症治療全無保障")
    else:
        if inpatient_gap > 0:
            gaps.append(f"醫療 - 住院保障不足，每晚差額 HK$ {inpatient_gap:,}")
        if surgery_gap > 0:
            gaps.append(f"醫療 - 手術保障不足，每次差額 HK$ {surgery_gap:,}")
        if cancer_gap > 0:
            gaps.append(f"醫療 - 癌症治療保障不足，每年差額 HK$ {cancer_gap:,}")
    if data["has_critical"] == "冇":
        gaps.append("完全沒有危疾保險，確診重大疾病時缺乏一筆過資金")
    elif critical_gap > 0:
        gaps.append(f"危疾 - 保障不足，差額 HK$ {critical_gap:,}")
    if data["has_accident"] == "冇":
        gaps.append("完全沒有意外保險")
    else:
        if accident_medical_gap > 0:
            gaps.append(f"意外 - 醫療保障不足，每年差額 HK$ {accident_medical_gap:,}")
        if accident_death_gap > 0:
            gaps.append(f"意外 - 身故/傷殘賠償不足，差額 HK$ {accident_death_gap:,}")
    
    if gaps:
        for gap in gaps:
            st.error(f"⚠️ {gap}")
    else:
        st.success("✅ 各項保障均達到市場參考水平，無明顯缺口")
    
    # 建議行動
    st.subheader("💡 建議行動")
    recommendations = []
    if data["has_medical"] == "冇":
        recommendations.append("立即考慮自願醫保靈活計劃，涵蓋住院、手術及癌症治療")
    else:
        if inpatient_gap > 0 or surgery_gap > 0 or cancer_gap > 0:
            recommendations.append("升級醫療保險，提高住院、手術及癌症治療賠償額")
    if data["has_critical"] == "冇":
        recommendations.append("添置危疾保險，建議保額 HK$ 1,000,000 或以上")
    elif critical_gap > 0:
        recommendations.append("增加危疾保額至 HK$ 1,000,000 以上")
    if data["has_accident"] == "冇":
        recommendations.append("添置意外保險，保障意外醫療及身故")
    else:
        if accident_medical_gap > 0 or accident_death_gap > 0:
            recommendations.append("加強意外保險，提高醫療及身故賠償額")
    
    if recommendations:
        for rec in recommendations:
            st.info(f"📌 {rec}")
    else:
        st.success("保持現有保障，每年檢視一次即可")
    
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
    
    # 重新計算一次（確保數據最新）
    market_inpatient = 1200
    market_surgery = 40000
    market_cancer_yearly = 720000
    market_critical = 800000
    market_accident_medical = 50000
    market_accident_death = 1000000
    
    inpatient_gap = max(0, market_inpatient - data["inpatient_amount"]) if data["has_medical"] == "有" else market_inpatient
    surgery_gap = max(0, market_surgery - data["surgery_amount"]) if data["has_medical"] == "有" else market_surgery
    cancer_gap = max(0, market_cancer_yearly - data["cancer_amount"]) if data["has_medical"] == "有" else market_cancer_yearly
    critical_gap = max(0, market_critical - data["critical_amount"]) if data["has_critical"] == "有" else market_critical
    accident_medical_gap = max(0, market_accident_medical - data["accident_medical"]) if data["has_accident"] == "有" else market_accident_medical
    accident_death_gap = max(0, market_accident_death - data["accident_death"]) if data["has_accident"] == "有" else market_accident_death
    
    st.markdown("### 保險快速檢視報告")
    st.markdown(f"**客人姓名**：{data['name']}")
    st.markdown(f"**檢視日期**：{data['date']}")
    st.markdown("---")
    
    # 醫療部分
    st.markdown("#### 一、醫療保障對比")
    if data["has_medical"] == "冇":
        st.warning("現狀：無任何醫療保險")
        st.markdown(f"- 住院缺口：HK$ {market_inpatient:,}/晚")
        st.markdown(f"- 手術缺口：HK$ {market_surgery:,}/次")
        st.markdown(f"- 癌症治療缺口：HK$ {market_cancer_yearly:,}/年")
    else:
        st.markdown(f"- **住院**：現有 HK$ {data['inpatient_amount']:,}/晚，市場參考 HK$ {market_inpatient:,}，**差額 HK$ {inpatient_gap:,}/晚**")
        st.markdown(f"- **手術**：現有 HK$ {data['surgery_amount']:,}/次，市場參考 HK$ {market_surgery:,}，**差額 HK$ {surgery_gap:,}/次**")
        st.markdown(f"- **癌症治療**：現有 HK$ {data['cancer_amount']:,}/年，市場參考 HK$ {market_cancer_yearly:,}，**差額 HK$ {cancer_gap:,}/年**")
    
    # 危疾部分
    st.markdown("#### 二、危疾保障對比")
    if data["has_critical"] == "冇":
        st.warning("現狀：無危疾保險")
        st.markdown(f"- 一筆過賠償缺口：HK$ {market_critical:,}")
    else:
        st.markdown(f"- 現有賠償：HK$ {data['critical_amount']:,}，市場參考治療費 HK$ {market_critical:,}，**差額 HK$ {critical_gap:,}**")
    
    # 意外部分
    st.markdown("#### 三、意外保障對比")
    if data["has_accident"] == "冇":
        st.warning("現狀：無意外保險")
        st.markdown(f"- 意外醫療缺口：HK$ {market_accident_medical:,}/年")
        st.markdown(f"- 意外身故/傷殘缺口：HK$ {market_accident_death:,}")
    else:
        st.markdown(f"- **意外醫療**：現有 HK$ {data['accident_medical']:,}/年，市場參考 HK$ {market_accident_medical:,}，**差額 HK$ {accident_medical_gap:,}/年**")
        st.markdown(f"- **意外身故/傷殘**：現有 HK$ {data['accident_death']:,}，市場參考 HK$ {market_accident_death:,}，**差額 HK$ {accident_death_gap:,}**")
    
    st.markdown("---")
    st.markdown("*無壓力・唔使買・純粹幫你睇*")
    st.caption("顧問：Sonia")
    
    # 下載報告（純文字版，包含差額）
    report_text = f"""
保險快速檢視報告
客人：{data['name']}
日期：{data['date']}

一、醫療保障
{'- 無醫療保險' if data['has_medical'] == '冇' else f'''
- 住院賠償：HK$ {data['inpatient_amount']:,}/晚 (市場參考 HK$ {market_inpatient:,}) 差額 HK$ {inpatient_gap:,}
- 手術賠償：HK$ {data['surgery_amount']:,}/次 (市場參考 HK$ {market_surgery:,}) 差額 HK$ {surgery_gap:,}
- 癌症治療賠償：HK$ {data['cancer_amount']:,}/年 (市場參考 HK$ {market_cancer_yearly:,}) 差額 HK$ {cancer_gap:,}
'''}

二、危疾保障
{'- 無危疾保險' if data['has_critical'] == '冇' else f'- 危疾賠償：HK$ {data['critical_amount']:,} (市場參考治療費 HK$ {market_critical:,}) 差額 HK$ {critical_gap:,}'}

三、意外保障
{'- 無意外保險' if data['has_accident'] == '冇' else f'''
- 意外醫療賠償：HK$ {data['accident_medical']:,}/年 (市場參考 HK$ {market_accident_medical:,}) 差額 HK$ {accident_medical_gap:,}
- 意外身故賠償：HK$ {data['accident_death']:,} (市場參考 HK$ {market_accident_death:,}) 差額 HK$ {accident_death_gap:,}
'''}

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
    
    if st.button("← 開始新檢視"):
        st.session_state.step = 1
        st.session_state.client_data = {}
        st.rerun()
