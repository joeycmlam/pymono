"""

Sample bot that demonstrates how to use OpenAI function calling with the Poe API.

"""
from __future__ import annotations

import json
from typing import AsyncIterable

import fastapi_poe as fp
from modal import Image, Stub, asgi_app


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    #with open('/root/weather_data.json') as json_file:
    #    weather_data = json.load(json_file)

    weather_data = {
    "weather": [
        {
            "location": "Tokyo",
            "temperature": "-10",
            "unit": "fahrenheit"
        },
        {
            "location": "San Francisco",
            "temperature": "72",
            "unit": "fahrenheit"
        },
        {
            "location": "Paris",
            "temperature": "22",
            "unit": "fahrenheit"
        }]
    }
    location = location.title()  # Convert to title case to match the keys in the JSON file



    # Find the weather data for the requested location
    for weather in weather_data['weather']:
        if weather['location'] == location:
            if unit != weather['unit']:
                # Convert the temperature to the requested unit
                # This is a placeholder, replace with your actual conversion logic
                weather['temperature'] = weather['temperature']
                weather['unit'] = unit
            return json.dumps(weather)

    # If the location was not found in the data, return unknown
    return json.dumps({"location": location, "temperature": "unknown"})


tools_executables = [get_current_weather]

tools_dict_list = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
tools = [fp.ToolDefinition(**tools_dict) for tools_dict in tools_dict_list]


class GPT35FunctionCallingBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        async for msg in fp.stream_request(
            request,
            "GPT-3.5-Turbo",
            request.access_key,
            tools=tools,
            tool_executables=tools_executables,
        ):
            yield msg

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"GPT-3.5-Turbo": 2})


REQUIREMENTS = ["fastapi-poe==0.0.25"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
stub = Stub("function-calling-poe")


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    bot = GPT35FunctionCallingBot()
    # Optionally, provide your Poe access key here:
    # 1. You can go to https://poe.com/create_bot?server=1 to generate an access key.
    # 2. We strongly recommend using a key for a production bot to prevent abuse,
    # but the starter examples disable the key check for convenience.
    # 3. You can also store your access key on modal.com and retrieve it in this function
    # by following the instructions at: https://modal.com/docs/guide/secrets
    # POE_ACCESS_KEY = ""
    # app = make_app(bot, access_key=POE_ACCESS_KEY)
    app = fp.make_app(bot, allow_without_key=True)
    return app
