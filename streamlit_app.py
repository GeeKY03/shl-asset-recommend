import streamlit as st
import requests

st.set_page_config(page_title="SHL Recommender", layout="centered")
st.title("🧠 SHL Assessment Recommender")

query = st.text_area("🔍 Enter job description or hiring query", placeholder="E.g. Looking for a short test for Java engineers with communication skills")

if st.button("Get Recommendations") and query:
    with st.spinner("Fetching recommendations..."):
        response = requests.post("http://localhost:8000/recommend", json={"query": query})

        if response.status_code == 200:
            data = response.json()
            st.subheader("📋 Top Recommendations")

            for item in data["recommendations"]:
                st.markdown(f"**[{item['name']}]({item['url']})**")
                st.markdown(f"- ⏱ Duration: {item['duration']} min")
                st.markdown(f"- 🧪 Type: {item['test_type']}")
                st.markdown(f"- 🌐 Remote Testing Support: {item['remote_testing_support']}")
                st.markdown("---")
        else:
            st.error("Failed to fetch recommendations. Try again later.")
