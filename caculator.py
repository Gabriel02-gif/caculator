import streamlit as st
import re
from supabase import create_client, Client

st.set_page_config(page_title="Caculator", layout="wide")
st.title("124电费计算器")

#小计算器
power = st.number_input("电器功率（W）：")
a = st.number_input("使用时长（分钟）：")
hours = a / 60
price = 0.63

if st.button("计算"):
    kwh = power / 1000 * hours
    cost = kwh * price
    st.write(f"耗电量：{kwh:.3f}度")
    st.write(f"电费：{cost:.3f}元")

#配置数据库链接
SUPABASE_URL="https://dgljivltoxemquqpwznp.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnbGppdmx0b3hlbXF1cXB3em5wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3NDcyOTksImV4cCI6MjExMDMyMzI5OX0.Lpsr-bNY7FR3KkBc3dzuUfvpTy-rm61RBsGocvL2-GA"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"数据库连接失败，检查 URL 和 KEY 是否正确。错误信息：{e}")
    st.stop

#侧边栏计算表达式
def safe_eval(expr):
    if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expr):
        try:
            return eval(expr)
        except:
            return None
    return None

#侧边栏交互：输入与提交
st.sidebar.header("身份与输入")
user_identity = st.sidebar.selectbox("你是：", ["奶奶", "美美","小鬼", "基米", "娟娟"])
expr_input = st.sidebar.text_input("输入算式 (如 0.5+0.4 ):", value="")

if st.sidebar.button("提交计算"):
    if expr_input:
        result = safe_eval(expr_input)
        if result is not None:
            try:
                response = supabase.table("records").insert({
                    "name": user_identity,
                    "text": expr_input
                }).execute()
                st.sidebar.success(f"已保存{expr_input} = {result}")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"保存失败：{e}")
        else:
            st.sidebar.error("算式错误，只可包含数字，小数和加减乘除")

#从云端拉取数据并展示
st.subheader("记录栏")
st.write("点击下方人名，展开查看个人统计记录。")

try:
    response = supabase.table("records").select("*").execute()
    all_records = response.data
except Exception as e:
    st.error(f"读取数据失败：{e}")
    all_records = []

for user in ["奶奶", "美美","小鬼", "基米", "娟娟"]:
    user_msgs = [msg for msg in all_records if msg["name"] == user]

    if user_msgs:
        user_total = 0.0
        for m in user_msgs:
            val = safe_eval(m["text"])
            if val is not None:
                user_total += val
        with st.expander(f"{user}的记录（共{len(user_msgs)}）条——总计：{user_total:.2f}"):
            for m in user_msgs:
                val = safe_eval(m["text"])
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"- {m['text']} = **{val}**")
                with col2:
                    if st.button("删除", key=f"del_{m['id']}"):
                        try:
                            supabase.table("records").delete().eq("id", m["id"]).execute()
                            st.toast("已删除")
                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败：{e}")
    else:
        with st.expander(f"{user}的记录(暂无）"):
            st.write("还没有记录。")