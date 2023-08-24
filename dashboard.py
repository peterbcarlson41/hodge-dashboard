import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Trim
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

#Function to create stacked bar plot for the meat presence by restaurant
def create_meat_stacked_bar_plot(data):
    # Group the data by "Restaurant" and "Meat Y/N/U" and count the occurrences
    meat_presence_counts = data.groupby(['Restaurant', 'Meat Y/N/U']).size().unstack(fill_value=0)

    # Create a stacked bar chart using Plotly Express
    fig = go.Figure(data=[
        go.Bar(name='Meat - Yes', x=meat_presence_counts.index, y=meat_presence_counts['Y']),
        go.Bar(name='Meat - No', x=meat_presence_counts.index, y=meat_presence_counts['N']),
        go.Bar(name='Meat - Unknown', x=meat_presence_counts.index, y=meat_presence_counts['U'])
    ])

    fig.update_layout(barmode='stack', xaxis_title='Restaurant', yaxis_title='Count',
                      title='Meat Presence in Restaurants (Stacked Bar Plot)')
    fig.update_xaxes(title='Restaurant Name', tickangle=-45)

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

# Define a CSS style dictionary to set a different background color for "All Buckets" rows
conditional_style = [
    {
        'if': {'filter_query': '{Stream} = "All Buckets"'},
        'backgroundColor': 'lightgray',  # You can change this color to your preference
    }
]


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
    html.Br(),
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
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='meat-stacked-bar'), width=12),  # Meat presence stacked bar chart
    ]),
    html.Br(),
    dbc.Row([
        html.Div(
            "Average Weight by Type and Stream",
            style={
                "textAlign": "center",  # Center text horizontally
            },
        ),
        html.Br(),
        dbc.Col(dash_table.DataTable(id='average-weight-table', style_data_conditional=conditional_style), width=12)  # Add this line for the table
    ]),
    html.Br()
])

# Callback to update stacked bar chart, zoomed-in stacked bar chart, and pie chart based on selected values
@app.callback(
    [Output('stacked-bar', 'figure'),
     Output('zoomed-stacked-bar', 'figure'),
     Output('pie-chart', 'figure'),
     Output('mean-bucket-weight', 'children'),
     Output('median-bucket-weight', 'children'),
     Output('meat-stacked-bar', 'figure'),
     Output('average-weight-table', 'data'),
     Output('average-weight-table', 'columns')],
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

    meat_stacked_bar = create_meat_stacked_bar_plot(full_data)
    
    # Calculate the average weight for each Stream and Type combination
    average_weight_data = filtered_data.groupby(['Type', 'Stream'])['Weight'].mean().reset_index()

    # Calculate the average weight for all buckets that fall under each type
    average_weight_all_buckets = average_weight_data.groupby('Type')['Weight'].mean().reset_index()
    average_weight_all_buckets['Stream'] = 'All Buckets'

    # Create a list to store the final rows for the table
    table_rows = []

    # Iterate through each type
    for type_name in filtered_data['Type'].unique():
        type_data = average_weight_data[average_weight_data['Type'] == type_name]
        
        # Append rows for individual streams within the type
        for _, row in type_data.iterrows():
            table_rows.append([type_name, row['Stream'], row['Weight']])
        
        # Append the row for all buckets after the type's individual streams
        all_buckets_row = average_weight_all_buckets[average_weight_all_buckets['Type'] == type_name]
        if not all_buckets_row.empty:
            table_rows.append([type_name, 'All Buckets', all_buckets_row.iloc[0]['Weight']])

    # Create a DataFrame from the collected table rows
    average_weight_data = pd.DataFrame(table_rows, columns=['Type', 'Stream', 'Average Weight'])

    # Define columns for the average weight table
    average_weight_table_columns = [
        {'name': 'Type', 'id': 'Type'},
        {'name': 'Stream', 'id': 'Stream'},
        {'name': 'Average Weight', 'id': 'Average Weight', 'type': 'numeric', 
        'format': Format(precision=4), 'auto_format': True}
    ]

    return (
        stacked_bar_updated, zoomed_stacked_bar, pie_chart,
        f"Mean Bucket Weight: {mean_bucket_weight_selected:.2f} lbs",
        f"Median Bucket Weight: {median_bucket_weight_selected:.2f} lbs",
        meat_stacked_bar,
        average_weight_data.to_dict('records'),
        average_weight_table_columns 
    )





if __name__ == '__main__':
    app.run_server(debug=False)