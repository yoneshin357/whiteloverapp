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
st.write('## 表示設定')


