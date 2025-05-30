import datetime as dt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from plotly.graph_objects import Layout
from PIL import Image

from util.style import team_colors, image_sizing_ratio


def create_fig(df, selected_poolers=None):
    poolers = df[['pooler_name', 'pooler_team']].drop_duplicates()
    df = df[df['in_playoff']]
    df_grouped = df.groupby(['pooler_name', 'pooler_team']).agg(num_players=('player_name', 'count'), avg_points=('average_points', 'mean')).reset_index()
    df = df_grouped[['pooler_name', 'pooler_team', 'num_players', 'avg_points']]
    df = df.rename(columns={
        'avg_points': 'x',
        'num_players': 'y',
    })
    df = pd.merge(poolers, df, how='left', on=['pooler_name', 'pooler_team'])
    df['y'] = df['y'].fillna(0.35)
    df['x'] = df['x'].fillna(0.05)
    if selected_poolers:
        df['selected'] = df['pooler_name'].isin(selected_poolers)
    else:
        df['selected'] = True

    x_range = [0.0, 2.0]
    y_range = [0.0, 13.0]


    fig_width = 800
    fig_height = 400
    layout = Layout(
        plot_bgcolor='rgba(255,255,255,1)',
        width=fig_width,
        height=fig_height)
    fig = go.Figure(layout=layout)
    sizex, sizey = image_sizing_ratio(35, fig_width, fig_height, x_range, y_range)

    for i, r in df.sort_values(['selected', 'y', 'x'], ascending=True).iterrows():
        # Get data for the specific pooler_name
        pooler_name = r["pooler_name"]

        if r["selected"]:
            a = 0.8
        else:
            a = 0.1

        pooler_team = r['pooler_team']
        team_logo = Image.open(f"assets/img/teams/{pooler_team}.png")
        team_color = team_colors[pooler_team]
        color = f"rgba({','.join([str(c) for c in team_color.primary.rgb])}, {str(a)})"

        fig.add_layout_image(
            dict(
                source=team_logo,  # Replace with your image URL
                x=r['x'],
                y=r['y'],
                xref="x",  # Use the x-axis for reference
                yref="y",  # Use the y-axis for reference
                xanchor="center",  # Center the image horizontally
                yanchor="middle",  # Center the image vertically
                sizex=sizex,  # Image width in data coordinates
                sizey=sizey,  # Image height in data coordinates
                opacity=a  # Set image transparency
            )
        )

    # Define the starting value (M) and step size (steps) for x * y
    M = 0.5  # Starting value of x * y
    steps = 3  # Step size for incrementing x * y

    # Calculate the number of lines to be drawn based on the range
    num_lines = 10  # You can adjust this to your needs

    # Add decreasing diagonal grid lines where x * y = M + i * steps
    for i in range(num_lines):
        constant_value = M + i * steps
        epsilon = 1e-10

        # Calculate y-values for each x in the range for the grid line
        x_values_grid = np.linspace(x_range[0], x_range[1], 100)
        x_values_grid = np.where(x_values_grid == 0, epsilon, x_values_grid)
        y_values_grid = constant_value / x_values_grid

        # Add the grid line to the plot
        fig.add_trace(go.Scatter(
            x=x_values_grid,
            y=y_values_grid,
            mode="lines",
            line=dict(color="#E6EAF1", width=1)  # Style it like a grid line
        ))

    # Update layout
    fig.update_layout(showlegend=False,
                      margin=dict(t=0, l=0, b=0, r=0),
                      xaxis=dict(visible=True, showgrid=False, zeroline=False, range=x_range, tickangle=30, title=dict(text="Average Points"), tickformat=".1f", fixedrange=True),  # Remove x-axis grid and labels
                      yaxis=dict(visible=True, showgrid=False, zeroline=False, range=y_range, tickangle=30, title=dict(text="Player Count"), fixedrange=True) # Keep y-axis grid lines
    )

    return fig
