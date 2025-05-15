# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from shapely import wkt
import plotly.graph_objects as go
import os, glob



###ファイルパス設定（直下を参照する）
path= ''

###CSV読込み
##座標データ
kilo = pd.read_csv(path+"kirotei_lonlat.csv", encoding="shift_jis")
##駅データ
sta = pd.read_csv(path+"station_lonlat_jre.csv", encoding="shift_jis")
##路線データ
line = pd.read_csv(path+"tsushosen_line.csv", encoding="shift_jis")
##サンプルデータ
data_raw = pd.read_csv(path+"sample_snow.csv", encoding="shift_jis")

###データ下処理
##駅データ
sta['label'] = sta['N02_003'].astype(str) +str(" ")+ sta['N02_005'].astype(str)

##路線データ
line['label'] = line['通称線']
line['geometry'] = line['WKT'].apply(wkt.loads)
line_gdf = gpd.GeoDataFrame(line, geometry='geometry')

###Streamlitの初期設定
st.set_page_config(page_title="white Lover", 
                   layout="wide", page_icon="⛄",
                   initial_sidebar_state="expanded")


###メインページ
st.write("""# ⛄🧊 White Lover""")    



from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# 認証情報を読み込む
creds = service_account.Credentials.from_service_account_file(
          'service_account.json',  # JSON形式のキーファイルへのパス
          scopes=['https://www.googleapis.com/auth/drive']
        )
# Google Drive APIクライアントを作成
drive_service = build('drive', 'v3', credentials=creds)
# アップロードするファイルの情報
file_name = 'example.csv'
file_metadata = {
  'name': file_name,
  'parents': ['1B9zvcUnbuKrpFRLbXt2bOVgjKnIL1Tf7'],  # ファイルID(ドライブURIの’folders/’に続く値)
}
# ファイルをアップロード
media = MediaFileUpload(file_name, mimetype='application/csv')
file = drive_service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id',
          supportsAllDrives=True  # ポイント！
        ).execute()
print(f'File ID: {file.get("id")}')


st.write(os.getcwd())
st.write(glob.glob(os.getcwd()+"/*"))

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

