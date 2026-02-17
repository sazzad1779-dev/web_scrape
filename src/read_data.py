import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV URL Viewer", layout="wide")

st.title("🔎 CSV URL Data Viewer")

# Cache load (important for large CSVs)
@st.cache_data
def load_data():
    df = pd.read_csv("output_v3/pep_pedia_master.csv")
    df = df.convert_dtypes().astype("object")
    df["URL"] = df["URL"].str.strip().str.lower()   # normalize
    return df

df = load_data()

user_url = st.text_input("Enter URL to search")

if user_url:
    user_url = user_url.strip().lower()
    print("user_url: ",user_url)
    result = df[df["URL"] == user_url]
    
    if result.empty:
        st.error("URL not found in dataset ❌")
    else:
        # Remove null columns
        result = result.dropna(axis=1, how='all')

        st.success("Data found ✅")
        st.dataframe(
            result,
            use_container_width=True,
            height=400


            # hide_index=True
        )
##uv run streamlit run src/read_data.py  --server.headless true
##uv run streamlit run src/read_data.py  --server.headless true --server.port 8501 --server.address 0.0.0.0
##ngrok http 8501