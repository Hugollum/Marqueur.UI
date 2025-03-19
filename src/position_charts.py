import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from PIL import Image

from util.style import team_colors, image_sizing_ratio


def create_fig(df, x_column='total_points', position=None, selected_poolers=None):
    # Filter data for max value_dt
    df["value_dt"] = pd.to_datetime(df["value_dt"])
    max_value_dt = df["value_dt"].max()
    df = df[df["value_dt"] == max_value_dt]
    df = df.drop(columns=["value_dt"])

    if position is not None:
        df = df[df['position'] == position]

    df = df.groupby(['pooler_name', 'pooler_team'])[x_column].sum().reset_index()
    median = df[x_column].median()
    avg = df[x_column].mean()
    std = df[x_column].std()
    df['x'] = df[x_column]-median
    largest_gap = np.ceil(abs(df['x']).max() / 15) * 15
    df = df[['pooler_name', 'pooler_team', 'x']]

    s = (df['x'].max() - df['x'].min()) * 0.1
    x_range = [-largest_gap*1.1, largest_gap*1.1]
    df['y'] = 0
    y_range = [-1,1]

    if selected_poolers:
        df['selected'] = df['pooler_name'].isin(selected_poolers)
    else:
        df['selected'] = True

    fig_width = 800
    fig_height = 60
    layout = Layout(
        plot_bgcolor='rgba(255,255,255,1)',
        width=fig_width,
        height=fig_height)
    fig = go.Figure(layout=layout)

    sizex, sizey = image_sizing_ratio(30.0, fig_width, fig_height, x_range, y_range)
    sizey + 1

    for x_vline, value in [(largest_gap*i/3, largest_gap*i/3) for i in [-3, -2, -1, 0, 1, 2, 3]]:

        fig.add_annotation(x=x_vline, y=-0.85, text=(f"{int(value):+}" if value != 0 else "0"),
            showarrow=False,
            opacity=1,
        )

    # Loop over each unique pooler_name to generate a cubic spline curve
    for i, r in df.sort_values(['selected', 'y'], ascending=True).iterrows():
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


        fig.add_layout_image(
            dict(
                source=team_logo,  # Replace with your image URL
                x=df_pooler['x'].iloc[0],
                y=df_pooler['y'].iloc[0],
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
    fig.update_layout(
      showlegend=False,
      margin=dict(t=0, l=0, b=0, r=0),
      xaxis=dict(visible=True, showticklabels=False, range=x_range, fixedrange=True),
      yaxis=dict(visible=True, showticklabels=False, showgrid=False, fixedrange=True, side="right", range=y_range)
    )

    return fig