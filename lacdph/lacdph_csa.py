#!/usr/bin/env python
# coding: utf-8

# In[52]:


import os
import geopandas
import pandas as pd
import numpy as np
import plotly.express as px
DATE = 'date'
AREA = 'area'
px.set_mapbox_access_token(os.environ['MAPBOXKEY_CAVAX'])


# In[26]:


df_7day_orig, df_14day_orig = [
    pd.read_csv(
        f'LA_County_Covid19_CSA_{x}day_case_death_table.csv',
        parse_dates=['ep_date'],
        infer_datetime_format=True
    )
    .drop(columns='Unnamed: 0')
    .rename(columns={'ep_date': DATE, 'geo_merge': AREA})
    .sort_values([DATE, AREA])
    .reset_index(drop=True)
    for x in (7, 14)
]
df_7day_orig = df_7day_orig[df_7day_orig[DATE].notna()]
df_14day_orig = df_14day_orig[df_14day_orig[DATE].notna()]
for df in (df_7day_orig, df_14day_orig):
    for col in ('case_rate_unstable', 'death_rate_unstable'):
        df[col] = (df[col]=='^').astype(bool)
    df[AREA] = df[AREA].convert_dtypes()
    df['population'] = df['population'].astype('int')
for col in df_7day_orig:
    if '7day' in col:
        df_7day_orig[col] = (df_7day_orig[col] / 7).round(1)
for col in df_14day_orig:
    if '14day' in col:
        df_14day_orig[col] = (df_14day_orig[col] / 14).round(1)


# In[94]:


df_csa = (
    geopandas.read_file('lac-csa.geojson')
    [['LABEL', 'geometry']]
    .copy()
    .rename(columns={'LABEL': AREA})
)
df_csa[AREA] = df_csa[AREA].convert_dtypes()
df_csa = df_csa.set_index(AREA)


# In[51]:


# Plot parameters
seven_day = True
area = 'Los Angeles - North Hollywood'
start_date = '2021-03-01'
end_date = None

# Plot specific calculations
df_plot = df_7day_orig if seven_day else df_14day_orig
df_plot = df_plot[df_plot[AREA]==area]
window_days = 7 if seven_day else 14
dep_var = f'case_{window_days}day_rate'

# Determine plot range
df_range = df_plot[[DATE, dep_var]]
if start_date is not None:
    df_range = df_range[df_range[DATE]>=start_date]
if end_date is not None:
    df_range = df_range[df_range[DATE]<=end_date]
y_max = 1.05 * df_range[dep_var].max()

fig = px.line(
    df_plot,
    x=DATE,
    y=dep_var,
    title=f'COVID-19 Cases in {area}',
    height=500
)
fig.update_xaxes(
    title='',
    range=[df_range[DATE].min(), df_range[DATE].max()]
)
fig.update_yaxes(
    title=f'New cases, {window_days} average',
    range=[0, y_max]
)
fig.show()


# In[ ]:


seven_day = True
days_to_use = 1,
df_plot = df_7day_orig if seven_day else df_14day_orig
df_plot = df_plot[df_plot[DATE].apply(lambda x: x.day).isin(days_to_use)]
# df_plot = df_plot[df_plot[AREA]=='City of Burbank']
df_plot = df_plot.copy()
df_plot[DATE] = df_plot[DATE].apply(lambda x: x.strftime('%Y-%m-%d'))
window_range = 7 if seven_day else 14
dep_var = f'case_{window_days}day_rate'
# fig = px.choropleth(
#     data_frame=df_plot,
#     geojson=df_csa.geometry.to_json(),
#     locations=AREA,
#     color=f'case_{window_days}day_rate',
#     animation_frame=DATE,
# #     animation_group=AREA
# )
# fig.show()


# In[69]:


df_plot[df_plot[DATE].apply(lambda x: x.day).isin(days_to_use)]


# In[102]:


gapminder = px.data.gapminder()
px.choropleth(df_plot,               
              locations=AREA,
              geojson=df_csa,
              color=dep_var,
#               hover_name="country",  
              animation_frame=DATE,    
#               color_continuous_scale='Plasma',  
              height=600             
)

