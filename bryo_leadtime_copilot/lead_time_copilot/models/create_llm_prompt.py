import json
import re

import pandas
import psycopg2
from datetime import datetime, time

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


def askai(message, vendor_df):
    context = create_llm_context()
    vendor_df_str = convert_dataframe_to_string(vendor_df)
    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    url = "http://35.92.128.67:8000/askaiaboutleadtime"
    payload = {
        "security_token": "bryo_access_control_1",
        "context": context,
        "message": message,
        "vendor_df": vendor_df_str
    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    # print(response_palm.text)
    response_palm = response_palm.text
    # print(response_palm)
    return response_palm


def askaileadtimeimpact(message, vendor_df, rfq_flag):
    context = create_llm_context()
    vendor_df_str = convert_dataframe_to_string(vendor_df)
    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    if rfq_flag:
        print("####Inside rfq flag######")
        url = "http://35.92.128.67:8000/askaiaboutleadtimeimpactrfq"
    else:
        print("####Inside po flag######")
        url = "http://35.92.128.67:8000/askaiaboutleadtimeimpactpo"
    payload = {
        "security_token": "bryo_access_control_1",
        "context": context,
        "message": message,
        "vendor_df": vendor_df_str
    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    # print(response_palm.text)
    response_palm = response_palm.text
    # print(response_palm)
    return response_palm


def askaidelayedproducts(message, inventory_df, sales_order_df):
    context = create_llm_context()
    inventory_df_str = convert_dataframe_to_string(inventory_df)
    sales_order_df_str = convert_dataframe_to_string(sales_order_df)
    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    url = "http://35.92.128.67:8000/askaiaboutdelayedproducts"
    payload = {
        "security_token": "bryo_access_control_1",
        "context": context,
        "message": message,
        "inventory_df": inventory_df_str,
        "sales_order_df": sales_order_df_str
    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    # print(response_palm.text)
    response_palm = response_palm.text
    # print(response_palm)
    return response_palm


def askaidelayedmanufacturingproducts(message, inventory_df, manufacturing_order_df):
    context = create_llm_context()
    inventory_df_str = convert_dataframe_to_string(inventory_df)
    manufacturing_order_df_str = convert_dataframe_to_string(manufacturing_order_df)
    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    url = "http://35.92.128.67:8000/askaiaboutdelayedmanufacturingproducts"
    payload = {
        "security_token": "bryo_access_control_1",
        "context": context,
        "message": message,
        "inventory_df": inventory_df_str,
        "sales_order_df": manufacturing_order_df_str
    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    # print(response_palm.text)
    response_palm = response_palm.text
    # print(response_palm)
    return response_palm


def uploadpdftollm(pdf_file_path):
    url = "http://35.92.128.67:8000/upload"
    pdf_file = open(pdf_file_path, "rb")
    files = {'file': pdf_file}

    # payload = {
    #     "security_token": "bryo_access_control_1",
    #     "pdf_file": pdf_file
    # }
    print(files)
    # print(requests.post(url, files=files).headers['Content-Type'])

    # response_palm = requests.post(url, files=files).headers['Content-Type']

    response_palm = requests.post(
        url, files=files
    )

    return response_palm.text


# def create_slack_message():
#     url = "http://35.92.128.67:8000/createslackmessage"
#     payload = {
#         "security_token": "bryo_access_control_1"
#     }
#     response_palm = requests.post(
#         url, data=json.dumps(payload),
#         headers={'Content-Type': 'application/json'}
#     )
#     # print(response_palm.text)
#     response_palm = response_palm.text
#     # print(response_palm)
#     return response_palm

def create_message_draft(msg, unstructured_data, impacted_so, impacted_mo):
    url = "http://35.92.128.67:8000/createmessagedraft"
    payload = {
        "security_token": "bryo_access_control_1",
        "message": msg,
        "unstructured_data": unstructured_data,
        "impacted_so": impacted_so,
        "impacted_mo": impacted_mo

    }
    response_palm = requests.post(
        url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    response_palm = response_palm.text
    return response_palm
