{
    'name': 'A ChatGPT for order management',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': '-100',
    'description': """Bryo automates your order management in Odoo by leveraging large language models like the ones used by ChatGPT""",
    'author': 'Bryo UG',
    'maintainer': 'Bryo UG',
    'license': 'LGPL-3',
    'website': 'https://www.bryo.io',
    'summary': 'Bryo automates your order management in Odoo by leveraging large language models like the ones used by ChatGPT',
    "keywords": ["fulfillment", "bard", "chatgpt", "openai", "AI", "copilot", "llm"],
    'data': [
        'security/ir.model.access.csv',
        # 'views/menu.xml',
        # 'views/sales_order.xml',
        'views/order_tracking_menu.xml',
        'views/sale_order_table.xml',
        # 'views/orders_table_1.xml',
        # 'views/ordered_products.xml',
        # 'views/stock_levels.xml',
        # 'views/fulfillment.xml',
        # 'views/stock_movements.xml',
        # 'views/ai_copilot.xml',
        'views/ai_copilot.xml',
        'data/custom_channels.xml',
    ],
    "depends": [
        "sale",
        "sale_stock",
        "project",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
}