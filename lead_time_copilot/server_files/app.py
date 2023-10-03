#import pandas
import requests
import logging
#from llama_cpp import Llama
import json
from flask import Flask, redirect, url_for, request, render_template
from bry_test_2 import ask_palm_order_tracking, ask_palm_leadtime_update, ask_palm_leadtime_impact, \
    ask_palm_delayed_products, ask_palm_delayed_manufacturing_products

UPLOAD_FOLDER = '/home/ubuntu/bard_llm/ocr'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config["ALLOWED_FILE_TYPES"] = ["application/pdf"]
# app.config["ALLOWED_EXTENSIONS"] = [".pdf", ".jpg", ".xls", ".json"]

# llama = Llama(model_path="/home/ubuntu/dalai/llama/models/7B/ggml-model-f16.bin")

logger = logging.getLogger(name=__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='app.log',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


@app.route('/')
def hello_world():
    return 'HELLO WORLD!'

@app.route('/askai', methods=['POST'])
def webhook():
    print("Data received from Webhook is: ", request.json)

    if request.method == 'POST':
        payload = request.data.decode("utf-8")
        payload = json.loads(payload)
        security_token = payload.get('security_token')
        logger.info("**new request to llm**")
        logger.info(("security_token {}").format(security_token))

        if security_token in ['bryo_access_control_1']:
            context = payload.get("context")
            msg = payload.get("message")
            logger.info(("context: {}").format(context))
            logger.info(("message: {}").format(msg))
            # max_tokens = payload.get('max_tokens')
            # stop = payload.get('stop')
            # temperature = payload.get('temperature')
            # top_p = payload.get('top_p')
            # frequency_penalty = payload.get('frequency_penalty')
            # presence_penalty = payload.get('presence_penalty')
            # engine = payload.get('engine')
            # best_of = payload.get('best_of')
            # n = payload.get('n')
            # stream = payload.get('stream')
            # logprobs = payload.get('logprobs')
            echo = payload.get('echo')
            # stop_sequence = payload.get('stop_sequence')
            # return_prompt = payload.get('return_prompt')
            # logit_bias = payload.get('logit_bias')

            # output = llama(question_string, max_tokens = max_tokens, stop = stop, echo = echo)
            output = ask_palm_order_tracking(msg)
            print(output)
            return output
        else:
            print("wrong security token")
            return "incorrect security token"

@app.route('/askaiaboutleadtime', methods=['POST'])
def webhook_leadtime():
    print("Data received from Webhook is: ", request.json)
    if request.method == 'POST':
        logger.info("inside post message")
        payload = request.data.decode("utf-8")
        payload = json.loads(payload)
        logger.info(("payload {}").format(payload))
        security_token = payload.get('security_token')
        logger.info("**new request to llm about leadtime**")
        logger.info(("security_token {}").format(security_token))

        if security_token in ['bryo_access_control_1']:
            context = payload.get("context")
            msg = payload.get("message")
            vendor_df_str = payload.get("vendor_df")
            logger.info(("context: {}").format(context))
            logger.info(("message: {}").format(msg))
            # max_tokens = payload.get('max_tokens')
            # stop = payload.get('stop')
            # temperature = payload.get('temperature')
            # top_p = payload.get('top_p')
            # frequency_penalty = payload.get('frequency_penalty')
            # presence_penalty = payload.get('presence_penalty')
            # engine = payload.get('engine')
            # best_of = payload.get('best_of')
            # n = payload.get('n')
            # stream = payload.get('stream')
            # logprobs = payload.get('logprobs')
            echo = payload.get('echo')
            # stop_sequence = payload.get('stop_sequence')
            # return_prompt = payload.get('return_prompt')
            # logit_bias = payload.get('logit_bias')

            # output = llama(question_string, max_tokens = max_tokens, stop = stop, echo = echo)
            output = ask_palm_leadtime_update(msg, vendor_df_str)
            print(output)
            return output
        else:
            print("wrong security token")
            return "incorrect security token"


@app.route('/askaiaboutleadtimeimpact', methods=['POST'])
def webhook_leadtime_impact():
    print("Data received from Webhook is: ", request.json)
    if request.method == 'POST':
        logger.info("inside post message")
        payload = request.data.decode("utf-8")
        payload = json.loads(payload)
        logger.info(("payload {}").format(payload))
        security_token = payload.get('security_token')
        logger.info("**new request to llm about leadtime**")
        logger.info(("security_token {}").format(security_token))

        if security_token in ['bryo_access_control_1']:
            context = payload.get("context")
            msg = payload.get("message")
            vendor_df_str = payload.get("vendor_df")
            logger.info(("context: {}").format(context))
            logger.info(("message: {}").format(msg))
            echo = payload.get('echo')
            # output = llama(question_string, max_tokens = max_tokens, stop = stop, echo = echo)
            output = ask_palm_leadtime_impact(msg, vendor_df_str)
            print(output)
            return output
        else:
            print("wrong security token")
            return "incorrect security token"


@app.route('/askaiaboutdelayedproducts', methods=['POST'])
def webhook_delayed_products():
    print("Data received from Webhook is: ", request.json)
    if request.method == 'POST':
        logger.info("inside post message")
        payload = request.data.decode("utf-8")
        payload = json.loads(payload)
        logger.info(("payload {}").format(payload))
        security_token = payload.get('security_token')
        logger.info("**new request to llm about leadtime**")
        logger.info(("security_token {}").format(security_token))

        if security_token in ['bryo_access_control_1']:
            context = payload.get("context")
            msg = payload.get("message")
            inventory_df_str = payload.get("inventory_df")
            sales_order_df_str = payload.get("sales_order_df")
            logger.info(("context: {}").format(context))
            logger.info(("message: {}").format(msg))
            echo = payload.get('echo')
            # output = llama(question_string, max_tokens = max_tokens, stop = stop, echo = echo)
            output = ask_palm_delayed_products(msg, inventory_df_str, sales_order_df_str)
            print(output)
            return output
        else:
            print("wrong security token")
            return "incorrect security token"


@app.route('/askaiaboutdelayedmanufacturingproducts', methods=['POST'])
def webhook_delayed_manufacturingproducts():
    print("Data received from Webhook is: ", request.json)
    if request.method == 'POST':
        logger.info("inside post message")
        payload = request.data.decode("utf-8")
        payload = json.loads(payload)
        logger.info(("payload {}").format(payload))
        security_token = payload.get('security_token')
        logger.info("**new request to llm about leadtime**")
        logger.info(("security_token {}").format(security_token))

        if security_token in ['bryo_access_control_1']:
            context = payload.get("context")
            msg = payload.get("message")
            inventory_df_str = payload.get("inventory_df")
            manufacturing_order_df_str = payload.get("manufacturing_order_df")
            logger.info(("context: {}").format(context))
            logger.info(("message: {}").format(msg))
            echo = payload.get('echo')
            # output = llama(question_string, max_tokens = max_tokens, stop = stop, echo = echo)
            output = ask_palm_delayed_manufacturing_products(msg, inventory_df_str, manufacturing_order_df_str)
            print(output)
            return output
        else:
            print("wrong security token")
            return "incorrect security token"


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    logger.info("inside upload function")
    logger.info("UPLOADDDDData received from Webhook is: ")
    logger.info(request.files)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    # Get the PDF file from the request
    pdf_file = request.files['file']
    logger.info(("pdf_file {}").format(pdf_file))

    # Save the PDF file to the server
    try:
        pdf_file.save("uploaded.pdf")
        logger.info("pdf file saved")
    except Exception as e:
        print(e)
        logger.info("pdf file not saved")
        return "Could not save file"

    # Return a success message
    return "PDF uploaded successfully!"

if __name__ == "__main__":
    # result = cursor.execute("select * from postgres.public.auctions a")
    # print(result)
    app.run(host='0.0.0.0', port=8000, debug=True)
