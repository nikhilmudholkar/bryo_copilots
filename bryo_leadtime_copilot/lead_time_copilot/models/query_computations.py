from datetime import datetime
import pandas as pd


def calculate_impacted_saleorders(inventory_df, sale_orders_df, po_list_str):
    # print("Calculating impacted sale orders...")
    inventory = inventory_df.copy()
    # print(inventory[['product_id', 'product_name', 'quantity']])
    sale_orders = sale_orders_df.copy()
    # sort sales_orders by delivery_date
    # print(sale_orders)
    sale_orders = sale_orders.sort_values(by=['commitment_date'])


    # po_list_str is a list of multiple dictinaries in the string format. Convert this string into a list of dictionaries
    po_list = eval(po_list_str)
    # print("po_list", po_list)
    # convert the list of dictionaries into a dataframe
    po_df = pd.DataFrame(po_list)
    # print("po_df", po_df)
    impacted_so = []
    # for every sale order, get the quantity of the product. Then find the same product by product id in the inventory table. If the quantity in inventory >= quantity in sale order, update the quantity in inventory as difference
    for index, row in sale_orders.iterrows():
        product_id = row["product_id"]
        quantity_so = row["qty_ordered"]
        if product_id in po_df['product_id'].values:
            new_expected_delivery_date = po_df[po_df['product_id'] == product_id]['new_delivery_date'].values[0]
            # convert the new_expected_delivery_date into a datetime object
            # new_expected_delivery_date = datetime.strptime(new_expected_delivery_date, '%Y-%m-%d %H:%M:%S')
            # row['new_expected_delivery_date'] = new_expected_delivery_date + pd.Timedelta(days=int(row['lead_time']))
            # print(row['new_expected_delivery_date'])
            if new_expected_delivery_date != "":
                new_expected_delivery_date = datetime.strptime(new_expected_delivery_date, '%Y-%m-%d %H:%M:%S')
                row['new_delivery_date'] = new_expected_delivery_date + pd.Timedelta(days=int(row['lead_time']))
                print(row['new_delivery_date'])
            else:
                row['new_delivery_date'] = None
        else:
            row['new_delivery_date'] = None

    #   find the product in inventory
        product_row_inventory = inventory[inventory["product_id"] == product_id]
        if len(product_row_inventory) == 0:
            impacted_so.append(row)
        elif product_row_inventory["quantity"].values[0] >= quantity_so:
            inventory.loc[inventory["product_id"] == product_id, "quantity"] = product_row_inventory["quantity"].values[0] - quantity_so
        else:
            impacted_so.append(row)

    # print("impacted_so", impacted_so)
    result_df = pd.DataFrame(impacted_so)
    # print(result_df)
    return result_df



def calculate_impacted_manufacturing_orders(inventory_df, manufacturing_orders_df, po_list_str):
    # print("calculate_impacted_manufacturing_orders")
    inventory = inventory_df.copy()
    # print(inventory[['product_id', 'product_name', 'quantity']])
    manufacturing_orders = manufacturing_orders_df.copy()

    # sort manufacturing_orders by planned_start in ascending order
    manufacturing_orders = manufacturing_orders.sort_values(by=['date_planned_start'])
    # print(manufacturing_orders.columns)
    # print(manufacturing_orders['manuf_lead_time'])
    # po_list_str is a list of multiple dictinaries in the string format. Convert this string into a list of dictionaries
    po_list = eval(po_list_str)
    # convert the list of dictionaries into a dataframe
    po_df = pd.DataFrame(po_list)
    # print("po_df", po_df)
    impacted_so = []
    # for every sale order, get the quantity of the product. Then find the same product by product id in the inventory table. If the quantity in inventory >= quantity in sale order, update the quantity in inventory as difference
    for index, row in manufacturing_orders.iterrows():
        product_id = row["bom_product_id"]
        quantity_so = row["bom_product_qty"]
        if product_id in po_df['product_id'].values:
            new_expected_delivery_date = po_df[po_df['product_id'] == product_id]['new_delivery_date'].values[0]
            # convert the new_expected_delivery_date into a datetime object
            if new_expected_delivery_date != "":
                new_expected_delivery_date = datetime.strptime(new_expected_delivery_date, '%Y-%m-%d %H:%M:%S')
                row['new_delivery_date'] = new_expected_delivery_date + pd.Timedelta(days=int(row['manuf_lead_time']))
                # print(row['new_delivery_date'])
            else:
                row['new_delivery_date'] = None
            # new_expected_delivery_date = datetime.strptime(new_expected_delivery_date, '%Y-%m-%d %H:%M:%S')
            # row['new_expected_delivery_date'] = new_expected_delivery_date + pd.Timedelta(days=int(row['manuf_lead_time']))
            # print(row['new_expected_delivery_date'])
        else:
            row['new_delivery_date'] = None

    #   find the product in inventory
        product_row_inventory = inventory[inventory["product_id"] == product_id]
        # print("*********************" + str(row["name"]) + "************************")
        if len(product_row_inventory) == 0:
            impacted_so.append(row)
            # print("inventory not found")
        elif product_row_inventory["quantity"].values[0] >= quantity_so:
            # print("inventory found in sufficient quantity")
            # print("inventory: ", product_row_inventory["quantity"].values[0])
            # print("quantity_manufacturing_order: ", quantity_so)
            inventory.loc[inventory["product_id"] == product_id, "quantity"] = product_row_inventory["quantity"].values[0] - quantity_so
        else:
            # print("inventory found in insufficient quantity")
            # print("inventory: ", product_row_inventory["quantity"].values[0])
            # print("quantity_manufacturing_order: ", quantity_so)

            impacted_so.append(row)

    # print("impacted_so", impacted_so)
    result_df = pd.DataFrame(impacted_so)
    # print(result_df)
    return result_df
