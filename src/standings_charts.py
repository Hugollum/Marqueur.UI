import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from PIL import Image

from util.style import team_colors, image_sizing_ratio


def create_fig(df, conference, division, showticklabels=False):
    df = df.rename(columns={
        'points': 'x'
    })
    s = (df['x'].max() - df['x'].min()) * 0.1
    x_range = [df['x'].max() + s, df['x'].min() - s]
    df['y'] = 0
    y_range = [-1,1]

    fig_width = 800
    fig_height = 90 if showticklabels else 60
    layout = Layout(
        plot_bgcolor='rgba(255,255,255,1)',
        width=fig_width,
        height=fig_height)
    fig = go.Figure(layout=layout)

    sizex, sizey = image_sizing_ratio(30.0, fig_width, fig_height, x_range, y_range)
    sizey + 1


    df = df[df['conference'] == conference]
    x_line = (df[df['wildcard_standing'] <= 2]['x'].min() + df[df['wildcard_standing'] > 2]['x'].max()) / 2
    fig.add_vrect(x0=x_line, x1=x_range[0], fillcolor="#F0F2F6", line_width=0, layer="below")

    # Loop over each unique pooler_name to generate a cubic spline curve
    for i, r in df[df['division']==division].sort_values(['wildcard_standing'], ascending=False).iterrows():
        a = 0.8

        team = r['team']
        team_logo = Image.open(f"assets/img/teams/{team}.png")
        team_color = team_colors[team]

        fig.add_layout_image(
            dict(
                source=team_logo,  # Replace with your image URL
                x=r['x'],
                y=df['y'].iloc[0],
                xref="x",  # Use the x-axis for reference
                yref="y",  # Use the y-axis for reference
                xanchor="center",  # Center the image horizontally
                yanchor="middle",  # Center the image vertically
                sizex=sizex,  # Image width in data coordinates
                sizey=1,  # Image height in data coordinates
                opacity=a  # Set image transparency
            )
        )

    # Update layout
    fig.update_layout(margin=dict(t=0, l=0, b=0, r=0),
                      xaxis=dict(visible=True, showticklabels=showticklabels, range=x_range, fixedrange=True),
                      yaxis=dict(visible=True, showticklabels=False, showgrid=False, fixedrange=True, side="right", range=y_range)
    )
    return fig