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
    
    # 選擇保障類型
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
        
    else:  # 意外
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

# ==================== 第二步：問題（醫療 + 危疾 + 意外） ====================
elif st.session_state.step == 2:
    st.header("📝 第二步：保障現況")
    
    st.info("以下問題會幫我了解你嘅需要同現時保障")
    
    # ----- 醫療 -----
    st.subheader("🏥 醫療保障")
    col1, col2 = st.columns(2)
    with col1:
        risk = st.selectbox(
            "最擔心嘅健康風險",
            ["癌症", "心臟病", "中風", "意外受傷", "其他"]
        )
    with col2:
        budget = st.number_input("住院預算 (每晚)", min_value=0, step=500, value=1000)
    
    has_medical = st.radio("有冇買醫療保險？", ["有", "冇"], horizontal=True)
    
    company = ""
    inpatient_amount = 0
    cancer_cover = "冇"
    if has_medical == "有":
        company = st.text_input("保險公司")
        inpatient_amount = st.number_input("住院一晚賠幾多？", min_value=0, step=500, value=0)
        cancer_cover = st.radio("有冇包癌症治療？", ["有", "冇", "唔知"], horizontal=True)
    
    st.divider()
    
    # ----- 危疾 -----
    st.subheader("❤️ 危疾保障")
    has_critical = st.radio("有冇買危疾保險？", ["有", "冇"], horizontal=True)
    
    critical_amount = 0
    if has_critical == "有":
        critical_amount = st.number_input("危疾賠償額 (一筆過)", min_value=0, step=100000, value=0, format="%d")
    
    st.divider()
    
    # ----- 意外 -----
    st.subheader("⚠️ 意外保障")
    has_accident = st.radio("有冇買意外保險？", ["有", "冇"], horizontal=True)
    
    accident_medical = 0
    accident_death = 0
    if has_accident == "有":
        col1, col2 = st.columns(2)
        with col1:
            accident_medical = st.number_input("意外醫療賠償 (每年)", min_value=0, step=10000, value=0)
        with col2:
            accident_death = st.number_input("意外身故/傷殘賠償", min_value=0, step=100000, value=0)
    
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
            st.session_state.client_data["cancer_cover"] = cancer_cover
            st.session_state.client_data["has_critical"] = has_critical
            st.session_state.client_data["critical_amount"] = critical_amount
            st.session_state.client_data["has_accident"] = has_accident
            st.session_state.client_data["accident_medical"] = accident_medical
            st.session_state.client_data["accident_death"] = accident_death
            st.session_state.step = 3
            st.rerun()

