
from openai import OpenAI
import json

client = OpenAI()

# Predefined employee leave balances
def get_employee_leave_balance(employee_id):
    leave_balances = {
        "101": 10,
        "102": 5,
        "103": 15
    }

    return leave_balances.get(str(employee_id), None)


# Check leave eligibility
def check_leave_eligibility(employee_id, requested_days):
    balance = get_employee_leave_balance(employee_id)

    if balance is None:
        return {
            "eligible": False,
            "message": "Employee ID not found"
        }

    if requested_days <= 0:
        return {
            "eligible": False,
            "message": "Requested days must be greater than zero",
            "available_days": balance
        }

    if requested_days <= balance:
        return {
            "eligible": True,
            "message": "Employee is eligible for leave",
            "available_days": balance
        }

    return {
        "eligible": False,
        "message": "Insufficient leave balance",
        "available_days": balance
    }


# Tool definitions
tools = [
    {
        "type": "function",
        "name": "get_employee_leave_balance",
        "description": "Get the available leave balance of an employee",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"}
            },
            "required": ["employee_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "check_leave_eligibility",
        "description": "Check whether an employee can take the requested leave days",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"},
                "requested_days": {"type": "integer"}
            },
            "required": ["employee_id", "requested_days"],
            "additionalProperties": False
        },
        "strict": True
    }
]

# Get user input
question = input(
    "Enter employee ID and requested leave details: "
)

response = client.responses.create(
    model="gpt-4o-mini",
    input=question,
    tools=tools
)

# Execute tool calls
tool_outputs = []

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)

        if item.name == "get_employee_leave_balance":
            result = get_employee_leave_balance(
                args["employee_id"]
            )

        elif item.name == "check_leave_eligibility":
            result = check_leave_eligibility(
                args["employee_id"],
                args["requested_days"]
            )

        else:
            continue

        tool_outputs.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result)
        })

# Send tool results back to the LLM
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
