import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis
import json
import time

#Connect to redis
def get_redis_data():
    r = redis.Redis(host='localhost', port=6379, decode_responses = True)
    raw_data = r.get('augustovicente-proj3-output')
    if raw_data:
        return json.loads(raw_data)
    return {}

#Initialize dash app
app = dash.Dash(__name__)
app.title = 'Real Time Metrics Dashboard'

#Layout
app.layout = html.Div([
    html.H1('Real Time Metrics Dashboard', style={'text-align': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=5*1e3,
        n_intervals=0
    ),
    dcc.Graph(id='cpu-usage-graph'),
    dcc.Graph(id='memory-network-graph')
])

#Callbacks
@app.callback(
    [Output('cpu-usage-graph', 'figure'),
     Output('memory-network-graph', 'figure')],
     [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    data = get_redis_data()

    if not data:
        return go.Figure(), go.Figure()
    
    #CPU Usage Graph
    cpu_data = {key: value for key, value in data.items() if key.startswith('avg-util-cpu')}
    cpu_fig = go.Figure()
    cpu_fig.add_trace(go.Bar(
        x = list(cpu_data.keys()),
        y = list(cpu_data.values()),
        name = 'CPU Usage (%)',
        marker_color='blue'
    ))
    cpu_fig.update_layout(
        title='Average CPU Utilization Last 60 sec',
        xaxis_title='CPU Cores',
        yaxis_title='Utilization (%)',
        yaxis=dict(range=[0,100]),
        template='plotly_dark'
    )

    #Memory and network Graph
    memory_network_fig = go.Figure()
    memory_network_fig.add_trace(go.Indicator(
        mode='gauge+number',
        value=data.get('percentage_memory_cached', 0) * 1e2,
        title={'text': 'Memory Cached (%)'},
        gauge={'axis': {'range': [0,100]}}
    ))
    memory_network_fig.add_trace(go.Indicator(
        mode='gauge+number',
        value=data.get('percentage_network_egress', 0) * 1e2,
        title={'text': 'Network Egress (%)'},
        gauge={'axis': {'range': [0,100]}}
    ))
    memory_network_fig.update_layout(
        title='Memory and Network Metrics',
        template='plotly_dark'
    )

    return cpu_fig, memory_network_fig


#Run Server
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)