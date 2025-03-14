# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
from shapely import wkt


    
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
st.set_page_config(page_title="Snow Lover", 
                   layout="wide", page_icon="⛄",
                   initial_sidebar_state="expanded")


###メインページ
st.write("""# ⛄ White Lover""")    


# データの準備
tokyo_data = {
    'date': ['2025-03-11', '2025-03-12', '2025-03-13'],
    'snow_depth': [0, 0, 0]  # 仮のデータ
}

osaka_data = {
    'date': ['2025-03-11', '2025-03-12', '2025-03-13'],
    'snow_depth': [0, 0, 0]  # 仮のデータ
}

tokyo_df = pd.DataFrame(tokyo_data)
osaka_df = pd.DataFrame(osaka_data)

st.dataframe(tokyo_df)
st.dataframe(osaka_df)

# 地図の設定
view_state = pdk.ViewState(
    latitude=35.6895,
    longitude=139.6917,
    zoom=5,
    pitch=0
)

# 東京と大阪の位置
locations = pd.DataFrame({
    'name': ['Tokyo', 'Osaka'],
    'lat': [35.6895, 34.6937],
    'lon': [139.6917, 135.5023]
})

# Pydeckのレイヤー
layer = pdk.Layer(
    'ScatterplotLayer',
    data=locations,
    get_position='[lon, lat]',
    get_radius=50000,
    get_color='[200, 30, 0, 160]',
    pickable=True
)

# Pydeckの地図
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"}
)

# Streamlitのレイアウト
st.title('Tokyo and Osaka Snow Depth Visualization')
selected_city = st.empty()
st.pydeck_chart(r)
