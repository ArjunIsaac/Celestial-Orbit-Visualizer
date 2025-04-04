
import dash
from dash import dcc, html, Input, Output
import numpy as np
import plotly.graph_objects as go
from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit

# Initialize Dash app
app = dash.Dash(__name__)

# Default orbit parameters
default_eccentricity = 0.1
default_inclination = 45  # degrees
default_sma = 7078  # km (Earth radius + 700km altitude)

# Create initial orbit
def create_orbit(sma, ecc, inc):
    return Orbit.from_classical(
        Earth,
        a=sma * u.km,
        ecc=ecc * u.one,
        inc=inc * u.deg,
        raan=0 * u.deg,
        argp=0 * u.deg,
        nu=0 * u.deg
    )

# App layout
app.layout = html.Div([
    html.H1("Satellite Orbit Simulator", style={'textAlign': 'center'}),
    
    # Controls
    html.Div([
        # Semi-major axis slider
        html.Div([
            html.Label("Semi-major Axis (km)", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='sma-slider',
                min=7000,
                max=15000,
                step=500,
                value=default_sma,
                marks={i: str(i) for i in range(7000, 16000, 1000)},
                tooltip={"placement": "bottom"}
            )
        ], style={'width': '50%', 'padding': '20px'}),
        
        # Earth size slider
        html.Div([
            html.Label("Earth Size", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='earth-size-slider',
                min=5,
                max=30,
                step=1,
                value=15,
                marks={i: str(i) for i in range(5, 31, 5)}
            )
        ], style={'width': '30%', 'padding': '20px'}),
        
        # Satellite size slider
        html.Div([
            html.Label("Satellite Size", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='satellite-size-slider',
                min=2,
                max=12,
                step=1,
                value=6,
                marks={i: str(i) for i in range(2, 13, 2)}
            )
        ], style={'width': '30%', 'padding': '20px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap'}),
    
    # 3D Graph
    dcc.Graph(id='orbit-graph', style={'height': '800px'}),
    
    # Animation controls
    html.Div([
        html.Button('▶ Play', id='play-button', n_clicks=0),
        html.Button('❚❚ Pause', id='pause-button', n_clicks=0)
    ], style={'textAlign': 'center', 'padding': '10px'})
])

# Callback to update the orbit visualization
@app.callback(
    Output('orbit-graph', 'figure'),
    [Input('sma-slider', 'value'),
     Input('earth-size-slider', 'value'),
     Input('satellite-size-slider', 'value')]
)
def update_orbit(sma, earth_size, satellite_size):
    # Create orbit with current parameters
    orbit = create_orbit(sma, default_eccentricity, default_inclination)
    
    # Propagate positions
    period = orbit.period.to(u.s).value
    time_span = np.linspace(0, period, num=100) * u.s
    propagated_positions = [orbit.propagate(t).r for t in time_span]
    x_vals, y_vals, z_vals = zip(*[(pos[0].value, pos[1].value, pos[2].value) for pos in propagated_positions])
    
    # Create figure
    fig = go.Figure()
    
    # Add orbit path
    fig.add_trace(go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals,
        mode='lines',
        line=dict(width=2, color='red'),
        name='Orbit Path'
    ))
    
    # Add Earth
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=earth_size, color='blue'),
        name='Earth'
    ))
    
    # Add initial satellite position
    fig.add_trace(go.Scatter3d(
        x=[x_vals[0]], y=[y_vals[0]], z=[z_vals[0]],
        mode='markers',
        marker=dict(size=satellite_size, color='green'),
        name='Satellite'
    ))
    
    # Create animation frames
    frames = [
        go.Frame(
            data=[
                go.Scatter3d(x=x_vals, y=y_vals, z=z_vals, mode='lines'),
                go.Scatter3d(x=[0], y=[0], z=[0], mode='markers'),
                go.Scatter3d(
                    x=[x_vals[i]], 
                    y=[y_vals[i]], 
                    z=[z_vals[i]], 
                    mode='markers'
                )
            ],
            name=f"frame_{i}"
        ) for i in range(len(x_vals))
    ]
    
    fig.frames = frames
    
    # Update layout
    fig.update_layout(
        title=f"Elliptical Orbit (SMA: {sma} km, Ecc: {default_eccentricity}, Inc: {default_inclination}°)",
        scene=dict(
            xaxis_title="X (km)",
            yaxis_title="Y (km)",
            zaxis_title="Z (km)",
            aspectmode='data'
        ),
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "type": "buttons",
            "x": 0.1,
            "y": 0,
            "yanchor": "top"
        }]
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)