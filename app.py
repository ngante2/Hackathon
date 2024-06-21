import openai
import psycopg2
from flask import Flask, request, jsonify, render_template
import assistant
import asyncio
openai.api_key = 'your-openai-api-key'

def get_response_from_openai(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def format_results_as_html_table(columns, results):
    table = '<table>'
    table += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in columns) + '</tr></thead>'
    table += '<tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
        for row in results
    ) + '</tbody>'
    table += '</table>'
    return table

def query_redshift(query, dropdown_value):
    user = "";
    password = "";
    if dropdown_value == "option1":
        user = 'cust-0dcb1576-5bb6-4612-aee9-9b8c1044aa8c';
        password='DemoPass1234'
    elif dropdown_value == 'option2':
        user = 'cust-0f761448-c0a7-46f7-b920-0d29d31b9fb5';
        password='DemoPass1234'
    else:
        user = 'cust-7335af4f-b47b-4097-868c-a87648c8fced';
        password='DemoPass1234'

    conn = psycopg2.connect(
        dbname='fivetran',
        user='bi_user',
        password='1oStyK$74ZJE',
        host='fivetran.ci0y2thfytw0.us-west-2.redshift.amazonaws.com',
        port='5439'
    )
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return colnames, results

def get_response_with_redshift(prompt, dropdown_value):
    if 'database query' in prompt:  # Example condition to trigger a Redshift query
        query = "SELECT * FROM ga4_floorforce.conversion_rates_raw LIMIT 5;"  # Example query
        columns, results = query_redshift(query, dropdown_value)
        return format_results_as_html_table(columns, results)
    else:
        return get_response_from_openai(prompt)
    
async def aiTool(thread):
    helper = await assistant.create_assistant()
    assistant_id = helper['id']

    thread = await assistant.create_thread(assistant_id, "How many page views did I see the week of June 10th?")
    thread_id = thread['id']

    await assistant.run_thread(thread_id, assistant_id)
    await assistant.stream_responses(thread_id, assistant_id)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message');
    dropdown_value = request.json.get('dropdown');
    response = get_response_with_redshift(user_input, dropdown_value)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
