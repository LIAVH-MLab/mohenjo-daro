# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 15:05:15 2020

@author: csucuogl for LIAVH
This code generates the pink artefact/ water/ floor features scatter plot.
"""

#%% ----------- IMPORT ------------------------
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import matplotlib.pyplot as plt
import plotly.graph_objects as go

#%% ------------- DATA -------------

da = pd.read_csv( "https://raw.githubusercontent.com/PrattSAVI/LIAVH/master/data/Artifacts.csv" , engine = 'python')
#ds = pd.read_csv( "https://raw.githubusercontent.com/PrattSAVI/LIAVH/master/data/Doorsils_and_Floor_Features_Level_Refs_Mackay.csv" , engine = 'python')

da.head()

# %%

plates = ['068-024-X','068-021-X','072-008-X','078-005-X']

df = da[ da['obj_plate_obj_ID'].isin(plates)]

df = df.dropna(axis = 1 , how='all')
df
# %%

df.to_csv( r"C:\Users\csucuogl\Desktop\test\sample.csv")
# %%
