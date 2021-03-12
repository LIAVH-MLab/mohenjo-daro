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
ds = pd.read_csv( "https://raw.githubusercontent.com/PrattSAVI/LIAVH/master/data/Doorsils_and_Floor_Features_Level_Refs_Mackay.csv" , engine = 'python')

da = da[['obj_plate_obj_ID','obj_block','obj_house','obj_room','obj_level_ft','obj_time_cat','obj_category','addl_type','addl_description']]
ds = ds[['Feature','Block','House','Room','Level_ft','Period_cited_in_text','Level_context','Text','Materials_notes']]
da.columns = ['Plate','Block','House','Room','Level_ft','Time_Cat','Feature','Type','Text']

ds['House'] = ds['House'].dropna(axis = 0)
ds['Block'] = ds['Block'].dropna(axis = 0)

ds['House'] = [r.split(', ')[0] for i,r in ds['House'].astype(str).iteritems()]

ds['N1'] = 'Floor Features'
da['N1'] = 'Artefacts'

display( ds.head(5) )
display( da.head(5))

#%% ------------------ WATER FEATURES ----------------

dw = pd.read_csv( "https://raw.githubusercontent.com/PrattSAVI/LIAVH/master/data/Wells_and_Water_Features_Refs_Mackay.csv" , engine = 'python' )

dw = dw.dropna( axis = 0 , how = 'all')
dw = dw.drop( ['Size_notes','Page_num' ] , axis = 1 )

dw = dw[['Feature','Block','House','Room','Level_ft','Period_cited_in_text','Text','Plate_num']].copy()
dw.columns = ['Feature','Block','House','Room','Level_ft' , 'Time_Cat' , 'Text' ,'Plate']

#If Block/ House is not defined, Remove from list
dw = dw[~pd.isna(dw['Block']) ]
dw = dw[~pd.isna(dw['House']) ]
dw['Block'] = dw['Block'].astype(int).astype(str)
dw['House'] = dw['House'].astype(int).astype(str)
dw['House'] = dw['House'].str.zfill(2)

#If time is NA, assign average value
dw.loc[ (pd.isna(dw['Level_ft'])) & (dw['Time_Cat']=='Late  II and I') , 'Level_ft'] = -7
dw.loc[ (pd.isna(dw['Level_ft'])) & (dw['Time_Cat']=='Late III') , 'Level_ft'] = -9.9
dw.loc[ (pd.isna(dw['Level_ft'])) & (dw['Time_Cat']=='Intermediate I') , 'Level_ft'] = -13
dw.loc[ (pd.isna(dw['Level_ft'])) & (dw['Time_Cat']=='Intermediate II') , 'Level_ft'] = -15.9
dw.loc[ (pd.isna(dw['Level_ft'])) & (dw['Time_Cat']=='Intermediate III') , 'Level_ft'] = -20.4

dw['N1'] = 'Water Features'

dw.sample(5)
#%% ------------------ MERGE ---------------
df = da.append( ds )
df = df.append( dw )

df[ df['N1'] == 'Water Features' ].sample(5)

#%% ------------------- CLEAN AND FORMAT
df['Block'] = df['Block'].astype(str) 

df['House'] = df['House'].replace(np.nan,None)
df['House'] = df['House'].replace('nan',None)
df['House'] = df['House'].dropna(axis = 0)
df['House'] = df['House'].astype(int).astype(str).str.zfill(2)

#Filter Data to Selected Houses and Rooms
df = df[ df['Block'].isin([ '4','7','9','10' ]) ]
#df = df[ df['House'].isin( ['07', '04', '03', '05', '06'] ) ]

df = df[ df.Level_ft != '?' ]
df = df[ df.Level_ft != '[?]' ]

df.loc[ df['Level_ft'] == 'SURFACE' , 'Level_ft' ] = 0
df.loc[ df['Level_ft'] == 'Surface' , 'Level_ft' ] = 0

df['Level_ft'] = df['Level_ft'].astype(float)

domestic = ['Animals', 'Cooking Baking Utensils', 'Personal Ornament', 
            'Vessels','Games And Toys', 'Human Figure', 'Household Objects'
            'Pottery - Incised and Painted', 'Pottery - Plain and Banded','Pottery - Incised and Painted - Upper']
craft = [ 'Tools', 'Lithics' , 'Metal']
trade = ['Weights And Measures', 'Beads', 'Seal' ]

