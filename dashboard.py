import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import ast

# Function to call the API and get the data
def fetch_data(player_id):
    url = "http://127.0.0.1:8000/generate_summary/"
    payload = {"player_id": player_id}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to plot line graph
def plot_line_graph(data, title, x_axis, y_axis):
    df = pd.DataFrame(data)
    fig = px.line(df, x=x_axis, y=y_axis, title=title)
    return fig

# Function to plot bar graph
def plot_bar_graph(data, title, x_axis, y_axis):
    df = pd.DataFrame(data)
    fig = px.bar(df, x=x_axis, y=y_axis, title=title)
    return fig

# Function to plot pie chart
def plot_pie_chart(data, title):
    data_for_df = [{'name': key, 'damage': value['damage']} for key, value in data.items()]
    df = pd.DataFrame(data_for_df)
    fig = px.pie(df, names='name', values='damage', title=title)
    return fig

# Streamlit UI
st.title('BeamNG.drive Session Summary')

player_id = st.text_input("Enter Player ID:", "")

if player_id:
    data = fetch_data(player_id)
    if data:
        tab1, tab2, tab3 = st.tabs(["Summary", "Charts", "DTC Codes"])
        
        # Tab for Generated Text
        with tab1:
            st.markdown("**Summary of Your Drive**")
            st.write(data["generated_text"])
        
        # Tab for Charts
        with tab2:
            # Check if there are any graphs to display
            if data.get("graphs"):
                for graph in data["graphs"]:
                    if graph["graph_type"] == "line":
                        fig = plot_line_graph(graph["data"], graph["title"], graph["x_axis"], graph["y_axis"])
                        st.plotly_chart(fig)
                    elif graph["graph_type"] == "bar":
                        fig = plot_bar_graph(graph["data"], graph["title"], graph["x_axis"], graph["y_axis"])
                        st.plotly_chart(fig)
                    elif graph["graph_type"] == "pie":
                        fig = plot_pie_chart(graph["data"], graph["title"])
                        st.plotly_chart(fig)
            else:
                st.write("No charts to display.")
        # Tab for DTC Response
        with tab3:
            if data["dtc_response"]:
                dtc_codes = ast.literal_eval(data["dtc_codes"])  
                options = st.multiselect(
                'DTC Codes',
                dtc_codes, dtc_codes)
                st.write(data["dtc_response"])
        
            
    else:
        st.write("No data found for the given player ID.")
