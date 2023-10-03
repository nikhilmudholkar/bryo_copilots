import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
from datetime import datetime


def create_llm_context_order_tracking():
    today = str(datetime.today().date())

    prompt = """You are a helpful order management assistant for the order management team to help them achieve maximum on-time delivery and best customer experience.


The date format is: yyyy-mm-dd
Today is: {0}


Provide 2 answers to the 2 following questions
Is the sale order delivered? You know if a sale order is delivered if all delivery orders related to a sale order have a delivered_date that is not null, which confirms the order was delivered.
Does the order have a delay? Consider only the committed_date, the delivered_date and Today. If the committed_date is before Today and / or is the committed_date before the delivered_date, then the order is delayed.


Describe where the sale order is stuck.


Use the fulfillment data contained between triple backticks and the fulfillment process contained between triple dashes. The description of the fulfillment process provides you with context on how to read the fulfillment data. Every [] corresponds to data found in fulfillment data.


<fulfillment process>
---


Start


<sale order> Creation
* Create <sale order> [sale_order] at [ordered_date] by [created_by]
* Enter <sale order> due date [due_date]
* Enter <ordered product> [product_id] and quantity [ordered_quantitiy]


<delivery order> Creation
* Create <delivery order> [delivery_order_id] at [delivery_create_date]
* Enter <delivery order> committed delivery date [committed_date]
* Enter <delivery order> scheduled shipment date [schedule_date] that should constantly be kept updated


Decision 1
* Was the <delivery order> created?
* Yes: Go to <stock picking order> Creation
* No: send reminder if there is a risk of delay


<stock picking order> Creation
* A <stock picking order> is created automatically for [stock_picking_id] of [product_id] at [stock_picking_date]
* Enter ordered quantity [stock_picking_quantity]
* Enter reserved quantity [reserved_quantity] from the stock in inventory
* Enter destination [stock_picking_destination]
* Enter from where the stock needs to be moved [stock_picking_origin]


Decision 2
* Was the stock picked?
* Yes: Go to <Stock picking confirmation>
* No: send reminder if there is a risk of delay


<Stock picking confirmation>
* Enter [stock_picking_quantity] at [picking_write_date] and change [stock_picking_state] to \"done\"


Decision 3
* Are all stock picks for this delivery order \"done\"?
* Yes: Go to <Delivery confirmation>
* No: send reminder to execute <stock picks> if there is a risk of delay


<Delivery confirmation>
* Change the <delivery order> status [delivery_state] to \"done\"
* Enter the [delivered_date]




END
---
""".format(today)
    print(prompt)
    return prompt

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


def create_llm_context_leadtime_update(vendor_df_str):
    today = str(datetime.today().date())
    # vendor_df_str = convert_dataframe_to_string(vendor_df)
    prompt = """You are a email parsing copilot. Your goal is to extract the Vendor name, product ID, product name, and updated delivery date from a supplier email. 
The first task in this is to extract the vendor ID and name from the email that will be provided as a prompt and match it to the correct vendor in the table called "Potential list of vendors" contained between triple backticks. 
Answer the prompt in json format with key value pairs 

```
<Potential list of vendors>
{0}
""".format(vendor_df_str)
    print(prompt)
    return prompt


def create_llm_context_leadtime_impact(vendor_df_str):
    today = str(datetime.today().date())
    # vendor_df_str = convert_dataframe_to_string(vendor_df)
    prompt = """You are a email parsing copilot. Your goal is to extract the partner_id, commercial_company_name, po_name, product_name, product_qty and date_planned from a supplier email that the user will provide as a prompt. 
The task in to then match it to the correct row in the table called "Pending POs and respective products" contained between triple backticks. 
Return the most probable row as answer to the prompt in json format with key value pairs. Add a new key to the json for the new_date_planned. 
Start your answer with "Please Verify if the email is about this PO?" 

```
<Pending POs and respective products>
{0}
""".format(vendor_df_str)
    print(prompt)
    return prompt


