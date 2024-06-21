import openai
import json
from datetime import datetime
from sqltools import SQLQueryToolEventHandler

# Configure your OpenAI API key
openai.api_key = "sk-ai-hackathon-gsJtmxRHihAEbkD3oM72T3BlbkFJsLD8OlkhwC899UJD2aIy"

current_date = datetime.now().isoformat()

schema = [
    {
        "schema_name": "ga4_floorforce",
        "table_name": "web_trends_mv",
        "description": "This is view is a summary of all metrics of interest and aggregated by retailer and calculated daily.",
        "fields": {
            "uuid": "Universal Retailer ID",
            "date": "Day the metric was counted",
            "sessions": "Sum of sessions",
            "users": "Sum of users",
            "pageviews": "Sum of pageviews",
            "avg_session_duration": "Average length of time for all sessions on the page",
            "bounce_rate": "Percentage of people that stay on the page and don’t submit data before leaving",
            "leads": "Lead count",
            "conversion_rate": "Goals (calls, chats, forms) divided by the number of sessions"
        }
    },
    {
        "schema_name": "ga4_floorforce",
        "table_name": "conversion_rates_raw",
        "description": "This view calculates daily total conversion rate and conversion rate by medium (chat, call, form).",
        "fields": {
            "uuid": "Universal Retailer ID",
            "date": "Date conversion was made",
            "call": "Conversion rate for call",
            "chat": "Conversion rate for chat",
            "form": "Conversion rate for form",
            "total": "Combined conversion rate for call, chat, and form"
        }
    },
    {
        "schema_name": "ga4_floorforce",
        "table_name": "top_pages",
        "description": "This view counts pageviews by page.",
        "fields": {
            "uuid": "Universal Retailer ID",
            "date": "Date that page was viewed",
            "page": "Page location that appears after the domain",
            "page_path": "Path of the page",
            "page_views": "Sum of pageviews for that page"
        }
    },
    {
        "schema_name": "ga4_floorforce",
        "table_name": "top_channels",
        "description": "This view counts sessions per channel group.",
        "fields": {
            "uuid": "Universal Retailer ID",
            "date": "Date session occurred",
            "channel group": "Medium for which the user found the site",
            "sessions": "Sum of sessions"
        }
    },
    {
        "schema_name": "ga4_floorforce",
        "table_name": "web_trends_daily",
        "description": "This view counts sessions, users, and pageviews daily.",
        "fields": {
            "uuid": "Universal Retailer ID",
            "date": "Date that page was viewed",
            "users": "Sum of users",
            "sessions": "Sum of sessions",
            "pageviews": "Sum of pageviews for that page"
        }
    }
]

assistant_instructions = """You are an assistant meant to help users gain insights into their data by writing SQL queries for them that fulfill their question.
Please inform the user if their query does not make sense before writing code.
Please write one valid SQL statement to fetch data to answer the user's question. Prefix all tables with their schema names. 
MAKE SURE EVERY QUERY IS FOR THE USER'S UUID. DO NOT FORGET TO INCLUDE THE UUID IN THE SQL QUERY. 
If possible respond only with SQL code. Be succinct."""

system_prompt = f"""
The current date is: {current_date}
This user's UUID is: 81d8595a-0e85-4afd-a399-204958879c84
The following is a JSON document containing schema information about tables in AWS Redshift:
{json.dumps(schema, indent=4)}
Please use this information to respond to the user's query.
"""

async def create_assistant():
    response = await openai.beta.assistants.create(
        model="gpt-4o",
        instructions=assistant_instructions,
        name="AI Hackathon Analytic Reporter Assistant",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "sql_query",
                    "description": "Run an SQL query and return the results as JSON.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schema_name": {
                                "type": "string",
                                "description": "The schema name that contains the table"
                            },
                            "table_name": {
                                "type": "string",
                                "description": "The table to run the SQL query on"
                            },
                            "sql": {
                                "type": "string",
                                "description": "The raw SQL to run"
                            }
                        },
                        "required": ["schema_name", "table_name", "sql"]
                    }
                }
            }
        ]
    )
    return response

async def create_thread(assistant_id, user_query):
    response = await openai.Thread.create(
        assistant_id=assistant_id,
        messages=[
            {
                "role": "user",
                "content": user_query
            }
        ]
    )
    return response

async def run_thread(thread_id, assistant_id):
    response = await openai.Thread.run(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions=system_prompt,
        tool_choice="required"
    )
    return response

async def stream_responses(thread_id, assistant_id):
    event_handler = SQLQueryToolEventHandler(openai)

    async for event in openai.Thread.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions=system_prompt,
        tool_choice="required"
    ):
        event_handler.on_event(event)

async def main():
    assistant = await create_assistant()
    assistant_id = assistant['id']

    thread = await create_thread(assistant_id, "How many page views did I see the week of June 10th?")
    thread_id = thread['id']

    await run_thread(thread_id, assistant_id)
    await stream_responses(thread_id, assistant_id)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
