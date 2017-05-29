# -*- coding: utf-8 -*-
{
    "name": "Stock Asset Management",
    "version": "0.1",
    "author": "Ecosoft",
    "website": "http://ecosoft.co.th",
    "category": "Customs Modules",
    "depends": [
        "account_asset_management",
        "stock_account",
        "account_anglo_saxon",
        "pabi_purchase_work_acceptance",
        "account_budget_activity",
    ],
    "description": """
This module allow creating asset during incoming shipment.
    """,
    "data": [
        "data/account_data.xml",
        "views/account_invoice_view.xml",
        "views/account_view.xml",
        "views/asset_view.xml",
        "views/product_view.xml",
        "views/purchase_requisition_view.xml",
        "views/stock_view.xml",
    ],
    'installable': True,
    'active': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
