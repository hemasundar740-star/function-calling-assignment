
from openai import OpenAI
import json

client = OpenAI()

# Predefined city temperatures
def get_temperature(city):
    temperatures = {
        "Hyderabad": 32,
        "Chennai": 35,
        "Delhi": 30,
        "Mumbai": 31
    }

    return temperatures.get(city.title(), "Temperature data not available")

# Tool definition
tools = [
    {
        "type": "function",
        "name": "get_temperature",
        "description": "Get the temperature of a city in Celsius",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        },
        "strict": True
    }
]

# Ask the user
question = input("Ask about a city's temperature: ")

response = client.responses.create(
    model="gpt-4o-mini",
    input=question,
    tools=tools
)

# Execute the requested function
tool_outputs = []

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)

        result = get_temperature(args["city"])

        tool_outputs.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({"temperature": result})
        })

# Send the result back to the LLM
if tool_outputs:
    final_response = client.responses.create(
        model="gpt-4o-mini",
        previous_response_id=response.id,
        input=tool_outputs,
        tools=tools
    )
    print(final_response.output_text)
else:
    print(response.output_text)
