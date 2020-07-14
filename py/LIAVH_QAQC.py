# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 15:05:15 2020

@author: csucuogl
"""

#%% IMPORT
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly
import requests

#%% ------------- Definitions -------------

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

df = da.append( ds )

df['Block'] = df['Block'].astype(str) 
df = df[ df.Block == '7' ]

df['House'] = df['House'].replace(np.nan,None)
df['House'] = df['House'].dropna(axis = 0)
df['House'] = df['House'].astype(int).astype(str).str.zfill(2)

df = df[ df['House'].isin( ['07', '04', '03', '05', '06'] ) ]

df = df[ df.Level_ft != '?' ]
df = df[ df.Level_ft != '[?]' ]

df.loc[ df['Level_ft'] == 'SURFACE' , 'Level_ft' ] = 0
df.loc[ df['Level_ft'] == 'Surface' , 'Level_ft' ] = 0

df['Level_ft'] = df['Level_ft'].astype(float)

domestic = ['Animals', 'Cooking Baking Utensils', 'Personal Ornament', 
            'Vessels','Games And Toys', 'Human Figure',
            'Pottery - Incised and Painted', 'Pottery - Plain and Banded']
craft = [ 'Tools', 'Lithics' , 'Metal']

trade = ['Weights And Measures', 'Beads', 'Seal' ]

df.loc[df['Feature'].isin(domestic) , 'Class'] = 'Domestic'
df.loc[df['Feature'].isin(craft) , 'Class'] = 'Craft'
df.loc[df['Feature'].isin(trade) , 'Class'] = 'Trade'

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
df.sample(5)

#%%Images from GitHub
_ = ['1','2']
images = pd.DataFrame()
for i in _:
    resp = requests.get( 'https://api.github.com/repos/PrattSAVI/LIAVH/contents/images_1?ref=master' ).json()
    temp = pd.DataFrame.from_dict( resp )

    images = images.append( temp )
images = images.drop(['sha','size','url','html_url','git_url','type','_links'], axis = 1)
images['plate'] = [ (r.split('.')[0]).upper() for i,r in images['name'].iteritems() ]
images.sample( 5 )
#%% Match Images with Data

df = df.join( images.drop(['path','name'],axis = 1).set_index('plate') , on = 'Plate' )
df.sample(5)

df['download_url'] = df['download_url'].fillna( '' )

#%% PLOTLY

import plotly.graph_objects as go
import numpy as np
import matplotlib as mpl

time_order = [ 'Late Ia','Late Ib','Late II','Late III',
 'Intermediate I','Intermediate II','Intermediate III',
 'Early Periods']

ff = go.Figure() #Start an empty Figure Object

#STRATA LINES
for t in time_order: #Draw the Strata Lines
    at = df[ df['Time_Cat'] == t ]
    mins = at[['House','Level_ft']].groupby( by = 'House' ).min().reset_index()
    maxs = at[['House','Level_ft']].groupby( by = 'House' ).max().reset_index()
    al = mins.join( maxs.set_index('House') , on = 'House' , rsuffix = '_max')
     
    ff.add_trace(
        go.Scatter(
                x=al['House'], 
                y=al['Level_ft_max'],
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend = False
                )
            )
    ff.add_trace(
        go.Scatter(
                x=al['House'],
                y=al['Level_ft'],
                fill='tonexty',
                mode='lines',
                fillcolor='rgba(255,255,255,0.3)',
                line=dict(width=0, color='white'),
                showlegend = False,
                )
            )

#FLOOR FEATURE
cmap = mpl.cm.get_cmap('Set2')
colors = [ 'rgb(' + str(int(cmap(i)[0]*255)) + ',' + str(int(cmap(i)[1]*255)) + ',' + str(int(cmap(i)[2]*255)) + ')' for i in np.linspace( 0 ,1 , len( df[df['N1']=='Floor Features']['Feature'].unique() ) ) ]
count = 0
for f in df[df['N1']=='Floor Features']['Feature'].unique(): # Draw Floor Features
    dff = df[ (df['N1']=='Floor Features') & (df['Feature'] == f) ]

    ff.add_trace( # Draw Floor Features
        go.Scatter(
            mode='markers',
            x= dff['House'],
            y=dff['Level_ft'],
            legendgroup =  f,
            marker_symbol = 'line-ew',
            marker_line_color= colors[count], 
            marker_line_width=3, marker_size=15,
            name = f
            )
        )
    count = count + 1

#SWARM PLOT
def box_figure( df ): # Prepare the Swarm Plot

    cmap = mpl.cm.get_cmap('Set1')
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
                        'text': '<b>' + df[df['Class'] == item]['Feature'] + '</b>' + '<br>' + df[df['Class'] == item]['Text2'] + '<br>Link: <a href=' + df[df['Class'] == item]['download_url'] + '>' + df[df['Class'] == item]['Plate'] + '</a>' ,
                        'hovertemplate': "%{text}" ,
                        'legendgroup': item ,
                        'line': {'color': 'rgba(255,255,255,0)'},
                        'marker': { 
                                    'color': colors[ count ] ,
                                    'size': 6,
                                    'opacity':0.8
                                    },
                        'name': item,
                        'pointpos':0,
                        'type': 'box',
                        'x': df[df['Class'] == item]['House'].tolist(),
                        'y': df[df['Class'] == item]['Level_ft'].tolist(),
                        'jitter':1
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
    width = 900 , height = 700 ,
    showlegend=True,
    dragmode = 'zoom',
    hovermode = 'closest',
    hoverdistance = 60,
    plot_bgcolor = '#FDD2CD',
    paper_bgcolor = '#FDD2CD',
    title = 'Block 7 Artefact and Floor Features',
    margin=dict(l=50,r=50,b=50,t=100, pad=25 ),
    xaxis = dict(
        gridcolor = "rgb(255, 255, 255,0.5)",
        showgrid = True),
    yaxis = dict(
        gridcolor = "rgb(255, 255, 255,0.5)",
        gridwidth = 0.1)
    )
ff.update_layout(
    hoverlabel=dict(
        bgcolor="white", 
        font_size=11, 
        font_family="Corbel"
    )
)
ff.show()


# %% ----   Artifacts & Floor Features -> Format, Geocode and Export
# Match formats

gr1 = df[ df['N1'] == 'Artefacts' ].groupby( ['Block', 'House', 'Class', 'Time_Cat', 'Level_ft'] ).size().reset_index()
gr1.columns = gr1.columns.tolist()[:-1] + ['item_count']

gr1 = gr1.sort_values(['Block', 'House','Level_ft'])
gr1['Block'] = gr1['Block'].str.zfill(2) 
gr1['place'] = gr1['Block'] + '-' + gr1['House']

gr1.sample(5)

# %% Import GeoLocations

locs = gpd.read_file( r'C:\Users\csucuogl\Dropbox\MJD\DATA\GeoLocations.shp' )
locs['lat'] = locs.geometry.x
locs['lon'] = locs.geometry.y

locs.sample( 5 )

# %% Join Location info
grf = gr1.join( locs.drop('id',axis=1).set_index('place_id') , on = 'place')
grf.sample( 5 )

# %% Export Data
grf.to_csv( r"C:\Users\csucuogl\Desktop\WORK\LIAVH\MappingArtefacts.csv" )

