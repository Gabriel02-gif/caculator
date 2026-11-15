import streamlit as st

st.title("124电费计算器")

power = st.number_input("电器功率（W）：")
a = st.number_input("使用时长（分钟）：")
hours = a / 60
price = 0.63

if st.button("计算"):
    kwh = power / 1000 * hours
    cost = kwh * price
    st.write(f"耗电量：{kwh:.3f}度")
    st.write(f"电费：{cost:.3f}元")
