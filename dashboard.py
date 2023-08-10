import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import dash
from dash import dcc
from dash import html

# Sample data obtained from the get_data function (replace this with your actual data)
from data import get_data

full_data = get_data()

server = ""

# Function to create stacked bar plot
def create_stacked_bar_plot(data):
    category_by_restaurant = pd.concat([data["Restaurant"], data["Primary category"]], axis=1)
    category_stacked = category_by_restaurant.groupby(['Restaurant', 'Primary category']).size().unstack().fillna(0)
    
    fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns,
                 color_discrete_sequence=px.colors.qualitative.Dark24,
                 title='Primary Food Waste Category by Restaurant Name (Stacked Bar Plot)')
    
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Restaurant Name', tickangle=-45)
    fig.update_yaxes(title='Count')
    
    return fig


full_data = get_data()

# Create the stacked bar plot
fig = create_stacked_bar_plot(full_data)

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the app layout
app.layout = html.Div([
    dcc.Graph(figure=fig),
])

if __name__ == '__main__':
    app.run_server(debug=False)
    