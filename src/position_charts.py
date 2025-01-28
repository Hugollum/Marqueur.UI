import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from PIL import Image

from style import team_colors


def image_sizing_ratio(target_size, fig_width, fig_height, x_range, y_range):
    x_pixels_per_unit = fig_width / (x_range[1] - x_range[0])
    y_pixels_per_unit = fig_height / (y_range[1] - y_range[0])
    return target_size / x_pixels_per_unit, target_size / y_pixels_per_unit


def create_fig(df, x_column='total_points', position=None, selected_poolers=None, showticklabels=False):
    # Filter data for max value_dt
    df["value_dt"] = pd.to_datetime(df["value_dt"])
    max_value_dt = df["value_dt"].max()
    df = df[df["value_dt"] == max_value_dt]
    df = df.drop(columns=["value_dt"])

    if position is not None:
        df_grouped = df.groupby(['pooler_name', 'pooler_team', 'position'])[x_column].sum().reset_index()
        df = df_grouped[['pooler_name', 'pooler_team', 'position', x_column]]
    else:
        df_grouped = df.groupby(['pooler_name', 'pooler_team'])[x_column].sum().reset_index()
        df = df_grouped[['pooler_name', 'pooler_team', x_column]]

    df = df.rename(columns={
        x_column: 'x'
    })
    s = (df['x'].max() - df['x'].min()) * 0.1
    x_range = [df['x'].min() - s, df['x'].max() + s]
    df['y'] = 0
    y_range = [-1,1]

    if position is not None:
        df = df[df['position'] == position]

    if selected_poolers:
        df['selected'] = df['pooler_name'].isin(selected_poolers)
    else:
        df['selected'] = True

    fig_width = 800
    fig_height = 90 if showticklabels else 60
    layout = Layout(
        plot_bgcolor='rgba(255,255,255,1)',
        width=fig_width,
        height=fig_height)
    fig = go.Figure(layout=layout)

    sizex, sizey = image_sizing_ratio(25.0, fig_width, fig_height, x_range, y_range)
    sizey + 1

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
        color = f"rgba({','.join([str(c) for c in team_color.primary.rgb])}, {str(a)})"
        faded = f"rgba({','.join([str(c) for c in team_color.primary.rgb])}, 0.1)"

        fig.add_trace(go.Scatter(
            x=df_pooler['x'],
            y=df_pooler['y'],
            mode='markers',
            name="",
            marker=dict(
                color=faded,
                size=30,
                line=dict(color=color, width=2)
            ),
            hovertemplate = f"{pooler_name}: %{{x}}",
            hoverinfo='none'
        ))  # Set font color to match the marker

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
    fig.update_layout(        title=dict(
            text=position
        ),
                      showlegend=False,
                      margin=dict(t=0, l=0, b=0, r=0),
                      xaxis=dict(visible=True, showticklabels=showticklabels, range=x_range, fixedrange=True),
                      yaxis=dict(visible=True, showticklabels=False, showgrid=False, fixedrange=True, side="right", range=y_range)
    )

    return fig