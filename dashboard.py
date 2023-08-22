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

#intialize bucket weight data
mean_bucket_weight = full_data['Weight'].mean()
median_bucket_weight = full_data['Weight'].median()


# Get unique categories and assign colors programmatically
unique_categories = full_data['Stream'].unique()
category_colors = {category: px.colors.qualitative.Dark24[i % len(px.colors.qualitative.Light24)]
                   for i, category in enumerate(unique_categories)}


def filter_data(selected_types, single_ingredient_value, selected_categories):
    filtered_data = full_data
    
    # Apply filtering based on selected types
    filtered_data = filtered_data[filtered_data['Type'].isin(selected_types)]
    
    # Apply filtering based on single ingredient checkbox values
    if 'Yes' in single_ingredient_value and 'No' not in single_ingredient_value:
        filtered_data = filtered_data[filtered_data['Single Ingredient?'] == 'Y']
    elif 'No' in single_ingredient_value and 'Yes' not in single_ingredient_value:
        filtered_data = filtered_data[filtered_data['Single Ingredient?'] == 'N']
    
    # Apply filtering based on selected categories
    filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]
    
    return filtered_data
    

# Updated function to create stacked bar plot
def create_stacked_bar_plot(selected_types, single_ingredient_value, selected_categories):
    filtered_data = filter_data(selected_types, single_ingredient_value, selected_categories)
    category_by_restaurant = pd.concat([filtered_data["Restaurant"], filtered_data["Stream"]], axis=1)
    category_stacked = category_by_restaurant.groupby(['Restaurant', 'Stream']).size().unstack().fillna(0)
    
    fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns,
                 color_discrete_map=category_colors,
                 title='Primary Food Waste Stream by Restaurant Name (Stacked Bar Plot)')
    
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Restaurant Name', tickangle=-45)
    fig.update_yaxes(title='Count')
    
    return fig

# Function to create zoomed-in stacked bar plot
def create_zoomed_stacked_bar_plot(data, selected_restaurant):
    restaurant_data = data[data['Restaurant'] == selected_restaurant]
    category_by_restaurant = pd.concat([restaurant_data["Restaurant"], restaurant_data["Stream"]], axis=1)
    category_stacked = category_by_restaurant.groupby(['Restaurant', 'Stream']).size().unstack().fillna(0)
    
    fig = px.bar(category_stacked, x=category_stacked.index, y=category_stacked.columns,
                 color_discrete_map=category_colors,
                 title=f'Primary Food Waste Stream for {selected_restaurant} (Zoomed In)',
                 height=400)  # Adjust the height as needed
    
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Restaurant Name')
    fig.update_yaxes(title='Count')
    
    return fig

# Function to create pie chart
def create_pie_chart(data, selected_restaurant):
    restaurant_data = data[data['Restaurant'] == selected_restaurant]
    category_counts_restaurant = restaurant_data.groupby('Stream').size().reset_index(name='Count')
    
    fig = px.pie(category_counts_restaurant, values='Count', names='Stream',
                 title=f'Primary Food Waste Stream for {selected_restaurant}',
                 color_discrete_map=category_colors)
    
    return fig

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create the default stacked bar plot with all values initially selected
stacked_bar = create_stacked_bar_plot(
    selected_types=['Pre', 'Post', 'Mixed'],
    single_ingredient_value=['Yes', 'No'],
    selected_categories=full_data['Category'].unique()
)


# Define the app layout using Dash Bootstrap components
app.layout = dbc.Container([
    html.Center(
        html.H1("Material Audit Dashboard"),
    ),
    dbc.Row([
        dbc.Col([
            html.H6("Type:"), 
            dcc.Checklist(
                id='type-checklist',
                options=[
                    {'label': 'Pre', 'value': 'Pre'},
                    {'label': 'Post', 'value': 'Post'},
                    {'label': 'Mixed', 'value': 'Mixed'},
                ],
                value=['Pre', 'Post', 'Mixed'],
            ),
        ]),
        dbc.Col([
            html.H6("Single Ingredient:"), 
            dcc.Checklist(
                id='single-ingredient-checklist',
                options=[
                    {'label': 'Yes', 'value': 'Yes'},
                    {'label': 'No', 'value': 'No'},
                ],
                value=['Yes', 'No'],
            ),
        ]),
        dbc.Col([
            html.H6("High Level Categories:"), 
            dcc.Dropdown(
                id='new-dropdown',
                options=[{'label': 'All Categories', 'value': 'all'}] + [{'label': category, 'value': category} for category in full_data['Category'].unique()],
                value='all',  # Set the default value to 'all'
                multi=True,
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H6(id='mean-bucket-weight'),
            html.H6(id='median-bucket-weight'),
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

# Callback to update stacked bar chart, zoomed-in stacked bar chart, and pie chart based on selected values
@app.callback(
    [Output('stacked-bar', 'figure'),
     Output('zoomed-stacked-bar', 'figure'),
     Output('pie-chart', 'figure'),
     Output('mean-bucket-weight', 'children'),
     Output('median-bucket-weight', 'children')],
    [Input('stacked-bar', 'clickData'),
     Input('type-checklist', 'value'),
     Input('single-ingredient-checklist', 'value'),
     Input('new-dropdown', 'value')]  # Add input for the dropdown
)
def update_charts(clickData, selected_types, single_ingredient_value, selected_categories):
    if 'all' in selected_categories:
        selected_categories = full_data['Category'].unique()  # Select all categories

    filtered_data = filter_data(selected_types, single_ingredient_value, selected_categories)
    
    if clickData is None:
        selected_restaurant = filtered_data['Restaurant'].iloc[0]  # Default to the first restaurant
    else:
        selected_restaurant = clickData['points'][0]['x']
    
    stacked_bar_updated = create_stacked_bar_plot(selected_types, single_ingredient_value, selected_categories)
    zoomed_stacked_bar = create_zoomed_stacked_bar_plot(filtered_data, selected_restaurant)
    pie_chart = create_pie_chart(filtered_data, selected_restaurant)
    
    # Calculate mean and median bucket weight values for the selected type(s)
    mean_bucket_weight_selected = filtered_data['Weight'].mean()
    median_bucket_weight_selected = filtered_data['Weight'].median()
    
    return (
        stacked_bar_updated, zoomed_stacked_bar, pie_chart,
        f"Mean Bucket Weight: {mean_bucket_weight_selected:.2f} lbs",
        f"Median Bucket Weight: {median_bucket_weight_selected:.2f} lbs"
    )

if __name__ == '__main__':
    app.run_server(debug=False)