import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models




def multiturn_generate_content(prompt, dtc_response, dtc_codes):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    }
    model = GenerativeModel("gemini-1.0-pro-001")
    chat = model.start_chat()
    chat.send_message(f"""{dtc_codes}\n\nBased on the above DTC codes, What could be the root cause of the problem? Also, provide the diagnostic steps and recommended fixes for the problem.""")
    chat.send_message(f"""{dtc_response}""", stream=False)
    response = chat.send_message(f"""{prompt}""", generation_config=config, stream=False)

    return response.text


