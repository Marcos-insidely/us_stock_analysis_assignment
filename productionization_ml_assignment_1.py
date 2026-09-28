from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np

from datetime import datetime, timedelta

app = FastAPI()
data = pd.read_csv('skin clinic campaign.csv')

def get_task_1(data):
    response_gender = data.groupby('Gender')['responded_bool'].mean().reset_index()
    response_gender['Response Rate (%)'] = response_gender['responded_bool'] * 100
    response_gender = response_gender[['Gender', 'Response Rate (%)']]
    return response_gender.to_dict(orient='records')

def get_task_2(data):
    response_age = data.groupby('AgeGroup')['responded_bool'].mean().reset_index()
    response_age['Response Rate (%)'] = response_age['responded_bool'] * 100
    response_age = response_age[['AgeGroup', 'Response Rate (%)']]
    return response_age.to_dict(orient='records')

def get_task_3(data):
    response_purchased = data.groupby('Purchase_Last_Quarter')['responded_bool'].mean().reset_index()
    response_purchased['Response Rate (%)'] = response_purchased['responded_bool'] * 100
    response_purchased = response_purchased[['Purchase_Last_Quarter', 'Response Rate (%)']]
    return response_purchased.to_dict(orient='records')

def get_task_4(data):
    bins = [0.99, 4, 8, np.inf]
    labels = ["1–4", "5–8", ">8"]
    product_segments = pd.cut(data["Unique_Products_Purchased"], bins=bins, labels=labels)
    summary_table = data.groupby(product_segments, observed=False)["responded_bool"].mean() * 100
    return summary_table.reset_index(name="Response Rate (%)").to_dict(orient='records')


# Convert 'yes'/'no' into a boolean True/False (handles mixed casing too)
data['responded_bool'] = data['Response_to_Campaign'].str.strip().str.lower() == 'yes'

# -------------------------------------------------
# Campaign analysis endpoint
# -------------------------------------------------
@app.get("/campaign-analysis-api")
def campaign_analysis():
    task_1_result = get_task_1(data)
    task_2_result = get_task_2(data)
    task_3_result = get_task_3(data)
    task_4_result = get_task_4(data)

    return {
        "task_1": task_1_result,
        "task_2": task_2_result,
        "task_3": task_3_result,
        "task_4": task_4_result,
    }


# -------------------------------------------------
# HTML frontend embedded directly in endpoint
# -------------------------------------------------
@app.get("/campaign-analysis", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Campaign analysis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
            }
            button {
                padding: 10px 16px;
                font-size: 16px;
                margin-bottom: 20px;
                cursor: pointer;
            }
            table {
                border-collapse: collapse;
                table-layout: fixed;
                width: 100%;
            }
            #summaryTables {
                display: flex;
                flex-direction: column;
                gap: 24px;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f4f4f4;
            }
        </style>
    </head>
    <body>

        <h2>Campaign analysis</h2>

        <button onclick="loadData()">Load Summary</button>

        <div id="summaryTables"></div>

        <script>
            function loadData() {
                fetch('/campaign-analysis-api')
                    .then(response => response.json())
                    .then(data => {
                        const tablesContainer = document.querySelector('#summaryTables');
                        tablesContainer.innerHTML = '';

                        const taskNames = [
                            'Response rate by gender',
                            'Response rate by age group',
                            'Response rate by purchase history',
                            'Response rate by product segment'
                        ];

                        Object.entries(data).forEach(([taskKey, taskResult], taskIndex) => {
                            if (!taskResult.length) {
                                return;
                            }

                            const table = document.createElement('table');
                            const headers = Object.keys(taskResult[0]);

                            table.innerHTML = `
                                <caption>${taskNames[taskIndex]}</caption>
                                <thead>
                                    <tr>${headers.map(header => `<th>${header}</th>`).join('')}</tr>
                                </thead>
                                <tbody>
                                    ${taskResult.map(row => `
                                        <tr>${headers.map(header => `<td>${row[header]}</td>`).join('')}</tr>
                                    `).join('')}
                                </tbody>
                            `;
                            tablesContainer.appendChild(table);
                        });
                    })
                    .catch(error => {
                        alert('Error fetching data');
                        console.error(error);
                    });
            }
        </script>

    </body>
    </html>
    """

    return html_content
