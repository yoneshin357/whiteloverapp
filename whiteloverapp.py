# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from shapely import wkt
import plotly.graph_objects as go

    
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
st.write("""# ⛄ White Lover""")    

# データ準備（東京と横浜の3日間の気温データ）
tokyo_temp = [15, 17, 16]
yokohama_temp = [14, 3, 10]
dates = ['2023-10-26', '2023-10-27', '2023-10-28']

# pydeckの初期設定
tokyo_lat, tokyo_lon = 35.6895, 139.6917
yokohama_lat, yokohama_lon = 35.4437, 139.6380

selection_dates = st.selectbox('日付を選んでください', dates)
selection_location = st.selectbox('観測値を選んでください', ['東京','横浜'])

view_state = pdk.ViewState(
    latitude=tokyo_lat,
    longitude=tokyo_lon,
    zoom=8,
    pitch=50,
    use_container_width=False,
    width="100%", 
    height=1200
)

layer = pdk.Layer(
    "ColumnLayer",
    [
        {"position": [tokyo_lon, tokyo_lat], "name": "東京", "elevation": tokyo_temp},
        {"position": [yokohama_lon, yokohama_lat], "name": "横浜", "elevation": yokohama_temp},
    ],
    get_position="position",
    get_elevation="elevation[0]*5000",
    get_color=[100, 100, 230,100],
    get_radius=10000,
    pickable=True,
    id="map",
    extruded=True,
    auto_highlight=True
)

        
deck = pdk.Deck(layers=[layer],initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9")


# Streamlitアプリ
event = st.pydeck_chart(deck, on_select="rerun", selection_mode="single-object")

place = None
try:
    place = event.selection["objects"]["map"][0]["name"]
except:
    st.write("ok")

if place:
    st.write(place)
    fig = None
    if place == "東京":
        fig = go.Figure(data=go.Scatter(x=dates, y=tokyo_temp))
        fig.update_layout(title="東京の気温推移")

    elif place == "横浜":
        fig = go.Figure(data=go.Scatter(x=dates, y=yokohama_temp))
        fig.update_layout(title="横浜の気温推移")
    if fig:
        st.plotly_chart(fig)
else:
    st.write("地図上のマーカーをクリックしてください。")


st.write(event.selection)
