import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Sample data obtained from the get_data function (replace this with your actual data)
from data import get_data

full_data = get_data()

server = ""

# Get unique categories and assign colors programmatically
unique_categories = full_data['Primary category'].unique()
category_colors = {category: px.colors.qualitative.Dark24[i % len(px.colors.qualitative.Light24)]
                   for i, category in enumerate(unique_categories)}

#filter the data based on selected criteria
def filter_data(selected_types):
    if 'All' in selected_types:
        return full_data
    else:
        return full_data[full_data['Type'].isin(selected_types)]

# Updated function to create stacked bar plot
def create_stacked_bar_plot(selected_types):
    filtered_data = filter_data(selected_types)
    category_by_restaurant = pd.concat([filtered_data["Restaurant"], filtered_data["Primary category"]], axis=1)
    category_stacked = category_by_restaurant.groupby(['Restaurant', 'Primary category']).size().unstack().fillna(0)
    
    fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns,
                 color_discrete_map=category_colors,
                 title='Primary Food Waste Category by Restaurant Name (Stacked Bar Plot)')
    
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Restaurant Name', tickangle=-45)
    fig.update_yaxes(title='Count')
    
    return fig

# Function to create zoomed-in stacked bar plot
def create_zoomed_stacked_bar_plot(data, selected_restaurant):
    restaurant_data = data[data['Restaurant'] == selected_restaurant]
    category_by_restaurant = pd.concat([restaurant_data["Restaurant"], restaurant_data["Primary category"]], axis=1)
    category_stacked = category_by_restaurant.groupby(['Restaurant', 'Primary category']).size().unstack().fillna(0)
    
    fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns,
                 color_discrete_map=category_colors,
                 title=f'Primary Food Waste Category for {selected_restaurant} (Zoomed In)',
                 height=400)  # Adjust the height as needed
    
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Restaurant Name')
    fig.update_yaxes(title='Count')
    
    return fig

# Function to create pie chart
def create_pie_chart(data, selected_restaurant):
    restaurant_data = data[data['Restaurant'] == selected_restaurant]
    category_counts_restaurant = restaurant_data.groupby('Primary category').size().reset_index(name='Count')
    
    fig = px.pie(category_counts_restaurant, values='Count', names='Primary category',
                 title=f'Primary Food Waste Category for {selected_restaurant}',
                 color_discrete_map=category_colors)
    
    return fig

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create the stacked bar plot
stacked_bar = create_stacked_bar_plot(['All'])

# Define the app layout using Dash Bootstrap components
app.layout = dbc.Container([
    html.Center(
        html.H1("Material Audit Dashboard"),
    ),
    dbc.Row([
        dbc.Col([
            dcc.Checklist(
                id='type-checklist',
                options=[
                    {'label': 'Pre', 'value': 'Pre'},
                    {'label': 'Post', 'value': 'Post'},
                    {'label': 'Mixed', 'value': 'Mixed'},
                    {'label': 'All', 'value': 'All'}
                ],
                value=['All'],
                inline=True,
            ),
        ]),
       dbc.Col([
            dcc.Dropdown(
                id='new-dropdown',
                options=[
                    {'label': category, 'value': category} for category in full_data['High Level Category'].unique()
                ],
                value=full_data['High Level Category'].unique(),
                multi=True,
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='stacked-bar', figure=stacked_bar), width=12),  # Full-sized stacked bar chart
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='zoomed-stacked-bar'), width=6),  # Zoomed-in stacked bar chart
        dbc.Col(dcc.Graph(id='pie-chart'), width=6),  # Pie chart
    ])
])

# Callback to update zoomed-in stacked bar chart and pie chart based on selected types
@app.callback(
    [Output('stacked-bar', 'figure'),
     Output('zoomed-stacked-bar', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('stacked-bar', 'clickData'),
     Input('type-checklist', 'value')]
)
def update_charts(clickData, selected_types):
    filtered_data = filter_data(selected_types)
    
    if clickData is None:
        selected_restaurant = filtered_data['Restaurant'].iloc[0]  # Default to the first restaurant
    else:
        selected_restaurant = clickData['points'][0]['x']
    
    stacked_bar_updated = create_stacked_bar_plot(selected_types)
    zoomed_stacked_bar = create_zoomed_stacked_bar_plot(filtered_data, selected_restaurant)
    pie_chart = create_pie_chart(filtered_data, selected_restaurant)
    
    return stacked_bar_updated, zoomed_stacked_bar, pie_chart

if __name__ == '__main__':
    app.run_server(debug=False)