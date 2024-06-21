import asyncio
from pyee.asyncio import AsyncIOEventEmitter
import openai
import json
from datetime import datetime

class SQLQueryToolEventHandler(AsyncIOEventEmitter):
    def __init__(self, client):
        super().__init__()
        self.client = client

    async def on_event(self, event):
        try:
            print(json.dumps(event, indent=2))
            # Retrieve events that are denoted with 'requires_action'
            # since these will have our tool_calls
            if event.get('event') == 'thread.run.requires_action':
                await self.handle_requires_action(event)
        except Exception as error:
            print("Error handling event:", error)

    async def handle_requires_action(self, event):
        data = event.get('data')
        try:
            tool_calls = data.get('required_action', {}).get('submit_tool_outputs', {}).get('tool_calls', [])
            tool_outputs = [
                await self.handle_sql_query(event, tool_call)
                for tool_call in tool_calls
                if tool_call['function']['name'] == 'sql_query'
            ]
            # Submit all the tool outputs at the same time
            await self.submit_tool_outputs(tool_outputs, data['id'], data['thread_id'])
        except Exception as error:
            print("Error processing required action:", error)

    async def handle_sql_query(self, event, tool_call):
        example_output = {
            "isSuccess": True,
            "error": None,
            "output": "total_pageviews\n512"
        }
        return {
            "output": json.dumps(example_output),
            "tool_call_id": tool_call['id']
        }

    async def submit_tool_outputs(self, tool_outputs, run_id, thread_id):
        try:
            print(f"submitting: {tool_outputs}")
            async with self.client.beta.threads.runs.submit_tool_outputs_stream(
                    thread_id, run_id, {'tool_outputs': tool_outputs}) as stream:
                async for event in stream:
                    self.emit("event", event)
        except Exception as error:
            print("Error submitting tool outputs:", error)

# Example usage
async def main():
    client = openai.Client(api_key="sk-ai-hackathon-gsJtmxRHihAEbkD3oM72T3BlbkFJsLD8OlkhwC899UJD2aIy")
    handler = SQLQueryToolEventHandler(client)

    # Simulate receiving an event
    example_event = {
        "event": "thread.run.requires_action",
        "data": {
            "id": "example_run_id",
            "thread_id": "example_thread_id",
            "required_action": {
                "submit_tool_outputs": {
                    "tool_calls": [
                        {
                            "id": "example_tool_call_id",
                            "function": {
                                "name": "sql_query"
                            }
                        }
                    ]
                }
            }
        }
    }

    await handler.on_event(example_event)

if __name__ == '__main__':
    asyncio.run(main())
