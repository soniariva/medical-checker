import streamlit as st
import pandas as pd
from datetime import datetime

# 页面设定
st.set_page_config(page_title="15分钟医疗保险检视", page_icon="🩺", layout="wide")

# 标题
st.title("🩺 15分钟医疗保险检视")
st.caption("输入你嘅数字，系统会自动计算保障缺口")

# 侧边栏：对比价目表
with st.sidebar:
    st.header("💰 医疗费用 vs 保单赔偿 对比价目表")
    st.caption("以下係常见医疗项目嘅参考费用")
    
    # 对比表格
    compare_data = {
        "项目": ["专科门诊", "住院 (大房/晚)", "住院 (半私家/晚)", 
                 "大型手术", "复杂手术", "标靶药 (每月)", "MRI 扫描"],
        "实际费用 (HK$)": [800, 1200, 2500, 40000, 300000, 60000, 8000],
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
    st.caption(f"顾问：Sonia")
    
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