# ==================== 第三步：計算結果 ====================
elif st.session_state.step == 3:
    st.header("📊 第三步：保障缺口分析")
    
    data = st.session_state.client_data
    
    # 計算標準
    standard_inpatient = 1000
    standard_surgery = 100000
    standard_critical = 1000000
    standard_accident_medical = 50000
    standard_accident_death = 1000000
    
    # 醫療缺口
    inpatient_gap = max(0, standard_inpatient - data["inpatient_amount"]) if data["has_medical"] == "有" else standard_inpatient
    
    # 危疾缺口
    critical_gap = max(0, standard_critical - data["critical_amount"]) if data["has_critical"] == "有" else standard_critical
    
    # 意外缺口
    accident_medical_gap = max(0, standard_accident_medical - data["accident_medical"]) if data["has_accident"] == "有" else standard_accident_medical
    accident_death_gap = max(0, standard_accident_death - data["accident_death"]) if data["has_accident"] == "有" else standard_accident_death
    
    # 顯示三個部分
    tab1, tab2, tab3 = st.tabs(["🏥 醫療", "❤️ 危疾", "⚠️ 意外"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("住院標準", f"${standard_inpatient:,}/晚")
        with col2:
            if data["has_medical"] == "有":
                st.metric("你現時住院", f"${data['inpatient_amount']:,}/晚", 
                         delta=f"差額 ${inpatient_gap:,}" if inpatient_gap > 0 else None,
                         delta_color="inverse" if inpatient_gap > 0 else "off")
            else:
                st.warning("未有醫療保險")
        
        if data["has_medical"] == "有":
            st.metric("癌症保障", data["cancer_cover"])
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("危疾標準", f"${standard_critical:,}")
        with col2:
            if data["has_critical"] == "有":
                st.metric("你現時危疾", f"${data['critical_amount']:,}",
                         delta=f"差額 ${critical_gap:,}" if critical_gap > 0 else None,
                         delta_color="inverse" if critical_gap > 0 else "off")
            else:
                st.warning("未有危疾保險")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("意外醫療標準", f"${standard_accident_medical:,}/年")
            st.metric("意外身故標準", f"${standard_accident_death:,}")
        with col2:
            if data["has_accident"] == "有":
                st.metric("意外醫療現時", f"${data['accident_medical']:,}/年",
                         delta=f"差額 ${accident_medical_gap:,}" if accident_medical_gap > 0 else None,
                         delta_color="inverse" if accident_medical_gap > 0 else "off")
                st.metric("意外身故現時", f"${data['accident_death']:,}",
                         delta=f"差額 ${accident_death_gap:,}" if accident_death_gap > 0 else None,
                         delta_color="inverse" if accident_death_gap > 0 else "off")
            else:
                st.warning("未有意外保險")
    
    # 總結缺口
    st.divider()
    st.subheader("🔍 主要缺口")
    
    gaps = []
    if data["has_medical"] == "冇":
        gaps.append("完全沒有醫療保險")
    else:
        if inpatient_gap > 0:
            gaps.append(f"醫療 - 住院保障不足，每晚差額 ${inpatient_gap:,}")
        if data["cancer_cover"] != "有":
            gaps.append("醫療 - 缺乏癌症保障")
    
    if data["has_critical"] == "冇":
        gaps.append("完全沒有危疾保險")
    elif critical_gap > 0:
        gaps.append(f"危疾 - 保障不足，差額 ${critical_gap:,}")
    
    if data["has_accident"] == "冇":
        gaps.append("完全沒有意外保險")
    else:
        if accident_medical_gap > 0:
            gaps.append(f"意外 - 醫療保障不足，差額 ${accident_medical_gap:,}/年")
        if accident_death_gap > 0:
            gaps.append(f"意外 - 身故賠償不足，差額 ${accident_death_gap:,}")
    
    if gaps:
        for gap in gaps:
            st.error(f"⚠️ {gap}")
    else:
        st.success("✅ 無明顯缺口，保障足夠")
    
    # 建議行動
    st.subheader("💡 建議行動")
    recommendations = []
    if data["has_medical"] == "冇":
        recommendations.append("考慮自願醫保計劃，建立基本醫療保障")
    elif inpatient_gap > 0 or data["cancer_cover"] != "有":
        recommendations.append("升級醫療計劃，填補住院及癌症缺口")
    
    if data["has_critical"] == "冇":
        recommendations.append("考慮危疾保險，應對重大疾病風險")
    elif critical_gap > 0:
        recommendations.append("增加危疾保額至 $1,000,000 或以上")
    
    if data["has_accident"] == "冇":
        recommendations.append("考慮意外保險，保障意外醫療及身故")
    elif accident_medical_gap > 0 or accident_death_gap > 0:
        recommendations.append("加強意外保障，提高醫療及身故賠償")
    
    if recommendations:
        for rec in recommendations:
            st.info(f"📌 {rec}")
    else:
        st.success("保持現有保障，每年檢視一次")
    
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
    
    # 計算缺口
    inpatient_gap = max(0, 1000 - data["inpatient_amount"]) if data["has_medical"] == "有" else 1000
    critical_gap = max(0, 1000000 - data["critical_amount"]) if data["has_critical"] == "有" else 1000000
    accident_medical_gap = max(0, 50000 - data["accident_medical"]) if data["has_accident"] == "有" else 50000
    accident_death_gap = max(0, 1000000 - data["accident_death"]) if data["has_accident"] == "有" else 1000000
    
    # 顯示報告內容
    st.markdown("### 保險快速檢視報告")
    st.markdown(f"**客人姓名**：{data['name']}")
    st.markdown(f"**檢視日期**：{data['date']}")
    st.markdown("---")
    
    st.markdown("#### 一、醫療")
    if data['has_medical'] == '冇':
        st.warning("無醫療保險")
    else:
        st.markdown(f"- 住院賠償：${data['inpatient_amount']:,}/晚 (標準 $1,000)")
        st.markdown(f"- 癌症保障：{data['cancer_cover']}")
    
    st.markdown("#### 二、危疾")
    if data['has_critical'] == '冇':
        st.warning("無危疾保險")
    else:
        st.markdown(f"- 危疾賠償：${data['critical_amount']:,} (標準 $1,000,000)")
    
    st.markdown("#### 三、意外")
    if data['has_accident'] == '冇':
        st.warning("無意外保險")
    else:
        st.markdown(f"- 意外醫療：${data['accident_medical']:,}/年 (標準 $50,000)")
        st.markdown(f"- 意外身故：${data['accident_death']:,} (標準 $1,000,000)")
    
    st.markdown("---")
    st.markdown("*無壓力・唔使買・純粹幫你睇*")
    st.caption(f"顧問：Sonia")
    
    # 下載報告功能
    report_text = f"""
保險快速檢視報告

客人：{data['name']}
日期：{data['date']}

一、醫療
{'- 無醫療保險' if data['has_medical'] == '冇' else f'- 住院賠償：${data['inpatient_amount']:,}/晚\n- 癌症保障：{data['cancer_cover']}'}

二、危疾
{'- 無危疾保險' if data['has_critical'] == '冇' else f'- 危疾賠償：${data['critical_amount']:,}'}

三、意外
{'- 無意外保險' if data['has_accident'] == '冇' else f'- 意外醫療：${data['accident_medical']:,}/年\n- 意外身故：${data['accident_death']:,}'}

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
        st.rerun()0, 300000, 60000, 8000],
        "基本保单赔偿 (HK$)": [0, 750, 1200, 25000, 50000, 0, 2000],
    }
    df_compare = pd.DataFrame(compare_data)
    df_compare["你要自付 (HK$)"] = df_compare["实际费用 (HK$)"] - df_compare["基本保单赔偿 (HK$)"]
    
    st.dataframe(df_compare, use_container_width=True)
    
    st.info("💡 以上数字只供参考，实际费用因医院及医生而异")

# 主页面
# 初始化 session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "client_data" not in st.session_state:
    st.session_state.client_data = {}

# 进度显示
st.progress(st.session_state.step / 4)

# ==================== 第一步：基本资料 ====================
if st.session_state.step == 1:
    st.header("📋 第一步：基本资料")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("客人姓名")
    with col2:
        date = st.date_input("检视日期", datetime.today())
    
    phone = st.text_input("联络电话")
    
    if st.button("下一步 →"):
        if name:
            st.session_state.client_data["name"] = name
            st.session_state.client_data["date"] = str(date)
            st.session_state.client_data["phone"] = phone
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("请输入客人姓名")

# ==================== 第二步：5条问题 ====================
elif st.session_state.step == 2:
    st.header("📝 第二步：5条问题")
    
    st.info("以下问题会帮了解你嘅需要同现时保障")
    
    # 问题1
    risk = st.selectbox(
        "1. 你而家最担心嘅健康风险系咩？",
        ["癌症", "心脏病", "中风", "意外受伤", "其他"]
    )
    
    # 问题2
    budget = st.number_input("2. 如果突然要住院，你 budget 系几多一晚？", min_value=0, step=500, value=1000)
    
    # 问题3
    has_insurance = st.radio("3. 你而家有冇买医疗保险？", ["有", "冇"], horizontal=True)
    
    company = ""
    if has_insurance == "有":
        company = st.text_input("边间保险公司？")
    
    # 问题4
    inpatient_amount = 0
    if has_insurance == "有":
        inpatient_amount = st.number_input("4. 你份保单住院一晚赔几多？", min_value=0, step=500, value=0)
    
    # 问题5
    cancer_cover = "冇"
    if has_insurance == "有":
        cancer_cover = st.radio("5. 你份保单有冇包癌症治疗？", ["有", "冇", "唔知"], horizontal=True)
    
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

# ==================== 第三步：计算结果 ====================
elif st.session_state.step == 3:
    st.header("📊 第三步：保障缺口分析")
    
    data = st.session_state.client_data
    
    # 计算标准（$1,000/晚为基本标准）
    standard_inpatient = 1000
    standard_surgery = 100000
    
    # 计算缺口
    inpatient_gap = max(0, standard_inpatient - data["inpatient_amount"]) if data["has_insurance"] == "有" else standard_inpatient
    
    # 显示结果表格
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("住院标准", f"${standard_inpatient:,}/晚")
        st.metric("手术标准", f"${standard_surgery:,}")
    with col2:
        if data["has_insurance"] == "有":
            st.metric("你现时住院", f"${data['inpatient_amount']:,}/晚", 
                     delta=f"差额 ${inpatient_gap:,}" if inpatient_gap > 0 else None,
                     delta_color="inverse" if inpatient_gap > 0 else "off")
            st.metric("癌症保障", data["cancer_cover"])
        else:
            st.warning("你现时未有医疗保险")
    
    # 总结缺口
    st.divider()
    st.subheader("🔍 主要缺口")
    
    gaps = []
    if data["has_insurance"] == "冇":
        gaps.append("完全没有医疗保险")
    else:
        if inpatient_gap > 0:
            gaps.append(f"住院保障不足，每晚差额 ${inpatient_gap:,}")
        if data["cancer_cover"] != "有":
            gaps.append("缺乏癌症保障（标靶药、化疗）")
    
    if gaps:
        for gap in gaps:
            st.error(f"⚠️ {gap}")
    else:
        st.success("✅ 无明显缺口，保障足够")
    
    # 建议行动
    st.subheader("💡 建议行动")
    if data["has_insurance"] == "冇":
        st.info("建议：尽快建立基本医疗保障，可考虑自愿医保计划")
    else:
        if inpatient_gap > 0 or data["cancer_cover"] != "有":
            st.info("建议：考虑升级现有计划，填补以上缺口")
        else:
            st.success("建议：定期检视，保持现有保障")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回修改"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("生成报告 →"):
            st.session_state.step = 4
            st.rerun()

# ==================== 第四步：生成报告 ====================
elif st.session_state.step == 4:
    st.header("📄 第四步：报告总结")
    
    data = st.session_state.client_data
    
    # 显示报告内容
    st.markdown("### 医疗保险快速检视报告")
    st.markdown(f"**客人姓名**：{data['name']}")
    st.markdown(f"**检视日期**：{data['date']}")
    st.markdown("---")
    
    st.markdown("#### 一、你嘅保障现况")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"- 担心风险：{data['risk']}")
        st.markdown(f"- 住院预算：${data['budget']:,}/晚")
    with col2:
        st.markdown(f"- 有冇保险：{data['has_insurance']}")
        if data['has_insurance'] == '有':
            st.markdown(f"- 保险公司：{data['company']}")
    
    st.markdown("#### 二、保障缺口")
    if data['has_insurance'] == '冇':
        st.warning("⚠️ 完全没有医疗保险")
    else:
        inpatient_gap = max(0, 1000 - data['inpatient_amount'])
        if inpatient_gap > 0:
            st.warning(f"⚠️ 住院保障不足，每晚差额 ${inpatient_gap:,}")
        if data['cancer_cover'] != '有':
            st.warning("⚠️ 缺乏癌症保障")
    
    st.markdown("#### 三、建议行动")
    if data['has_insurance'] == '冇':
        st.info("建议尽快建立基本医疗保障")
    else:
        if inpatient_gap > 0 or data['cancer_cover'] != '有':
            st.info("建议升级现有计划，填补保障缺口")
        else:
            st.success("保障足够，建议每年检视一次")
    
    st.markdown("---")
    st.markdown("*无压力・唔使买・纯粹帮你睇*")
    st.caption(f"顾问：淇錡")
    
    # 下载报告功能
    report_text = f"""
医疗保险快速检视报告

客人：{data['name']}
日期：{data['date']}

一、保障现况
- 担心风险：{data['risk']}
- 住院预算：${data['budget']:,}/晚
- 有冇保险：{data['has_insurance']}
{'- 保险公司：' + data['company'] if data['has_insurance'] == '有' else ''}

二、缺口分析
{'- 完全没有医疗保险' if data['has_insurance'] == '冇' else f'- 住院差额：${max(0, 1000 - data['inpatient_amount']):,}/晚'}

三、建议
{'建议尽快建立基本医疗保障' if data['has_insurance'] == '冇' else '建议检视及升级保障'}

--- 
无压力・唔使买・纯粹帮你睇
顾问：淇錡
    """
    
    st.download_button(
        label="📥 下载报告 (TXT)",
        data=report_text,
        file_name=f"医疗报告_{data['name']}.txt",
        mime="text/plain"
    )
    
    if st.button("← 开始新检视"):
        st.session_state.step = 1
        st.session_state.client_data = {}
        st.rerun()

