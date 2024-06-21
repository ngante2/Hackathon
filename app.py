import openai
import psycopg2
from flask import Flask, request, jsonify, render_template

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

def query_redshift(query):
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
        columns, results = query_redshift(query)
        return format_results_as_html_table(columns, results)
    else:
        return get_response_from_openai(prompt)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message');
    dropdown_value = request.json.get('selectedValue');
    response = get_response_with_redshift(user_input, dropdown_value)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
