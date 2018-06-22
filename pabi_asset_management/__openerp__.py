# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Asset Management",
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
        "pabi_invest_construction",
        "pabi_chartfield_merged",
        "pabi_utils",
        "pabi_account_move_adjustment",
        "hr_expense_auto_invoice",
        "pabi_utils",
    ],
    "description": """
This module allow creating asset during incoming shipment.
    """,
    "data": [
        "security/ir.model.access.csv",
        # "data/import_templates.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
        "xlsx_template/xlsx_template_wizard.xml",
        "data/sequence_data.xml",
        "data/asset_purchase_method.xml",
        "data/account_data.xml",
        "data/location_data.xml",
        "data/journal_data.xml",
        "data/asset_status.xml",
        "data/default_value.xml",
        "wizard/asset_parent_deliver_wizard.xml",
        "views/asset_view.xml",
        "wizard/account_asset_remove_view.xml",
        "wizard/create_asset_request_view.xml",
        "wizard/create_asset_removal_view.xml",
        "wizard/create_asset_adjust_wizard.xml",
        "wizard/account_asset_compute.xml",
        "views/account_invoice_view.xml",
        "views/account_view.xml",
        "views/asset_request_view.xml",
        "views/asset_changeowner_view.xml",
        "views/asset_transfer_view.xml",
        "views/asset_adjust_view.xml",
        "views/asset_removal_view.xml",
        "views/asset_receive_view.xml",
        "views/product_view.xml",
        "views/purchase_requisition_view.xml",
        "views/stock_view.xml",
        "views/purchase_view.xml",
        "views/purchase_master_data_view.xml",
        "views/res_project_view.xml",
        "views/res_section_view.xml",
        "views/hr_expense_view.xml",
        "views/ir_sequence_view.xml",
        "wizard/asset_action_excel_import.xml",
    ],
    'installable': True,
    'active': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
