# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Budget Report',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'report_xls',
        'account_budget_activity',
        'pabi_budget_plan',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/budget_summary_report_wizard.xml',
        'wizards/budget_cost_centre_report_wizard.xml',
        'wizards/budget_detail_report_wizard.xml',
        'wizards/budget_plan_unit_analysis_report_wizard.xml',
        'wizards/budget_plan_project_analysis_report_wizard.xml',
        'xlsx_reports/directory.xml',
        'xlsx_reports/xlsx_report_budget_summary.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
