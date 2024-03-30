import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import ast
from chat import multiturn_generate_content


def fetch_data(player_id):
    url = "http://127.0.0.1:8000/generate_summary/"
    payload = {"player_id": player_id}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# import json

# def fetch_data(player_id):
#     with open('sample.json') as f:
#         data = json.load(f)
#     return data


def plot_line_graph(data, title, x_axis, y_axis):
    df = pd.DataFrame(data)
    fig = px.line(df, x=x_axis, y=y_axis, title=title)
    return fig


def plot_bar_graph(data, title, x_axis, y_axis):
    df = pd.DataFrame(data)
    fig = px.bar(df, x=x_axis, y=y_axis, title=title)
    return fig


def plot_pie_chart(data, title):
    data_for_df = [{'name': key, 'damage': value['damage']} for key, value in data.items()]
    df = pd.DataFrame(data_for_df)
    fig = px.pie(df, names='name', values='damage', title=title)
    return fig


if 'data' not in st.session_state:
    st.session_state.data = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Summary"
if 'selected_dtc_codes' not in st.session_state:
    st.session_state.selected_dtc_codes = []

st.set_page_config(
    page_title="Drive Summary Dashboard",
    layout="wide",
)

with st.sidebar:
    with st.form(key='my_form'):
        player_id = st.text_input("Enter Player ID:", "")
        submit_button = st.form_submit_button(label='Start Game')
        reset_button = st.form_submit_button("🧹")
    
if reset_button:
    st.session_state.data = None
    st.session_state.current_tab = "Summary"
    st.session_state.selected_dtc_codes = []

if submit_button or st.session_state.data:
    
    if not st.session_state.data or submit_button:
        with st.spinner('Fetching data...'):
            st.balloons()
            st.session_state.data = fetch_data(player_id)
    
    data = st.session_state.data
    if data:
        
        tab1, tab2, tab3 = st.tabs(["Summary","Graph", "DTC Codes"])

        
        with tab1:
            st.session_state.current_tab = "Summary"
            st.write("Summary")
            st.write(data["generated_text"])
            
            

        with tab2:
            st.session_state.current_tab = "Graph"
            col1, col2 = st.columns(2)
            if data.get("graphs"):
                for graph in data["graphs"]:
                    if graph["graph_type"] == "line":
                        fig = plot_line_graph(graph["data"], graph["title"], graph["x_axis"], graph["y_axis"])
                        col1.plotly_chart(fig)
                    elif graph["graph_type"] == "bar":
                        fig = plot_bar_graph(graph["data"], graph["title"], graph["x_axis"], graph["y_axis"])
                        col2.plotly_chart(fig)
                    elif graph["graph_type"] == "pie":
                        fig = plot_pie_chart(graph["data"], graph["title"])
                        col2.plotly_chart(fig)
                    elif graph["graph_type"] == "area":
                        df = pd.DataFrame(graph["data"])
                        fig = px.area(df, x=graph["x_axis"], y=graph["y_axis"], title=graph["title"])
                        col2.plotly_chart(fig)
            else:
                col2.write("No charts to display.")
            
        
        with tab3:
            st.session_state.current_tab = "DTC Codes"

            
            if data["dtc_response"]:
                with st.spinner('Loading DTC Codes...'):
                    dtc_codes = ast.literal_eval(data["dtc_codes"])  
                    selected_dtc_codes = st.multiselect('DTC Codes', dtc_codes, dtc_codes)
                    st.session_state.selected_dtc_codes = selected_dtc_codes
                st.write(data["dtc_response"])
            else:
                st.write("No data found for the given player ID.")
                
            prompt = st.text_input("Still have questions? Ask me anything!", key="chat_input")

            
            if prompt:
                with st.spinner('Processing...'):
                    response = multiturn_generate_content(prompt, data.get("dtc_response", ""), selected_dtc_codes)
                st.write(response)
            else:
                st.write("")
