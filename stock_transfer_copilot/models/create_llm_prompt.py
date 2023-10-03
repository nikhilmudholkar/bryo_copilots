import json
import re

import pandas
import psycopg2
from datetime import datetime


# function to create an LLm prompt just like context
import requests


def create_llm_context():
    today = str(datetime.today().date())

    prompt = """
      find anomalies in these tables
      """.format(today, today, today)
    print(prompt)
    return prompt




import pandas as pd

def convert_dataframe_to_string(df):
    """Converts a DataFrame into a string format.

    Args:
    df: The DataFrame to convert.

    Returns:
    A string in the format of:
      sale_order|ordered_date           |due_date|created_by|
      ----------+-----------------------+--------+----------+
      S00024    |2023-07-26|        |         1|
    """

    string = ""

    for col in df.columns:
        string += col + "|"

    string += "\n"
    for col in df.columns:
        string += "-" * len(col) + "+"
    # string += "-" * len(string) + "\n"
    string += "\n"

    for index, row in df.iterrows():
        # if a col in empty, add a tab
        string += "|".join([str(col) if str(col) not in ["NaT", "None"] else "\t" for col in row]) + "\n"

        # string += "|".join([str(col) for col in row]) + "\n"
    return string


def create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders):
    # print("Creating LLm message...")
    df_sale_order_string = convert_dataframe_to_string(df_sale_order)

    df_ordered_products_string = convert_dataframe_to_string(df_ordered_products)

    df_fulfillment_string = convert_dataframe_to_string(df_fulfillment)

    df_stock_movements_string = convert_dataframe_to_string(df_stock_movements)

    df_back_orders_string = convert_dataframe_to_string(df_back_orders)

    message_string = """<fulfillment process>\n"""
    message_string += """```\n"""
    message_string += "1. <sale order> table:\n"
    message_string += df_sale_order_string + "\n"
    message_string += "2. <ordered product> table:\n"
    message_string += df_ordered_products_string + "\n"
    message_string += "3. <fulfillment order> table:\n"
    message_string += df_fulfillment_string + "\n"
    message_string += "4. <stock move order> table:\n"
    message_string += df_stock_movements_string + "\n"
    message_string += "5. <back order> table:\n"
    message_string += df_back_orders_string + "\n"
    # print(message_string)

    return message_string

def remove_tags(text):
    """Remove HTML tags from a string."""
    tags = re.compile('<.*?>')
    return tags.sub('', text)

def askai(message):
    context = create_llm_context()
    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    url = "http://35.92.128.67:8000/askai"
    payload = {
        "security_token": "bryo_access_control_1",
        "context": context,
        "message": message
    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    # print(response_palm.text)
    response_palm = response_palm.text
    # print(response_palm)
    return response_palm
