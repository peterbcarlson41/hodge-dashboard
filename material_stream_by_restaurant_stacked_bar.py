import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import dash
from dash import dcc
from dash import html

# Create a directory to save the images
output_directory = "stacked_bar_images"
os.makedirs(output_directory, exist_ok=True)

# Sample data obtained from the get_data function (replace this with your actual data)
from data import get_data

full_data = get_data()

primary_category = full_data["Primary category"]
restaurant_name = full_data["Restaurant"]

category_by_restaurant = pd.concat([restaurant_name, primary_category], axis=1)

# Group data and unstack to create the stacked bar plot
category_stacked = category_by_restaurant.groupby(['Restaurant', 'Primary category']).size().unstack().fillna(0)

# Create the stacked bar plot using Plotly Express
fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns, color_discrete_sequence=px.colors.qualitative.Dark24, title='Primary Food Waste Category by Restaurant Name (Stacked Bar Plot)')
fig.update_layout(barmode='stack')
fig.update_xaxes(title='Restaurant Name', tickangle=-45)
fig.update_yaxes(title='Count')

# Save the figure as an HTML file
html_filename = os.path.join(output_directory, "stacked_bar_chart.html")
pio.write_html(fig, file=html_filename)

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Graph(figure=fig),
])

if __name__ == '__main__':
    app.run_server(debug=True)
