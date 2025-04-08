import streamlit as st
import requests

st.title("🔍 SHL Assessment Recommendation System")

query = st.text_input("Enter recruiter's requirement:")

if query:
    with st.spinner("Fetching recommendations..."):
        try:
            response = requests.post("http://localhost:8000/recommend", json={"query": query})
            response.raise_for_status()
            recommendations = response.json()

            if recommendations:
                st.subheader("✅ Top Recommended Assessments:")
                for i, item in enumerate(recommendations, start=1):
                    name = item.get("name", "N/A")
                    duration = item.get("duration", "N/A")
                    test_type = item.get("test_type", "N/A")
                    remote_support = item.get("remote_testing_support", "N/A")
                    url = item.get("url", "#")

                    st.markdown(
                        f"**{i}. [{name}]({url})**  \n"
                        f"- Duration: {duration} mins  \n"
                        f"- Type: {test_type}  \n"
                        f"- Remote Support: {remote_support}"
                    )
            else:
                st.warning("No recommendations found.")

        except Exception as e:
            st.error(f"❌ Failed to fetch recommendations: {e}")
