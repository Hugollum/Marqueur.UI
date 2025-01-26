import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

def create_plot(data, data_point=None):
    column = 'data'
    data = {column: data}  # Skewed distribution
    df = pd.DataFrame(data)

    # Kernel Density Estimate (KDE) for smoothing the distribution
    kde = gaussian_kde(df[column])
    x_vals = np.linspace(df[column].min(), df[column].max(), 500)
    y_vals = kde(x_vals)

    # Create the Plotly figure
    fig = go.Figure()

    # Add the KDE line (smoothed curve)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        line=dict(color='black', width=3),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[data_point, data_point],
        y=[min(y_vals), max(y_vals)],
        mode='lines',
        line=dict(color='black', width=2, dash='dash'),
        showlegend=False
    ))

    # Add a label for the custom x value
    fig.add_trace(go.Scatter(
        x=[data_point],
        y=[max(y_vals) * 1.03],  # Position the label 80% up the y-axis for visibility
        text=[f"{data_point}"],
        mode='text',
        textfont=dict(color='black', size=20),
        showlegend=False
    ))

    # Update layout for a minimalist look
    fig.update_layout(
        xaxis=dict(showline=False, showgrid=False, zeroline=False, title='', visible=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False, title='', visible=False),
        template='plotly_white',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig.show()
    return fig