well = [ 'Well', 'Well Steening', 'Well Feature Detail', 'Well - Pit']
drain = ['Pottery - Jar','Pipe', 'Drain','Outfall', 'Channel', 'Pit', 'Cesspit','Niche','Aperture', 'Chute', 'Drain Below Stair']
platform = ['Pavement']

df['Class'] = None

#Floor Features
df.loc[df['Feature'].isin(domestic) , 'Class'] = 'Domestic'
df.loc[df['Feature'].isin(craft) , 'Class'] = 'Craft'
df.loc[df['Feature'].isin(trade) , 'Class'] = 'Trade'

#Water Class
df.loc[df['Feature'].isin(well) , 'Class'] = 'Well'
df.loc[df['Feature'].isin(drain) , 'Class'] = 'Drainage'
df.loc[df['Feature'].isin(platform) , 'Class'] = 'Water Platforms'

#Catch All Else
df.loc[ (df['N1']=='Artefacts') & (pd.isna(df['Class'])) , 'Class'] = 'Other'


def div_text( df , col ):  #Style Text by dividing at 6th word with <br>
    texts = []
    for i,r in df.iterrows():
        if r[col]:
            span = 6
            words = str(r[col]).split(" ")
            res = [" ".join(words[i:i+span]) for i in range(0, len(words), span)]
            res = "<br>".join( res )
            texts.append( res )
        else:
            texts.append( None )
    return texts

df['Text2'] = div_text( df , 'Text' )
df['Text2'] = df['Text2'].replace('nan' , 'Not Available' )

df.sample(5)

#%% PLOTLY

time_order = [ 'Late Ia','Late Ib','Late II','Late III',
 'Intermediate I','Intermediate II','Intermediate III',
 'Early Periods']

ff = go.Figure() #Start an empty Figure Object

'''
#-----DRAW ==> STRATA LINES
for t in time_order: #Draw the Strata Lines
    at = df[ df['Time_Cat'] == t ]
    mins = at[['Block','House','Level_ft']].groupby( by = ['Block','House'] ).min().reset_index()
    maxs = at[['Block','House','Level_ft']].groupby( by = ['Block','House'] ).max().reset_index()
    al = mins.join( maxs.set_index('Block','House') , on = ['Block','House'] , rsuffix = '_max')
     
    ff.add_trace(
        go.Scatter( #lines
                x=[al['Block'],al['House']], 
                y=al['Level_ft_max'],
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend = False
                )
            )
    ff.add_trace(
        go.Scatter( #White Fill
                x=[ al['Block'],al['House'] ],
                y=al['Level_ft'],
                fill='tonexty',
                mode='lines',
                fillcolor='rgba(255,255,255,0.2)',
                line=dict(width=0, color='white'),
                showlegend = False,
                )
            )
'''

#------DRAW ==> FLOOR FEATURE
cmap = plt.cm.get_cmap('Set2')
colors = [ 'rgb(' + str(int(cmap(i)[0]*255)) + ',' + str(int(cmap(i)[1]*255)) + ',' + str(int(cmap(i)[2]*255)) + ')' for i in np.linspace( 0 ,1 , len( df[df['N1']=='Floor Features']['Feature'].unique() ) ) ]
count = 0
for f in df[df['N1']=='Floor Features']['Feature'].unique(): # Draw Floor Features
    dff = df[ (df['N1']=='Floor Features') & (df['Feature'] == f) ]

    ff.add_trace( # Draw Floor Features
        go.Scatter(
            mode='markers',
            x= [ dff['Block'] , dff['House'] ],
            y = dff['Level_ft'],
            legendgroup =  f,
            text = '<b>' + dff['Feature'] + '</b><br>'+ dff['Text2'],
            hovertemplate = "%{text}<extra></extra>",
            marker_symbol = 'line-ew',
            marker_line_color = colors[count], 
            marker_line_width = 1.5, marker_size = 15,
            name = f
            )
        )
    count = count + 1

#------DRAW ==> WATER FEATURE
cmap = plt.cm.get_cmap('Set1')
colors = [ 'rgb(' + str(int(cmap(i)[0]*255)) + ',' + str(int(cmap(i)[1]*255)) + ',' + str(int(cmap(i)[2]*255)) + ')' for i in np.linspace( 0 ,1 , len( df[df['N1']=='Water Features']['Feature'].unique() ) ) ]

