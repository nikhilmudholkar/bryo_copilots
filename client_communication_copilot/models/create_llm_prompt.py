import json
import re

import pandas
import psycopg2
from datetime import datetime, time

# function to create an LLm prompt just like context
import requests


def remove_tags(text):
    """Remove HTML tags from a string."""
    tags = re.compile('<.*?>')
    return tags.sub('', text)


# def askai(message, vendor_df):
#     context = create_llm_context()
#     vendor_df_str = convert_dataframe_to_string(vendor_df)
#     # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
#     url = "http://35.92.128.67:8000/askaiaboutleadtime"
#     payload = {
#         "security_token": "bryo_access_control_1",
#         "context": context,
#         "message": message,
#         "vendor_df": vendor_df_str
#     }
#     response_palm = requests.post(
#         url, data=json.dumps(payload),
#         headers={'Content-Type': 'application/json'}
#     )
#     # print(response_palm.text)
#     response_palm = response_palm.text
#     # print(response_palm)
#     return response_palm


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
