import numpy as np
import plotly.graph_objects as go
from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.orbit import propagate

# Define an elliptical orbit (700 km perigee, 0.1 eccentricity)
alt_perigee = 700 * u.km
eccentricity = 0.1  # Elliptical orbit (0 = circular, 0-1 = elliptical)
inclination = 45 * u.deg  # Inclined orbit for better 3D visualization
orbit = Orbit.from_classical(
    Earth,
    a=Earth.R + alt_perigee,  # Semi-major axis
    ecc=eccentricity * u.one,
    inc=inclination,
    raan=0 * u.deg,
    argp=0 * u.deg,
    nu=0 * u.deg
)

# Define propagation time span (1 orbit period, 100 points)
period = orbit.period.to(u.s).value
time_span = np.linspace(0, period, num=100) * u.s
propagated_positions = [orbit.propagate(t).r for t in time_span]

# Extract x, y, z coordinates
x_vals, y_vals, z_vals = zip(*[(pos[0].value, pos[1].value, pos[2].value) for pos in propagated_positions])

# Create a 3D plot with Plotly
fig = go.Figure()

# Initial sizes
earth_size = 15  # Increased for better visibility
satellite_size = 6

# Add the orbit trace (static)
fig.add_trace(go.Scatter3d(
    x=x_vals, y=y_vals, z=z_vals,
    mode='lines', line=dict(width=2, color='red'),
    name='Orbit Path'
))

# Add Earth as a reference (larger size)
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers',
    marker=dict(size=earth_size, color='blue'),
    name='Earth'
))

# Add initial satellite marker
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
            go.Scatter3d(
                x=x_vals, y=y_vals, z=z_vals,
                mode='lines', line=dict(width=2, color='red')
            ),
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                marker=dict(size=earth_size, color='blue')
            ),
            go.Scatter3d(
                x=[x_vals[i]], y=[y_vals[i]], z=[z_vals[i]],  
                mode='markers',
                marker=dict(size=satellite_size, color='green')
            )
        ],
        name=f"Frame {i}"
    ) for i in range(len(x_vals))
]

# Add frames to figure
fig.frames = frames

# Create size selection buttons for Earth
earth_size_buttons = []
for size in range(5, 31, 5):  # Earth sizes from 5 to 30
    earth_size_buttons.append(
        dict(
            method="update",
            args=[{"marker": [None, dict(size=size), None]}],  # Only update Earth
            label=str(size)
        )
    )

# Create size selection buttons for Satellite
satellite_size_buttons = []
for size in range(2, 13, 2):  # Satellite sizes from 2 to 12
    satellite_size_buttons.append(
        dict(
            method="update",
            args=[{"marker": [None, None, dict(size=size)]}],  # Only update Satellite
            label=str(size)
        )
    )

# Layout with animation controls and size selectors
fig.update_layout(
    title=f"Elliptical Orbit Simulation (e={eccentricity}, i={inclination.value}°)",
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)",
        aspectmode='data'  # Better proportions for elliptical orbit
    ),
    updatemenus=[
        # Animation controls
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "type": "buttons",
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        },
        # Earth size selector
        {
            "buttons": earth_size_buttons,
            "direction": "down",
            "showactive": True,
            "x": 0.1,
            "xanchor": "left",
            "y": 0.15,
            "yanchor": "top",
            "type": "dropdown"
        },
        # Satellite size selector
        {
            "buttons": satellite_size_buttons,
            "direction": "down",
            "showactive": True,
            "x": 0.1,
            "xanchor": "left",
            "y": 0.25,
            "yanchor": "top",
            "type": "dropdown"
        }
    ],
    annotations=[
        dict(text="Earth Size", x=0.1, xref="paper", y=0.1, yref="paper", showarrow=False),
        dict(text="Satellite Size", x=0.1, xref="paper", y=0.2, yref="paper", showarrow=False)
    ]
)

fig.show()