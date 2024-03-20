import time
from google.cloud import bigquery
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import vertexai



def get_response_from_model(prompt, player_id = "player1"):
    
    list_datasets_func = FunctionDeclaration(
        name="list_datasets",
        description="Get a list of datasets that will help answer the user's question",
        parameters={
            "type": "object",
            "properties": {},
        },
    )

    list_tables_func = FunctionDeclaration(
        name="list_tables",
        description="List tables in a dataset that will help answer the user's question",
        parameters={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "Fully qualified ID of the dataset to fetch tables from. Always use the fully qualified dataset and table names.",
                }
            },
            "required": [
                "dataset_id",
            ],
        },
    )

    get_table_func = FunctionDeclaration(
        name="get_table",
        description="Get information about a table, including the description, schema, and number of rows that will help answer the user's question. Always use the fully qualified dataset and table names.",
        parameters={
            "type": "object",
            "properties": {
                "table_id": {
                    "type": "string",
                    "description": "Fully qualified ID of the table to get information about",
                }
            },
            "required": [
                "query",
            ],
        },
    )

    sql_query_func = FunctionDeclaration(
        name="sql_query",
        description="Get information from data in BigQuery using SQL queries",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a BigQuery dataset and table. In the SQL query, always use the fully qualified dataset and table names.",
                }
            },
            "required": [
                "query",
            ],
        },
    )

    sql_query_tool = Tool(
        function_declarations=[
            # list_datasets_func,
            # list_tables_func,
            # get_table_func,
            sql_query_func,
        ],
    )

    vertexai.init(project="fresh-span-400217", location="us-central1") 

    model = GenerativeModel(
        "gemini-1.0-pro",
        generation_config={"temperature": 0},
        tools=[sql_query_tool],
    )

    model = GenerativeModel(
        "gemini-1.0-pro",
        generation_config={"temperature": 0.4, "max_output_tokens":8192 },
        tools=[sql_query_tool],
    )
   
    client = bigquery.Client()
    chat = model.start_chat()
    final_prompt = f"""
        User Question: {prompt} \n\n
        \n\nThe answer to the above question is in this table: \n\n
        \n\nfresh-span-400217.simulated_vehicle_data.{player_id} \n\n
        The table records the statistics for the vehicle insights from the vehicle performance statistics obtained from a BeamNG.drive simulation driven by the player. The data reflects various performance metrics recorded on an automation test track. The data is recorded over a period of 30 seconds.
        There are 15 columns in the table. \n\n
        'Time' (FLOAT): The timestamp of the recorded data, measured in seconds. \n\n
        'accXSmooth' (FLOAT): Smoothed acceleration in the X-direction (lateral), measured in m/s². \n\n
        'accYSmooth' (FLOAT): Smoothed acceleration in the Y-direction (longitudinal), measured in m/s². \n\n
        'accZSmooth' (FLOAT): Smoothed acceleration in the Z-direction (vertical), measured in m/s². \n\n
        'brake' (FLOAT): The brake pedal position, ranging from 0 (not pressed) to 1 (fully pressed). \n\n
        'fuel' (FLOAT): The fuel level as a fraction of the tank capacity, ranging from 0 (empty) to 1 (full). \n\n
        'gear' (FLOAT): The current gear of the vehicle, with possible values including (but not limited to) 1 for first gear, 2 for second gear, etc. \n\n
        'horn' (FLOAT): The state of the horn, with 0 indicating it is not being used and 1 indicating it is being used. \n\n
        'oil_temperature' (FLOAT): The temperature of the oil in the vehicle, measured in degrees Celsius. \n\n
        'part_damage' (STRING): A list of parts that have sustained damage, represented as a list of strings (this could be empty if no parts are damaged). always look at the last row to see the list of the damaged parts. \n\n
        'rpm' (FLOAT): The revolutions per minute of the vehicle's engine. \n\n
        'steering' (FLOAT): The steering wheel position, with positive values indicating right turns and negative values indicating left turns. \n\n
        'throttle' (FLOAT): The throttle position, ranging from 0 (not pressed) to 1 (fully pressed). \n\n
        'water_temperature' (FLOAT): The temperature of the water in the vehicle, measured in degrees Celsius. \n\n
        'wheelspeed' (FLOAT): The speed of the vehicle's wheels, measured in km/h. \n\n
        
        Use the sql_query function to query the table and get the information you need to answer the question. Think Step by Step, understand the user question clearly, write a SQL query to get the information you need, and then use the sql_query function to get the information.         
        """

    response = chat.send_message(final_prompt)
    response = response.candidates[0].content.parts[0]

    print(response)

    api_requests_and_responses = []
    backend_details = ""

    function_calling_in_process = True
    while function_calling_in_process:
        try:
            params = {}
            for key, value in response.function_call.args.items():
                params[key] = value

            print(response.function_call.name)
            print(params)

            if response.function_call.name == "sql_query":

                query_job = client.query(params["query"])
                api_response = query_job.result()
                api_response = str([row for row in api_response])
                api_requests_and_responses.append(
                    [response.function_call.name, params, api_response]
                )

            print(api_response)

            response = chat.send_message(
                Part.from_function_response(
                    name=response.function_call.name,
                    response={
                        "content": api_response,
                    },
                ),
            )
            response = response.candidates[0].content.parts[0]

            backend_details += "- Function call:\n"
            backend_details += (
                "   - Function name: ```"
                + str(api_requests_and_responses[-1][0])
                + "```"
            )
            backend_details += "\n\n"
            backend_details += (
                "   - Function parameters: ```"
                + str(api_requests_and_responses[-1][1])
                + "```"
            )
            backend_details += "\n\n"
            backend_details += (
                "   - API response: ```"
                + str(api_requests_and_responses[-1][2])
                + "```"
            )
            backend_details += "\n\n"
        except AttributeError:
            function_calling_in_process = False
    client.close()

    time.sleep(3)

    full_response = response.text
    return full_response

# # # Example usage
# prompt = "list all datasets"
# response = get_response_from_model(prompt)
# print(response)
