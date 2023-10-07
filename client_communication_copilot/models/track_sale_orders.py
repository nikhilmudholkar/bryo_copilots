import datetime

import pandas as pd
from .create_llm_prompt import askai, remove_tags



def track_sale_orders(cursor, order_id):
    # extract sale order ids from the dataframe


    # get sale_order
    cursor.execute("""SELECT name as sale_order,
                            date_order as ordered_date,
                            commitment_date as due_date,
                            create_uid as created_by
                        FROM sale_order
                        where state = 'sale' and  name = %s""", (order_id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_sale_order = pd.DataFrame(result, columns=columns)

    # strip the time from all the datetime columns. These columns are in string format so convert them to
    # string first convert the datetime columns to strings
    df_sale_order['ordered_date'] = df_sale_order['ordered_date'].astype(str)
    df_sale_order['ordered_date'] = df_sale_order['ordered_date'].str[:10]
    # df_sale_order['ordered_date'] = df_sale_order['ordered_date'].dt.date
    df_sale_order['due_date'] = df_sale_order['due_date'].astype(str)
    df_sale_order['due_date'] = df_sale_order['due_date'].str[:10]
    # print datatype of all the columns
    # print(df_sale_order.dtypes)
    print(df_sale_order)

    # get ordered_products table
    cursor.execute("""SELECT sale_order, 
                                product_id, 
                                ordered_quantity 
                        FROM ordered_products where sale_order = %s""",
                     (order_id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_ordered_products = pd.DataFrame(result, columns=columns)

    # get fulfillment table
    cursor.execute("""SELECT sale_order, delivery_id, delivery_state, committed_date,
                        scheduled_date, delivered_date, delivery_priority from fulfillment where sale_order = %s""",
                     (order_id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_fulfillment = pd.DataFrame(result, columns=columns)

    # strip the time from all the datetime columns
    # convert the datetime columns to strings
    # df_fulfillment['fulfillment_create_date'] = df_fulfillment['fulfillment_create_date'].astype(str)
    # df_fulfillment['fulfillment_create_date'] = df_fulfillment['fulfillment_create_date'].str[:10]
    df_fulfillment['committed_date'] = df_fulfillment['committed_date'].astype(str)
    df_fulfillment['committed_date'] = df_fulfillment['committed_date'].str[:10]
    df_fulfillment['scheduled_date'] = df_fulfillment['scheduled_date'].astype(str)
    df_fulfillment['scheduled_date'] = df_fulfillment['scheduled_date'].str[:10]
    df_fulfillment['delivered_date'] = df_fulfillment['delivered_date'].astype(str)
    df_fulfillment['delivered_date'] = df_fulfillment['delivered_date'].str[:10]
    # print(df_fulfillment.dtypes)

    # get stock_movements table
    cursor.execute("""SELECT sale_order, delivery_id, stock_picking_id, picking_state, picking_create_date, 
                        product_id, picking_order_quantity, reserved_quantity, picked_quantity, picking_write_date,
                        stock_picking_origin, stock_picking_destination from stock_movements where sale_order = %s""",
                     (order_id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_stock_movements = pd.DataFrame(result, columns=columns)

    # strip the time from all the datetime columns
    # convert the datetime columns to strings
    df_stock_movements['picking_create_date'] = df_stock_movements['picking_create_date'].astype(str)
    df_stock_movements['picking_create_date'] = df_stock_movements['picking_create_date'].str[:10]
    df_stock_movements['picking_write_date'] = df_stock_movements['picking_write_date'].astype(str)
    df_stock_movements['picking_write_date'] = df_stock_movements['picking_write_date'].str[:10]
    # print(df_stock_movements.dtypes)

    # get back_orders table
    cursor.execute("""SELECT sale_order, backorder_id, delivery_id from back_orders where sale_order = %s""",
                     (order_id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_back_orders = pd.DataFrame(result, columns=columns)

    # message = create_llm_message(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements)

    # url = "http://35.92.128.67:8000/askai"
    # payload for slack webhook endpoint to send messages to a channel
    # payload = {
    #     "question": "Q: Who is elon musk? A: ",
    #     "max_tokens": 100,
    #     "stop": ["Q:", "\n"],
    #     "security_token": "bryo_access_control_1",
    #     # "echo": "true"
    # }

    response_palm = str(order_id) + "\n"
    llm_result = askai(df_sale_order, df_ordered_products, df_fulfillment, df_stock_movements, df_back_orders)
    response_palm = response_palm + llm_result

    return response_palm






