{
    'name': 'stock transfer copilot',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': '-100',
    'description': """Bryo automates your stock transfers between warehouses in Odoo by leveraging large language models like the ones used by ChatGPT""",
    'author': 'Bryo UG',
    'maintainer': 'Bryo UG',
    'license': 'LGPL-3',
    'website': 'https://www.bryo.io',
    'summary': 'Bryo automates your stock transfers between warehouses in Odoo by leveraging large language models like the ones used by ChatGPT',
    "keywords": ["fulfillment", "bard", "chatgpt", "openai", "AI", "copilot", "llm"],
    'data': [
        'data/stock_transfer_copilot_channel_data.xml',
        'data/copilot_user_partner_data.xml',
    ],
    "depends": [
        "sale",
        "sale_stock",
        "project",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
}