def create_llm_context_delayed_products(delayed_products_df_str, sales_order_df_str):
    today = str(datetime.today().date())
    # vendor_df_str = convert_dataframe_to_string(vendor_df)
    prompt = """You are a data matching copilot. 
You will be given a purchase order of procurement part by the user in the Json format as message.
You will also be given the inventory table called "Inventory for delayed products" and Sales orders table called "Orders that could be impacted by delayed products".

Your goal is to figure out which sale orders will be delayed because of this delay in procurement. The way you do this is find the relevant inventory levels of the product mentioned in the purchase order. Return this inventory level in the response
Then you need to calculate if the sum of all the qty_ordered in all the sale orders for that particular product is  > inventory levels for that product. Make sure to match exact product names
 If so, return the statement "INSUFICENT STOCK" and return the sales order that's affected

```
<Inventory for delayed products>
{0}


<Orders that could be impacted by delayed products>
{1}
```
""".format(delayed_products_df_str, sales_order_df_str)
    print(prompt)
    return prompt



def create_llm_context_delayed_manufacturing_products(delayed_products_df_str, manufacturing_order_df_str):
    today = str(datetime.today().date())
    # vendor_df_str = convert_dataframe_to_string(vendor_df)
    prompt = """You are a data matching copilot. 
You will be given a purchase order for procurement by the user in the Json format as message.
You will also be given the inventory table called "Inventory for delayed products" and Manufacturing orders table called "Manufacturing orders that could be impacted by delayed products".

Your goal is to figure out which Manufacturing orders will be delayed because of this delay in procurement. The way you do this is find the relevant inventory levels of the product mentioned in the purchase order. Return this inventory level in the response

Then you need to filter all the manufacturing orders as given in "Manufacturing orders that could be impacted by delayed products" table for that product and calculate the addition of the qty_ordered values for the filtered rows. If this sum value is > inventory levels for that product as given in "Inventory for delayed products" table, return "INSUFFICIENT STOCK" . Make sure to match exact product names
 Also return the Manufacturing orders that will be affected because of this.

```
<Inventory for delayed products>
{0}


<Manufacturing orders that could be impacted by delayed products>
{1}
```""".format(delayed_products_df_str, manufacturing_order_df_str)
    print(prompt)
    return prompt

