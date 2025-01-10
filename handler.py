from typing import Any

def handler(input: dict, context: object) -> dict[str, Any]:
    print(f"Context: {context}")
    response = {
        "message": "Hello from handler",
        "received_input": input,
        "extra_info": "Any additional data can be added here"
    }

    return response