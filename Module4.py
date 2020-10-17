# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 16:06:32 2020

@author: x
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

tree_query = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=boroname,health,steward,spc_common,count(tree_id)' +\
        '&$group=boroname,spc_common,steward,health').replace(' ', '%20')

trees = pd.read_json(tree_query)


#Setting up total for tree count by type
tree_totals = trees.groupby(['boroname','spc_common','steward'])['count_tree_id'].sum()
tree_totals = tree_totals.reset_index(drop=False)
tree_totals.columns = ['boroname', 'common_name', 'steward','total_in_boro']

#Setting up total by health
tree_total_spec_health = trees.groupby(['boroname', 'spc_common', 'health','steward'])['count_tree_id'].sum()
tree_total_spec_health = tree_total_spec_health.reset_index(drop=False)
tree_total_spec_health.columns = ['boroname', 'common_name', 'health','steward','total_by_health']

#combining them
tree_df = pd.merge(tree_total_spec_health, tree_totals, on=['boroname', 'common_name', 'steward'])

#Getting the Ratio
tree_df['ratio']=tree_df['total_by_health']/tree_df['total_in_boro']

df=tree_df

boro_indicators = df['boroname'].unique()
tree_indicators = df['common_name'].unique()
health_indicators = df['health'].unique()
steward_indicators = df['steward'].unique()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([

        html.Label(["Choose Boro", html.Div([
            dcc.Dropdown(
                id='boro_dropdown',
                options=[{'label': i, 'value': i} for i in boro_indicators],
                value='boroname'
            )
        ],
        style={'width': '30%', 'display': 'inline-block'})]),

        html.Label(["Choose Steward number", html.Div([
            dcc.Dropdown(
                id='steward_dropdown',
                options=[{'label': i, 'value': i} for i in steward_indicators],
                value='steward'
            )
        ],style={'width': '30%', 'display': 'inline-block'})
    ])]),
	
    dcc.Graph(id='graph-by-boro'),
    
    html.Div([
        dcc.Markdown("""
              Question 1: What proportion of the trees are in good, fair, 
                  or poor health according to the ‘health’ variable?  
              Question 2: Are stewards (steward activity measured by the 
              ‘steward’ variable) having an impact on the health of trees?  
              
              The graph answers both questions and adds an additional feature.
              
              -Boro filters the graph to a specific Boro  
              -Steward Amount filters the graph to a amount of stewards per tree specics.
              
              The Size and the Color of the dots relate to the ratio of Total number of trees types
              in each health category divided by the Total number of the same tree type in the boro.
                       
              health/total = ratio	
                
                """)    
           ])
    
])


@app.callback(
    Output('graph-by-boro', 'figure'),
    [Input('boro_dropdown', 'value'),
     Input('steward_dropdown', 'value')])
def update_graph(selected_boro, selected_steward):
    filtered_df = df[df.boroname == selected_boro]
    filtered_df = filtered_df[filtered_df.steward == selected_steward]

    fig = px.scatter(filtered_df, x='total_in_boro', y='health', 
                     size='ratio', color = 'ratio', hover_name='common_name', 
                     log_x=True, size_max=55)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)