def create_llm_examples():
    today = str(datetime.today().date())
    examples = [
        InputOutputTextPair(
        input_text="""<fulfillment data>
```
1. <sale order> table:

sale_order|ordered_date           |due_date|created_by|
----------+-----------------------+--------+----------+
S03232    |2023-08-08|        |         2|

2. <ordered product> table:

sale_order|product_id|ordered_quantity|
----------+----------+----------------+
S03232    |        13|            1.00|
S03232    |        19|            1.00|

3. <delivery order> table:

sale_order|delivery_id|delivery_state|committed_date         |scheduled_date         |delivered_date         |delivery_priority|
----------+-----------+--------------+-----------------------+-----------------------+-----------------------+-----------------+
S03232    |         39|done          |2023-08-08|2023-08-08|2023-08-08|0                |
S03232    |         40|done          |2023-08-08|2023-08-08|2023-08-13|0                |


4. <stock picking order> table:

sale_order|delivery_id|stock_picking_id|picking_state|picking_create_date    |product_id|picking_order_quantity|reserved_quantity|picked_quantity|picking_write_date     |stock_picking_origin|stock_picking_destination|
----------+-----------+----------------+-------------+-----------------------+----------+----------------------+-----------------+---------------+-----------------------+--------------------+-------------------------+
S03232    |         39|              71|done         |2023-08-08|        13|                  1.00|             0.00|           1.00|2023-08-08|                   8|                        5|
S03232    |         40|              72|done         |2023-08-08|        19|                  1.00|             0.00|           1.00|2023-08-13|                   8|                        5|


5. <backorder> table:

sale_order|backorder_id|delivery_id|
----------+------------+-----------+
S03232    |          39|         40|

```
""",
        output_text="""Order S03232 is fully delivered. Both delivery orders have a delivered_date. 
Delivery order 39 for product_id 13 was delivered at delivered_date 2023-08-08
Delivery order 40 for product_id 19 was a backorder (backorder_id 39) because the product was out of stock and was therefore delivered later at delivered_date 2023-08-13

Order S03232 was delayed as the committed_date was 2023-08-08 while the delivered_date of the last delivery order (delivery_id 40) was 2023-08-13

The order isn’t currently stuck as it has been delivered.

        """
        ),
        InputOutputTextPair(
        input_text="""<fulfillment data>
```
1. <sale order> table:

sale_order|ordered_date           |due_date|created_by|
----------+-----------------------+--------+----------+
S02121    |2023-07-26|        |         1|

2. <ordered product> table:

sale_order|product_id|ordered_quantity|
----------+----------+----------------+
S02121    |        31|            5.00|
S02121    |        21|            5.00|

3. <delivery order> table:

sale_order|delivery_id|delivery_state|committed_date         |scheduled_date         |delivered_date|delivery_priority|
----------+-----------+--------------+-----------------------+-----------------------+--------------+-----------------+
S02121    |         25|assigned      |2023-07-26|2023-07-27|              |0                |


4. <stock picking order> table:

sale_order|delivery_id|stock_picking_id|picking_state|picking_create_date    |product_id|picking_order_quantity|reserved_quantity|picked_quantity|picking_write_date     |stock_picking_origin|stock_picking_destination|
----------+-----------+----------------+-------------+-----------------------+----------+----------------------+-----------------+---------------+-----------------------+--------------------+-------------------------+
S02121    |         25|              43|assigned     |2023-07-26|        31|                  5.00|             5.00|           0.00|2023-07-26 12:45:54.006|                   8|                        5|
S02121    |         25|              44|assigned     |2023-07-26|        21|                  5.00|             5.00|           0.00|2023-07-26|                   8|                        5|


5. <backorder> table:

sale_order|backorder_id|delivery_id|
----------+------------+-----------+

```
""",
        output_text="""Order S02121 is not delivered. The delivery order delivery_id 25 has no delivered_date.

Order S02121 is delayed because the committed_date was  2023-07-26 while today is 2023-08-13.

Order S02121 is stuck in stock picking. Stock picking orders 43 and 44 were created on 2023-07-26. Both product 31 and 21 were ordered in picking_order_quantity 5 and both are reserved with reserved_quantity 5 from location 8. But both picks haven’t been done yet as the picked_quantity is 0 for both!
"""
        ),
        InputOutputTextPair(
        input_text="""<fulfillment data>
```
1. <sale order> table:

sale_order|ordered_date           |due_date|created_by|
----------+-----------------------+--------+----------+
S03434    |2023-08-13|        |         2|

2. <ordered product> table:

sale_order|product_id|ordered_quantity|
----------+----------+----------------+
S03434    |        40|            1.00|
S03434    |        35|            0.00|

3. <delivery order> table:

sale_order|delivery_id|delivery_state|committed_date         |scheduled_date         |delivered_date         |delivery_priority|
----------+-----------+--------------+-----------------------+-----------------------+-----------------------+-----------------+
S03434    |         46|cancel        |2023-08-13|2023-08-13|                       |0                |
S03434    |         45|done          |2023-08-13|2023-08-13|2023-08-13|0                |

4. <stock picking order> table:

sale_order|delivery_id|stock_picking_id|picking_state|picking_create_date    |product_id|picking_order_quantity|reserved_quantity|picked_quantity|picking_write_date     |stock_picking_origin|stock_picking_destination|
----------+-----------+----------------+-------------+-----------------------+----------+----------------------+-----------------+---------------+-----------------------+--------------------+-------------------------+
S03434    |         45|              78|done         |2023-08-13|        40|                  1.00|             0.00|           1.00|2023-08-13|                   8|                        5|


5. <backorder> table:

sale_order|backorder_id|delivery_id|
----------+------------+-----------+

```
""",
        output_text="""Order S03434 is partially delivered. The delivery order delivery_id 45 has been delivered at delivered_date 2023-08-13. The delivery order delivery_id 46 has been cancelled.

Product 40 was picked in quantity 1 at 2023-08-13.

Delivery of product 35 has been cancelled.
"""
        ),
        InputOutputTextPair(
        input_text="""<fulfillment data>
```
1. <sale order> table:

sale_order|ordered_date           |due_date|created_by|
----------+-----------------------+--------+----------+
S02626    |2023-08-08|        |         2|


2. <ordered product> table:

sale_order|product_id|ordered_quantity|
----------+----------+----------------+
S02626    |        16|            1.00|
S02626    |        27|            1.00|
S02626    |        13|            1.00|


3. <delivery order> table:

sale_order|delivery_id|delivery_state|committed_date         |scheduled_date         |delivered_date         |delivery_priority|
----------+-----------+--------------+-----------------------+-----------------------+-----------------------+-----------------+
S02626    |         33|done          |2023-08-08|2023-08-08|2023-08-08|0                |
S02626    |         34|assigned      |2023-08-08|2023-08-08|                       |0                |

4. <stock picking order> table:

sale_order|delivery_id|stock_picking_id|picking_state|picking_create_date    |product_id|picking_order_quantity|reserved_quantity|picked_quantity|picking_write_date     |stock_picking_origin|stock_picking_destination|
----------+-----------+----------------+-------------+-----------------------+----------+----------------------+-----------------+---------------+-----------------------+--------------------+-------------------------+
S02626    |         33|              59|done         |2023-08-08|        13|                  1.00|             0.00|           1.00|2023-08-08|                   8|                        5|
S02626    |         34|              60|assigned     |2023-08-08|        27|                  1.00|             1.00|           0.00|2023-08-09|                   8|                        5|
S02626    |         34|              58|assigned     |2023-08-08|        16|                  1.00|             1.00|           0.00|2023-08-09|                   8|                        5|


5. <backorder> table:

sale_order|backorder_id|delivery_id|
----------+------------+-----------+
S02626    |          33|         34|
S02626    |          33|         34|


```
""",
        output_text="""Order S02626 is partially delivered. The delivery order delivery_id 33 has been delivered at delivered_date 2023-08-13. The delivery order delivery_id 34 is a backorder for products 27 and 16 and has not been delivered yet.

Order S02626 is delayed because the committed_date was  2023-08-08 while today is 2023-08-13.

Delivery order 34 is stuck in stock picking. Stock picking orders 60 and 58 were created on 2023-08-08. Both product 16 and 27 were ordered in picking_order_quantity 1 and both are reserved with reserved_quantity 1 from location 8. But both picks haven’t been done yet as the picked_quantity is 0 for both!

""")
    ]
    return examples





