import datetime as dt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from plotly.graph_objects import Layout
from PIL import Image

from style import team_colors


def create_fig(df, selected_poolers=None):
    df['value_dt'] = pd.to_datetime(df['value_dt'])
    df['day'] = (df['value_dt'] - dt.datetime(2024, 9, 30)).dt.days
    max_day = df['day'].max()
    df_grouped = df.groupby(['day', 'pooler_name', 'pooler_team'])['total_points'].sum().reset_index()
    df_grouped['normalized_points'] = df_grouped['total_points'] - df_grouped.groupby('day')['total_points'].transform('median') + df_grouped.groupby('day')['total_points'].transform('median').iloc[-1]
    starting_points = df_grouped.groupby('day')['total_points'].transform('median').iloc[-1]
    df = df_grouped[['pooler_name', 'pooler_team', 'day', 'total_points', 'normalized_points']]
    df = df.rename(columns={
        'day': 'x',
        'normalized_points': 'y'
    })
    if selected_poolers:
        df['selected'] = df['pooler_name'].isin(selected_poolers)
    else:
        df['selected'] = True

    # Create the plot
    layout = Layout(plot_bgcolor='rgba(255,255,255,1)')
    fig = go.Figure(layout=layout)



    # Loop over each unique pooler_name to generate a cubic spline curve
    for i, r in df[df['x']==max_day].sort_values(['selected', 'y'], ascending=True).iterrows():
        # Get data for the specific pooler_name
        pooler_name = r["pooler_name"]
        df_pooler = df[df['pooler_name'] == pooler_name]

        if r["selected"]:
            a = 0.8
        else:
            a = 0.1

        pooler_team = r['pooler_team']
        team_logo = Image.open(f"assets/img/teams/{pooler_team}.png")
        team_color = team_colors[pooler_team]
        color = f"rgba({','.join([str(c) for c in team_color.primary.rgb])}, {str(a)})"


        # Create the cubic spline interpolation
        cs = CubicSpline(df_pooler['x'], df_pooler['y'])

        # Generate smooth x values for the spline curve
        x_smooth = np.linspace(df_pooler['x'].min(), df_pooler['x'].max(), 500)
        y_smooth = cs(x_smooth)

        # Add the smooth cubic spline curve for the current pooler_name (no markers)
        fig.add_trace(go.Scatter(
            x=x_smooth,
            y=y_smooth,
            mode='lines',
            name=f'{pooler_name}',
            line=dict(color=color, dash='solid', width=5),
            hovertemplate=f'{pooler_name}'
        ))


        fig.add_trace(go.Scatter(x=[df_pooler['x'].iloc[-1]], y=[df_pooler['y'].iloc[-1]],
                                 mode='markers', name=f'{pooler_name}',
                                 marker=dict(color=color, size=30),
                                 hovertemplate=f'{pooler_name}: {int(df_pooler['y'].iloc[-1])}',
                                 hoverinfo='y'))  # Set font color to match the marker

        # Add the marker only at the last point for the current pooler_name
        fig.add_trace(go.Scatter(x=[df_pooler['x'].iloc[-1]], y=[df_pooler['y'].iloc[-1]],
                                 mode='markers', name=f'{pooler_name}',
                                 marker=dict(color=f"rgba(255,255,255, {str(a)})", size=27),
                                 hovertemplate=f'{pooler_name}: {int(df_pooler['y'].iloc[-1])}',
                                 hoverinfo='y'))  # Set font color to match the marker

        fig.add_layout_image(
            dict(
                source=team_logo,  # Replace with your image URL
                x=df_pooler['x'].iloc[-1],
                y=df_pooler['y'].iloc[-1],
                xref="x",  # Use the x-axis for reference
                yref="y",  # Use the y-axis for reference
                xanchor="center",  # Center the image horizontally
                yanchor="middle",  # Center the image vertically
                sizex=12,  # Image width in data coordinates
                sizey=12,  # Image height in data coordinates
                opacity=a  # Set image transparency
            )
        )

    fig.add_trace(go.Scatter(x=[0], y=[starting_points],
                             mode='markers',
                             marker=dict(color="rgba(255,255,255, 1)", size=5),
                             hoverinfo='none'))  # Set font color to match the marker

    # Update layout
    fig.update_layout(showlegend=False,
                      height=500,
                      width=800,
                      margin=dict(t=0, l=0, b=0, r=0),
                      xaxis=dict(visible=True, showgrid=False, title=dict(text="Season (days)"), fixedrange=True),  # Remove x-axis grid and labels
                      yaxis=dict(visible=True, fixedrange=True, side="right") # Keep y-axis grid lines
    )

    return fig
