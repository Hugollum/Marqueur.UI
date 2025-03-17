import requests
import datetime as dt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from PIL import Image

from util.style import team_colors, image_sizing_ratio


def rounded_rectangle(x, y, width, height, radius, resolution=20):

    endpoint = "https://api-web.nhle.com/v1/playoff-series/carousel/20242025/"
    response = requests.get(endpoint)
    data = response.json()

    """Generate x, y coordinates for a perfectly rounded rectangle in Plotly."""
    left_x = x - width / 2
    right_x = x + width / 2
    top_y = y + height / 2
    bottom_y = y - height / 2

    # Ensure radius is not too large
    radius = min(radius, min(width, height) / 2)

    # Quarter-circle angles
    angles = np.linspace(0, np.pi / 2, resolution)

    # Define the four rounded corners correctly
    top_right = [(right_x - radius + radius * np.cos(a), top_y - radius + radius * np.sin(a)) for a in reversed(angles)]
    bottom_right = [
        (right_x - radius + radius * np.cos(a + 3 * np.pi / 2), bottom_y + radius + radius * np.sin(a + 3 * np.pi / 2))
        for a in reversed(angles)]
    bottom_left = [(left_x + radius + radius * np.cos(a + np.pi), bottom_y + radius + radius * np.sin(a + np.pi)) for a
                   in reversed(angles)]
    top_left = [(left_x + radius + radius * np.cos(a + np.pi / 2), top_y - radius + radius * np.sin(a + np.pi / 2)) for
                a in reversed(angles)]

    # Define straight edges
    top_edge = [(left_x + radius, top_y), (right_x - radius, top_y)]
    right_edge = [(right_x, top_y - radius), (right_x, bottom_y + radius)]
    bottom_edge = [(right_x - radius, bottom_y), (left_x + radius, bottom_y)]
    left_edge = [(left_x, bottom_y + radius), (left_x, top_y - radius)]

    # Combine all segments correctly
    points = top_edge + top_right + right_edge + bottom_right + bottom_edge + bottom_left + left_edge + top_left + [
        top_edge[0]]

    return zip(*points)  # Separate x and y coordinates


def create_fig():
    x_range = [-3.5, 3.5]
    y_range = [-2.5, 2.5]
    width, height = 0.8, 0.7
    radius = 0.025

    coordinate = [
        (-3.0, -1.5), (-3.0, -0.5),
        (-2.0, -1),
        (-1.35, 0.0),
        (0.0, 0.0)
    ]

    fig_width = 800
    fig_height = 500
    layout = Layout(
        plot_bgcolor='rgba(255,255,255,1)',
        width=fig_width,
        height=fig_height)
    fig = go.Figure(layout=layout)
    sizex, sizey = image_sizing_ratio(27, fig_width, fig_height, x_range, y_range)

    a=0.8

    # Generate mirrored points
    mirrored_coordinates = set()

    for x, y in coordinate:
        mirrored_coordinates.add((x, y))    # Original (Quadrant III)
        mirrored_coordinates.add((-x, y))   # Mirrored over Y-axis (Quadrant IV)
        mirrored_coordinates.add((x, -y))   # Mirrored over X-axis (Quadrant II)
        mirrored_coordinates.add((-x, -y))  # Mirrored over both axes (Quadrant I)

    # Convert set to list and sort based on given criteria
    sorted_coordinates = sorted(
        mirrored_coordinates,
        key=lambda p: (-abs(p[0]), -p[0], -p[1])  # Sort by abs(x) ↓, sign(x) ↓, y ↓
    )

    fig.add_layout_image(
        dict(
            source=Image.open("assets/img/nhl/STCUP.png"),  # Replace with your image URL
            x=0,
            y=height * 1.25,
            xref="x",  # Use the x-axis for reference
            yref="y",  # Use the y-axis for reference
            xanchor="center",  # Center the image horizontally
            yanchor="middle",  # Center the image vertically
            sizex=sizex*3,  # Image width in data coordinates
            sizey=sizey*3,  # Image height in data coordinates
            opacity=a  # Set image transparency
        )
    )

    fig.add_layout_image(
        dict(
            source=Image.open("assets/img/nhl/EC.png"),  # Replace with your image URL
            x=1.35/2,
            y=0,
            xref="x",  # Use the x-axis for reference
            yref="y",  # Use the y-axis for reference
            xanchor="center",  # Center the image horizontally
            yanchor="middle",  # Center the image vertically
            sizex=sizex*1.7,  # Image width in data coordinates
            sizey=sizey*1.7,  # Image height in data coordinates
            opacity=a  # Set image transparency
        )
    )

    fig.add_layout_image(
        dict(
            source=Image.open("assets/img/nhl/WC.png"),  # Replace with your image URL
            x=-1.35/2,
            y=0,
            xref="x",  # Use the x-axis for reference
            yref="y",  # Use the y-axis for reference
            xanchor="center",  # Center the image horizontally
            yanchor="middle",  # Center the image vertically
            sizex=sizex*1.7,  # Image width in data coordinates
            sizey=sizey*1.7,  # Image height in data coordinates
            opacity=a  # Set image transparency
        )
    )

    for i in range(len(sorted_coordinates)):
        x, y = sorted_coordinates[i]
        x_vals, y_vals = rounded_rectangle(x, y, width, height, radius)
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', fill="toself",
                                 line=dict(color="rgba(230, 234, 241, 1)", width=1)))
        fig.add_trace(go.Scatter(x=[x - width * 0.45, x + width * 0.45], y=[y, y], mode='lines', line=dict(color="rgba(230, 234, 241, 1)", width=1)))


    i=0
    for round in data['rounds']:
        for serie in round['series']:
            for seed, sign in [('topSeed', 1), ('bottomSeed', -1)]:
                x, y = sorted_coordinates[i]
                team_id = serie.get(seed, {}).get('id', 0)
                team = serie.get(seed, {}).get('abbrev')
                team_logo = Image.open(f"assets/img/teams/{team}.png")
                team_color = team_colors[team]

                if team_id == serie.get('winningTeamId', team_id):
                    a = 0.8
                elif team_id == serie.get('losingTeamId'):
                    a = 0.3
                color = f"rgba({','.join([str(c) for c in team_color.primary.rgb])}, {str(a)})"
                wins = serie.get(seed, {}).get('wins')
                fig.add_layout_image(
                    dict(
                        source=team_logo,  # Replace with your image URL
                        x=x - (width/4),
                        y=y + (height/4 * sign),
                        xref="x",  # Use the x-axis for reference
                        yref="y",  # Use the y-axis for reference
                        xanchor="center",  # Center the image horizontally
                        yanchor="middle",  # Center the image vertically
                        sizex=sizex,  # Image width in data coordinates
                        sizey=sizey,  # Image height in data coordinates
                        opacity=a  # Set image transparency
                    )
                )
                fig.add_annotation(
                    x=x + (width/4),
                    y=y + (height/4 * sign),
                    text=str(wins),
                    showarrow=False,
                    font=dict(
                        family="Impact",
                        size=18,
                        color="#444444"
                    ),
                    opacity=a,
                )

            i += 1

    # Update layout
    fig.update_layout(showlegend=False,
                      margin=dict(t=0, l=0, b=0, r=0),
                      xaxis=dict(visible=True, showgrid=False, zeroline=False, range=x_range, tickangle=30, fixedrange=True, showticklabels=False),  # Remove x-axis grid and labels
                      yaxis=dict(visible=True, showgrid=False, zeroline=False, range=y_range, tickangle=30, fixedrange=True, showticklabels=False) # Keep y-axis grid lines
    )

    return fig