def ask_palm_order_tracking(msg_text):
    context = create_llm_context_order_tracking()
    examples = create_llm_examples()
    print("example_created")
    vertexai.init(project="eternal-impulse-395109", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    chat = chat_model.start_chat(
        context=context,
        examples = examples
    )
    print("message_sent")
    response = chat.send_message(msg_text, **parameters)
    print(f"Response from Model: {response.text}")
    return response.text

def ask_palm_leadtime_update(msg_text, vendor_df_str):
    context = create_llm_context_leadtime_update(vendor_df_str)
    print("example_created")
    vertexai.init(project="eternal-impulse-395109", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    chat = chat_model.start_chat(
        context=context
    )
    print("message_sent")
    response = chat.send_message(msg_text, **parameters)
    print(f"Response from Model: {response.text}")
    return response.text


def ask_palm_leadtime_impact(msg_text, vendor_df_str):
    context = create_llm_context_leadtime_impact(vendor_df_str)
    print("example_created")
    vertexai.init(project="eternal-impulse-395109", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    chat = chat_model.start_chat(
        context=context
    )
    print("message_sent")
    response = chat.send_message(msg_text, **parameters)
    print(f"Response from Model: {response.text}")
    return response.text


def ask_palm_delayed_products(msg_text, inventory_df_str, sales_order_df_str):
    context = create_llm_context_delayed_products(inventory_df_str, sales_order_df_str)
    print("example_created")
    vertexai.init(project="eternal-impulse-395109", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    chat = chat_model.start_chat(
        context=context
    )
    print("message_sent")
    response = chat.send_message(msg_text, **parameters)
    print(f"Response from Model: {response.text}")
    return response.text


def ask_palm_delayed_manufacturing_products(msg_text, inventory_df_str, manufacturing_order_df_str):
    context = create_llm_context_delayed_manufacturing_products(inventory_df_str, manufacturing_order_df_str)
    print("example_created")
    vertexai.init(project="eternal-impulse-395109", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    chat = chat_model.start_chat(
        context=context
    )
    print("message_sent")
    response = chat.send_message(msg_text, **parameters)
    print(f"Response from Model: {response.text}")
    return response.text