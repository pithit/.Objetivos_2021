from datetime import timedelta
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st


# https://code.visualstudio.com/docs/python/environments to find the venv

######### setting up the projects
st.cache(persist=True)
name = 'Peter'

def load_data(): 
    mytaskbars = pd.read_csv ('Original.csv')
    ########### changing DF variables format to manipulate them
    mytaskbars['start'] = pd.to_datetime(mytaskbars['start'])
    mytaskbars['end'] = pd.to_datetime(mytaskbars['end'])
    mytaskbars['Progress_%'] = mytaskbars['Progress_%'].astype(int)

    mytaskbars['progress date'] =  ((mytaskbars['end'] - mytaskbars['start']).dt.days) * (mytaskbars['Progress_%'] / 100) 
    mytaskbars['progress date2'] = (pd.to_timedelta(mytaskbars['progress date'], unit='D') + (mytaskbars['start'])).dt.round(freq='1D')

    newdf = np.concatenate([mytaskbars[['task', 'start', 'end', 'Progress_%', 'project', 'comment', 'nombre']].values,  
                            mytaskbars[['task', 'start', 'progress date2', 'Progress_%', 'project', 'comment', 'nombre']].values])
    newdf = pd.DataFrame(newdf, columns=['task', 'start', 'end', 'Progress_%', 'project', 'comment','nombre'])

    newdf['start'] = pd.to_datetime(newdf['start'])
    newdf['end'] = pd.to_datetime(newdf['end'])
    newdf['progress_'] = np.concatenate([np.ones(len(newdf)//2), np.zeros(len(newdf)//2), ])
    return newdf

newdf = load_data()

st.title('2022 Goals Dashboard')
st.sidebar.markdown(' **Disclaimmer** ')
st.sidebar.markdown(''' 
This app is to give insights about my goals for this 2022. I will track my progress of each one using this Dashboard

Designed by: 
**Peter Silva Alva**  ''')  

st.header("Select the corresponding name")
    
cty = st.selectbox("Select name", newdf.nombre.unique())

############ Building the chart

newdf2 = newdf[newdf['nombre']==cty]

chart = alt.Chart(newdf2).mark_bar(opacity=0.7).encode(
    x=alt.X('start', axis=alt.Axis(
        title='Date', 
        values=[d.isoformat() for d in pd.date_range('2021-08-02', freq='14D', periods=104)],
        labelAngle=-90, labelFontSize=12, titleFontSize=14,
        #format = ('%b %Y'))
        format='%a %b %_d',
        tickCount=104)),
    x2='end',
    y=alt.Y('project', axis=alt.Axis(title = 'Projects', labelFontSize=14, titleFontSize=20), sort = list(newdf2.sort_values(['end', 'start']) ['project']*2)),
    #color=alt.Color('progress_', legend=None),
    color=alt.Color('project:N', legend=None), #alt.Legend(strokeColor='gray', fillColor='#EEEEEE', padding=10, cornerRadius=10,orient='top-right')),
    tooltip=['project', 'task', 'start', 'end', 'comment']
).properties(title= str(name) + ' - Projects', width=1000, height=600).interactive()

newdf2['text%'] = newdf2['Progress_%'].astype(str) + ' %'

text = alt.Chart(newdf2).mark_text(align='left', baseline='middle', dx=5, color='white',  fontWeight='bold').encode(
    y=alt.Y('project', sort=list(newdf2.sort_values(['end','start'])['project'])*2),
    x=alt.X('start'),
    text='text%',
)

shade = pd.DataFrame({'Q_ini': ['2021-12-31', '2022-04-01', '2022-07-01', '2022-10-01'],
                        'Q_fin': ['2022-03-31', '2022-06-30', '2022-09-30', '2022-12-31']})
shade['Q_ini'] = pd.to_datetime(shade['Q_ini'])
shade['Q_fin'] = pd.to_datetime(shade['Q_fin'])

areas = alt.Chart(shade.reset_index()).mark_rect(opacity=0.15).encode(x='Q_ini',x2='Q_fin',
    #y=alt.value(0),  # pixels from top
    #y2=alt.value(300),  # pixels from top
    color=alt.value('gray')) #'index:N')

plot = chart + text + areas

# plot_new = alt.concat(plot).properties(title=alt.TitleParams(
#         ['Follow ups:', 
#         '- Formula Price Simulation & Standard Analysis -> There is a file with the update of this project',
#         '- PTM -> There is a file with the update of this project',
#         '- Harden PHI Dashboard (given to Mario)',
#         '- PHI Visualization Dashboard - segmented data to show (given to Mario)',
#         '- Github access - contact EMIT to unlock my access (working on this)'],
#         baseline='top', #top
#         orient='bottom', #bottom
#         anchor='start', #end
#         fontWeight='normal',
#         fontSize=14))

st.altair_chart(plot, use_container_width=True)

# plot.save(str(name) + '_Gantt_Chart.html')

# streamlit run Dashboard.py