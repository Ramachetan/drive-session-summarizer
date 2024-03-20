from fastapi import FastAPI, HTTPException
from typing import Dict
import pandas as pd
from ast import literal_eval
import vertexai
from app import game
from stats import aggregate_statistics
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
    player_id: str

import logging

logging.basicConfig(level=logging.INFO)


@app.post("/generate_summary/")
async def generate_summary_endpoint(player: Player) -> Dict:
    player_id = str(player.player_id)
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
            f"""{summary}\n\n Above are the statistics for the vehicle with player_id: {player_id}, Generate a user-friendly summary and insights from the vehicle performance statistics obtained from a BeamNG.drive simulation driven by the player. The data reflects various performance metrics recorded on an automation test track. Given the statistics, provide insights and recommendations for the player to improve their driving skills and vehicle performance. The user-friendly summary should be in a conversational format and should be easy to understand for the player. Round off the numbers to 2 decimal places use imperial units\n""",
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0,
                "top_p": 1
            },
            stream=False,
        )

        return {"generated_text": responses.text, "player_id": player_id}

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def multiturn_generate_content(chat_message: ChatMessage):
    message = chat_message.message
    player_id = chat_message.player_id
    message = chat_message.message
    response = get_response_from_model(message, player_id)
    return {"response": response}



# To run the server, execute the following command: uvicorn api:app --reload