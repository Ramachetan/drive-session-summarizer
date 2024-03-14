from fastapi import FastAPI, HTTPException
from typing import Dict
import pandas as pd
from ast import literal_eval
import vertexai
from app import game
from chat import get_response_from_model
from vertexai.preview.generative_models import GenerativeModel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Player(BaseModel):
    player_id: str
    
class ChatMessage(BaseModel):
    message: str

import logging

logging.basicConfig(level=logging.INFO)


@app.post("/generate_summary/")
async def generate_summary_endpoint(player: Player) -> Dict:
    player_id = player.player_id
    try:
        # Initialize Vertex AI
        vertexai.init(project="fresh-span-400217", location="us-central1") 
        model = GenerativeModel("gemini-1.0-pro-001")
        
        logging.info(f"Calling game function with player_id: {player_id}")
        # game(player_id)
        
        # Load data
        logging.info(f"Loading CSV file for player_id: {player_id}")
        data = pd.read_csv(f'telematics/{player_id}_vehicle_data.csv')

        logging.info("Aggregating statistics")
        summary = aggregate_statistics(data)

        # Generate content
        logging.info("Generating content")
        responses = model.generate_content(
            f"""{summary}\n\n Above are the statistics for the vehicle with player_id: {player_id}, Generate a user-friendly summary and insights from the vehicle performance statistics obtained from a BeamNG.drive simulation driven by the player. The data reflects various performance metrics recorded on an automation test track. Given the statistics, provide insights and recommendations for the player to improve their driving skills and vehicle performance. The user-friendly summary should be in a conversational format and should be easy to understand for the player. 

            \n""",
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0,
                "top_p": 1
            },
            stream=False,
        )

        return {"generated_text": responses.text}

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
def multiturn_generate_content(chat_message: ChatMessage):
    message = chat_message.message
    response = get_response_from_model(message)
    return {"response": response}

def load_vehicle_data(player_id):
    data = pd.read_csv(f'telematics/{player_id}_vehicle_data.csv')
    return data

def compute_brake_usage(data):
    data['brake_change'] = data['brake'].diff()
    brake_starts_count = (data['brake_change'] == 1).sum()
    brake_average = data['brake'].mean()
    return brake_starts_count, brake_average

def compute_gear_changes(data):
    gears_used = data['gear'].unique()
    gear_changes = data[data['gear'].shift() != data['gear']]
    gear_change_details = gear_changes[['Time', 'gear']].values.tolist()
    return list(gears_used), gear_change_details

def compute_part_damage(data):
    last_part_damage = literal_eval(data['part_damage'].iloc[-1])
    return last_part_damage

def aggregate_statistics(data):
    total_time_secs = data['Time'].iloc[-1]
    accX_stats, accY_stats, accZ_stats = data['accXSmooth'].mean(), data['accYSmooth'].mean(), data['accZSmooth'].mean()
    brake_starts_count, brake_average = compute_brake_usage(data)
    fuel_start, fuel_end = data['fuel'].iloc[0], data['fuel'].iloc[-1]
    gears_used, gear_change_details = compute_gear_changes(data)
    oil_temp_stats = data['oil_temperature'].agg(['min', 'max', 'mean']).to_dict()
    last_part_damage = compute_part_damage(data)
    rpm_stats = data['rpm'].agg(['min', 'max', 'mean']).to_dict()
    steering_changes = data['steering'].diff().abs().sum()
    throttle_stats = data['throttle'].agg(['min', 'max', 'mean']).to_dict()
    water_temp_stats = data['water_temperature'].agg(['min', 'max', 'mean']).to_dict()
    wheel_speed_stats = data['wheelspeed'].agg(['min', 'max', 'mean']).to_dict()
    horn_usage_count = data['horn'].sum()

    summary = {
        "Total Time (secs)": total_time_secs,
        "Acceleration X (mean)": accX_stats,
        "Acceleration Y (mean)": accY_stats,
        "Acceleration Z (mean)": accZ_stats,
        "Brake Usage Count": brake_starts_count,
        "Brake Average": brake_average,
        "Fuel Start": fuel_start,
        "Fuel End": fuel_end,
        "Gears Used": gears_used,
        "Gear Change Details": gear_change_details,
        "Oil Temperature Stats": oil_temp_stats,
        "Part Damage": last_part_damage,
        "RPM Stats": rpm_stats,
        "Steering Changes": steering_changes,
        "Throttle Stats": throttle_stats,
        "Water Temperature Stats": water_temp_stats,
        "Wheel Speed Stats": wheel_speed_stats,
        "Horn Usage Count": horn_usage_count,
    }

    return summary


# To run the server, execute the following command: uvicorn api:app --reload