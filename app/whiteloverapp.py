# -*- coding: utf-8 -*-


import streamlit as st
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from shapely import wkt
import plotly.graph_objects as go
import pandas as pd
import os
import glob
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload





###Streamlitの初期設定
st.set_page_config(page_title="white Lover", 
                   layout="wide", page_icon="⛄",
                   initial_sidebar_state="expanded")


###メインページ
st.write("""# ⛄🧊 White Lover""")    

###ファイルパス設定（直下を参照する）
path= ''

st.write(os.getcwd())
st.write(glob.glob(os.getcwd()+"/*"))
st.write(path+"kirotei_lonlat.csv")



st.write(st.secrets["private_gsheets_url"])

creds = service_account.Credentials.from_service_account_info(
  st.secrets["gcp_service_account"],
  scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# ファイルアップロード
uploaded_file = st.file_uploader("ファイルをアップロードしてください", type=["csv", "txt", "xlsx"])

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_data = uploaded_file.read()
    media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype="application/octet-stream")

    file_metadata = {"name": file_name,"parents": ["1B9zvcUnbuKrpFRLbXt2bOVgjKnIL1Tf7"]}
    uploaded = drive_service.files().create(
      body=file_metadata,
      media_body=media,
    ).execute()

    st.success(f"ファイルをアップロードしました！File ID: {uploaded.get('id')}")

folder_id = "1B9zvcUnbuKrpFRLbXt2bOVgjKnIL1Tf7"
# sample.csv を検索
query = f"'{folder_id}' in parents and name = 'location_obs.csv' and mimeType = 'text/csv'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
items = results.get("files", [])
st.write(items)
if items:
    file_id = items[0]["id"]
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    df = pd.read_csv(fh,encoding='cp932')
    st.write("📄 sample.csv の内容:")
    st.dataframe(df)
else:
    st.warning("sample.csv が見つかりませんでした。")




def save_hello_txt():
    file_path = os.getcwd()+"/out.txt"
    with open(file_path, 'w') as f:
        f.write('hello')
if st.button('保存'):
    save_hello_txt()



place = None
# データ準備（東京と横浜の3日間の気温データ）
tokyo_temp = [15, 17, 16]
yokohama_temp = [14, 3, 10]
dates = ['2023-10-26', '2023-10-27', '2023-10-28']

# pydeckの初期設定
tokyo_lat, tokyo_lon = 39.7186, 140.10232
yokohama_lat, yokohama_lon = 37.9161, 139.03643

selection_dates = st.selectbox('日付を選んでください', dates)


view_state = pdk.ViewState(
    latitude=tokyo_lat,
    longitude=tokyo_lon,
    zoom=5,
    pitch=80,
    use_container_width=False,
    width="100%", 
    height=1200
)

layer = pdk.Layer(
    "ColumnLayer",
    [
        {"position": [tokyo_lon, tokyo_lat], "name": "秋田", "elevation": tokyo_temp},
        {"position": [yokohama_lon, yokohama_lat], "name": "新潟", "elevation": yokohama_temp},
    ],
    get_position="position",
    get_elevation="elevation[0]*5000",
    get_color=[230, 230, 230,100],
    
    pickable=True,
    id="map",
    extruded=True,
    auto_highlight=True,
    radius=5000
)
col = st.columns(2)


def on_select_callback(deck):
    place = event.selection["objects"]["map"][0]["name"]
    #st.write(event)
    #st.write(event.selection["objects"]["map"][0]["name"])
deck = pdk.Deck(layers=[layer],initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9")




with col[0]:
    event = st.pydeck_chart(deck, on_select="rerun", selection_mode="single-object")
    st.write(event)
    #if event.selection["objects"]:
    #    place = event.selection["objects"]["map"][0]["name"]

with col[1]:
    selection_location = st.selectbox('観測値を選んでください', ['秋田','新潟'])
    if selection_location:
        place = selection_location


fig = None
if place == "秋田":
    fig = go.Figure(data=go.Scatter(x=dates, y=tokyo_temp))
    fig.update_layout(title="秋田の気温推移")

elif place == "新潟":
    fig = go.Figure(data=go.Scatter(x=dates, y=yokohama_temp))
    fig.update_layout(title="新潟の気温推移")
if fig:
    with col[1]:
        st.plotly_chart(fig)
else:
    with col[1]:
        st.write("地図上のマーカーをクリックしてください。")

