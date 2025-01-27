import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np


def create_donut_chart(data, title):
    # Prepare data for the donut chart
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    # Create the figure using Plotly
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title=title, showlegend=True)

    # Convert the entire figure to a dictionary format that can be serialized
    chart_data = fig.to_dict()

    return chart_data

def create_bar_chart(data, title):
    # Prepare data for the bar chart
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    
    # Create the figure using Plotly
    fig = go.Figure(data=[go.Bar(x=labels, y=values)])
    fig.update_layout(title=title, xaxis_title="Users", yaxis_title="Reservations")

    # Convert the entire figure to a dictionary format that can be serialized
    chart_data = fig.to_dict()

    return chart_data
