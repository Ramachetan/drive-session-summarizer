# import time
from google.cloud import bigquery
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool

# Function Declarations
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
                "description": "Fully qualified ID of the dataset to fetch tables from.",
            }
        },
        "required": ["dataset_id"],
    },
)

get_table_func = FunctionDeclaration(
    name="get_table",
    description="Get information about a table schema, and number of rows and etc. in a BigQuery table.",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified ID of the table to get information about",
            }
        },
        "required": ["table_id"],
    },
)

sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Execute a SQL query to get information from a BigQuery dataset.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute.",
            }
        },
        "required": ["query"],
    },
)

sql_query_tool = Tool(
    function_declarations=[
        list_datasets_func,
        list_tables_func,
        get_table_func,
        sql_query_func,
    ],
)

model = GenerativeModel(
    "gemini-1.0-pro",
    generation_config={"temperature": 0},
    tools=[sql_query_tool],
)

def get_response_from_model(prompt):
    client = bigquery.Client()
    chat = model.start_chat()
    prompt += """
        Use your intelligence use the tools you have access to answer the user question to answer the user's question. \n
        """

    response = chat.send_message(prompt)
    response = response.candidates[0].content.parts[0]

    function_calling_in_process = True
    while function_calling_in_process:
        try:
            params = {key: value for key, value in response.function_call.args.items()}

            if response.function_call.name == "list_datasets":
                api_response = client.list_datasets()
                api_response = [dataset.dataset_id for dataset in api_response]

            elif response.function_call.name == "list_tables":
                api_response = client.list_tables(params["dataset_id"])
                api_response = [table.table_id for table in api_response]

            elif response.function_call.name == "get_table":
                api_response = client.get_table(params["table_id"])
                api_response = api_response.to_api_repr()

            elif response.function_call.name == "sql_query":
                job_config = bigquery.QueryJobConfig(maximum_bytes_billed=100000000)
                query_job = client.query(params["query"], job_config=job_config)
                api_response = query_job.result()
                api_response = [row for row in api_response]

            response = chat.send_message(
                Part.from_function_response(
                    name=response.function_call.name,
                    response={"content": str(api_response)},
                ),
            )
            response = response.candidates[0].content.parts[0]

        except AttributeError:
            function_calling_in_process = False

    full_response = response.text
    return full_response

# Example usage
# prompt = "list all datasets"
# response = get_response_from_model(prompt)
# print(response)
