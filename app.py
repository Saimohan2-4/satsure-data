import pandas as pd
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

repo_owner = 'Saimohan2-4'
repo_name = 'sample-for-satsure-data'
branch = 'main'
file_path = 'sample_dataset_large.csv'

# Construct the raw GitHub URL
url = f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}'

# Load the dataset from the GitHub URL
df = pd.read_csv(url)

# Convert necessary columns to datetime
df['Date'] = pd.to_datetime(df['Date'])
df['Start_Date'] = pd.to_datetime(df['Start_Date'])
df['End_Date'] = pd.to_datetime(df['End_Date'])

# Calculate Cycle Time
df['Cycle_Time'] = (df['End_Date'] - df['Start_Date']).dt.days

# Calculate Sprints (assuming 2-week sprints)
df['Sprint'] = ((df['Date'] - df['Date'].min()) // pd.Timedelta(weeks=2)).astype(int) + 1

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout with 3 pages and navigation buttons
app.layout = html.Div(style={'background-color': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Software Development Metrics Dashboard', style={'text-align': 'center'}),
    
    html.Div([
        html.Button('Page 1', id='page-1-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('Page 2', id='page-2-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('Page 3', id='page-3-button', n_clicks=0)
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    
    html.Div(id='page-content'),
    
    html.Div(id='hidden-div', style={'display': 'none'}),
    
    dcc.Interval(
        id='interval-component',
        interval=60000,  # Update interval in milliseconds (e.g., 60000 ms = 1 minute)
        n_intervals=0
    )
])

# Callback to update data from GitHub
@app.callback(
    Output('hidden-div', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_data(n_intervals):
    global df
    df = pd.read_csv(url)
    
    # Convert necessary columns to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df['Start_Date'] = pd.to_datetime(df['Start_Date'])
    df['End_Date'] = pd.to_datetime(df['End_Date'])
    
    # Calculate Cycle Time
    df['Cycle_Time'] = (df['End_Date'] - df['Start_Date']).dt.days
    
    # Calculate Sprints (assuming 2-week sprints)
    df['Sprint'] = ((df['Date'] - df['Date'].min()) // pd.Timedelta(weeks=2)).astype(int) + 1
    
    return ''

# Callback to render different pages
@app.callback(
    Output('page-content', 'children'),
    [Input('page-1-button', 'n_clicks'),
     Input('page-2-button', 'n_clicks'),
     Input('page-3-button', 'n_clicks')]
)
def display_page(page_1_clicks, page_2_clicks, page_3_clicks):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'page-1-button':
        return render_page_1()
    elif button_id == 'page-2-button':
        return render_page_2()
    elif button_id == 'page-3-button':
        return render_page_3()
    else:
        return render_page_1()  # Default to page 1 on initial load

def render_page_1():
    return html.Div([
        html.Div([
            dcc.RadioItems(
                id='sprint-radioitems',
                options=[{'label': f'Sprint {i}', 'value': i} for i in sorted(df['Sprint'].unique())],
                value=df['Sprint'].min(),  # Initial value
                inline=True,
                style={'color': 'white'}
            )
        ], style={'text-align': 'left', 'margin-bottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='velocity-graph', style={'display': 'inline-block', 'width': '49%', 'padding-right': '10px'}),
            dcc.Graph(id='cycle-time-graph', style={'display': 'inline-block', 'width': '49%', 'padding-left': '10px'})
        ], style={'text-align': 'center', 'margin-bottom': '20px'}),
        
        dcc.Graph(id='defect-rate-graph')
    ])

@app.callback(
    [Output('velocity-graph', 'figure'),
     Output('cycle-time-graph', 'figure'),
     Output('defect-rate-graph', 'figure')],
    [Input('sprint-radioitems', 'value')]
)
def update_page_1(selected_sprint):
    filtered_df = df[df['Sprint'] == selected_sprint]
    
    # Velocity Chart
    velocity_fig = px.bar(filtered_df, x='Task_ID', y='Story_Points', title=f'Velocity - Sprint {selected_sprint}')
    
    # Cycle Time Chart
    cycle_time_fig = px.line(filtered_df, x='Task_ID', y='Cycle_Time', title=f'Cycle Time - Sprint {selected_sprint}', text='Cycle_Time')
    cycle_time_fig.update_traces(textposition="bottom right")
    
    # Defect Rate Chart
    defect_rate_fig = px.bar(filtered_df, x='Task_ID', y='Defects_Reported', title=f'Defect Rate - Sprint {selected_sprint}')
    
    return velocity_fig, cycle_time_fig, defect_rate_fig

def render_page_2():
    return html.Div([
        html.Div([
            dcc.RadioItems(
                id='sprint-radioitems-page-2',
                options=[{'label': f'Sprint {i}', 'value': i} for i in sorted(df['Sprint'].unique())],
                value=df['Sprint'].min(),  # Initial value
                inline=True,
                style={'color': 'white'}
            )
        ], style={'text-align': 'left', 'margin-bottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='time-slippage-graph', style={'display': 'inline-block', 'width': '49%', 'padding-right': '10px'}),
            dcc.Graph(id='sprint-burndown-graph', style={'display': 'inline-block', 'width': '49%', 'padding-left': '10px'})
        ], style={'text-align': 'center', 'margin-bottom': '20px'}),
        html.Div([
            dcc.Graph(id='lead-time-graph', style={'display': 'inline-block', 'width': '49%', 'padding-right': '10px'}),
            dcc.Graph(id='resource-utilization-graph', style={'display': 'inline-block', 'width': '49%', 'padding-left': '10px'})
        ], style={'text-align': 'center', 'margin-bottom': '20px'})
    ])

@app.callback(
    [Output('time-slippage-graph', 'figure'),
     Output('sprint-burndown-graph', 'figure'),
     Output('lead-time-graph', 'figure'),
     Output('resource-utilization-graph', 'figure')],
    [Input('sprint-radioitems-page-2', 'value')]
)
def update_page_2(selected_sprint):
    filtered_df = df[df['Sprint'] == selected_sprint]
    
    # Calculate Time Slippage (Actual_Hours - Estimated_Hours)
    filtered_df['Time_Slippage'] = filtered_df['Actual_Hours'] - filtered_df['Estimated_Hours']
    
    # Time Slippage Chart
    time_slippage_fig = px.bar(filtered_df, x='Task_ID', y='Time_Slippage', title='Time Slippage')
    
    # Sprint Burndown Chart
    tasks_remaining = filtered_df[filtered_df['Status'] == 'In Progress'].groupby('Date').size().cumsum().reset_index(name='Tasks_Remaining')
    sprint_burndown_fig = px.line(tasks_remaining, x='Date', y='Tasks_Remaining', title='Sprint Burndown', text='Tasks_Remaining')
    sprint_burndown_fig.update_traces(textposition="bottom right")
    
    # Lead Time Chart
    lead_time_fig = px.line(filtered_df, x='Task_ID', y='Cycle_Time', title='Lead Time')
    
    # Resource Utilization Pie Chart
    resource_utilization_fig = px.pie(filtered_df, names='Resource', values='Actual_Hours', title='Resource Utilization')
    
    return time_slippage_fig, sprint_burndown_fig, lead_time_fig, resource_utilization_fig

def render_page_3():
    return html.Div([
        html.Div([
            dcc.RadioItems(
                id='sprint-radioitems-page-3',
                options=[{'label': f'Sprint {i}', 'value': i} for i in sorted(df['Sprint'].unique())],
                value=df['Sprint'].min(),  # Initial value
                inline=True,
                style={'color': 'white'}
            )
        ], style={'text-align': 'left', 'margin-bottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='rework-graph', style={'display': 'inline-block', 'width': '49%', 'padding-right': '10px'}),
            dcc.Graph(id='task-distribution-graph', style={'display': 'inline-block', 'width': '49%', 'padding-left': '10px'})
        ], style={'text-align': 'center', 'margin-bottom': '20px'}),
        
        dcc.Graph(id='cumulative-flow-graph')
    ])

@app.callback(
    [Output('rework-graph', 'figure'),
     Output('task-distribution-graph', 'figure'),
     Output('cumulative-flow-graph', 'figure')],
    [Input('sprint-radioitems-page-3', 'value')]
)
def update_page_3(selected_sprint):
    filtered_df = df[df['Sprint'] == selected_sprint]
    
    # Rework Chart
    rework_fig = px.bar(filtered_df, x='Task_ID', y='Rework_Hours', title='Rework')
    
    # Task Distribution Pie Chart
    task_distribution_fig = px.pie(filtered_df, names='Task_Type', title='Task Distribution')
    
    # Cumulative Flow Diagram
    cumulative_flow_data = filtered_df.groupby(['Date', 'Status']).size().unstack().cumsum().reset_index()
    cumulative_flow_fig = px.area(cumulative_flow_data, x='Date', y=cumulative_flow_data.columns[1:], title='Cumulative Flow Diagram')
    
    return rework_fig, task_distribution_fig, cumulative_flow_fig

if __name__ == '__main__':
    app.run_server(debug=True)