count = 0
for f in df[df['N1']=='Water Features']['Class'].unique(): # Draw Floor Features
    dff = df[ (df['N1']=='Water Features') & (df['Class'] == f ) ]

    ff.add_trace( # Draw Water Features
        go.Scatter(
            mode='markers',
            x= [ dff['Block'] , dff['House'] ] ,
            y=dff['Level_ft'],
            legendgroup =  f,
            text = '<b>' + dff['Feature'] + '</b><br>'+ dff['Text2'],
            hovertemplate = "%{text}<extra></extra>",
            marker_symbol = 'y-up',
            marker_line_color= colors[count], 
            marker_line_width=1.5, marker_size=5,
            name = f,
            )
        )
    count = count + 1

#SWARM PLOT
def box_figure( df ): # Prepare the Swarm Plot

    cmap = plt.cm.get_cmap('Set1')
    colors = [ 'rgb(' + str(int(cmap(i)[0]*255)) + ',' + str(int(cmap(i)[1]*255)) + ',' + str(int(cmap(i)[2]*255)) + ')' for i in np.linspace( 0 ,1 , len( df['Class'].unique() ) ) ]
    count = 0
    
    df = df[df['N1'] == 'Artefacts']
    data_group = []
    for item in sorted( df['Class'].unique() ):
        data_group.append(
            {
                        'boxpoints': 'all',
                        'fillcolor': 'rgba(255,255,255,0)',
                        'hoveron': 'points',
                        'text': '<b>' + df[df['Class'] == item]['Feature'] + '</b>' + '<br>Desc: ' + df[df['Class'] == item]['Text2'] + '<br>Link: <a target="_blank" href=' + '>' + df[df['Class'] == item]['Plate'] + '</a>' ,
                        'hovertemplate': "%{text}" ,
                        'legendgroup': item ,
                        'line': {'color': 'rgba(255,255,255,0)'},
                        'marker': { 
                                    'color': colors[ count ] ,
                                    'size': 5,
                                    'opacity':0.8
                                    },
                        'name': item,
                        'pointpos':0,
                        'type': 'box',
                        'x': [ df[df['Class'] == item]['Block'].tolist() , df[df['Class'] == item]['House'].tolist()],
                        'y': df[df['Class'] == item]['Level_ft'].tolist(),
                        'jitter':0.5
                        })
        count = count+1

    return {
        'data': data_group,
    }
for d in box_figure(df)['data']: #Draw Point Plot
    ff.add_trace( go.Box( d ) )

#ADD NAME ANNOTATIONS
gr = df.groupby(by='Time_Cat').mean().reset_index()

ff.add_trace( # Add the Names
    go.Scatter(
        x = ['03']*len( gr ) ,
        y = gr['Level_ft'],
        mode = "text",
        text = '                  ' + gr['Time_Cat'].astype(str).str.upper() ,
        textposition = "middle right",
        showlegend = False,
        textfont = dict(
            family = 'Tisa Sans Pro',
            size = 8,
            color = 'grey'
        )
    ))

#LAYOUT
ff.update_layout( #Style Layout
    width = 900 , height = 800 ,
    hoverlabel=dict(
        bgcolor="white", 
        font_size=11, 
        font_family="Corbel"
    ),
    showlegend=True,
    dragmode = 'zoom',
    hovermode = 'closest',
    hoverdistance = 60,
    plot_bgcolor = '#FDD2CD',
    paper_bgcolor = '#FDD2CD',
    title = 'Block 4,7,9,10,1 Artefact and Floor / Water Features',
    margin=dict(l=50,r=50,b=80,t=100, pad=25 ),
    xaxis = dict(
        gridcolor = "rgb(255, 255, 255,0.5)",
        showgrid = True),
    yaxis = dict(
        gridcolor = "rgb(255, 255, 255,0.5)",
        gridwidth = 0.1)
    )

ff.show()

#%%
# Write figure to HTML, for offline use.  
ff.write_html(r'C:\Users\csucuogl\Documents\GitHub\LIAVH\210205_LIAVH_All.html')

# %%

import seaborn as sns
pt = pd.pivot_table(data=df[ df['N1'] == 'Artefacts' ][['Block','House','Time_Cat']], columns=['Block','House'] , index = 'Time_Cat' , aggfunc=len )
sns.heatmap(pt , cmap = 'OrRd' )

# %%

df.to_csv( r"C:\Users\csucuogl\Documents\GitHub\LIAVH\data\Processed_Data.csv")
# %%
