# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from datetime import datetime
import time


class CDReceivablePaymentHistoryView(models.Model):
    _name = 'cd.receivable.payment.history.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        readonly=True,
    )
    invoice_plan_id = fields.Many2one(
        'sale.invoice.plan',
        string='Invoice Plan',
        readonly=True,
    )
    payment_id = fields.Many2one(
        'account.voucher',
        string='Payment',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY lca.id, sip.id, av.id) AS id,
                   lca.id AS loan_agreement_id,
                   sip.id AS invoice_plan_id,
                   av.id AS payment_id
            FROM loan_customer_agreement lca
            LEFT JOIN sale_order so ON lca.sale_id = so.id
            LEFT JOIN sale_invoice_plan sip ON so.id = sip.order_id
            LEFT JOIN account_invoice inv ON sip.ref_invoice_id = inv.id
            LEFT JOIN account_voucher_line avl ON inv.id = avl.invoice_id
            LEFT JOIN account_voucher av ON avl.voucher_id = av.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class JasperReportCDReceivablePaymentHistory(models.TransientModel):
    _name = 'jasper.report.cd.receivable.payment.history'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    bank_id = fields.Many2one(
        'res.bank',
        string='Bank',
    )
    bank_branch_id = fields.Many2one(
        'res.bank.branch',
        string='Bank Branch'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        self.bank_branch_id = False
        self.partner_ids = False

    @api.multi
    def _get_report_name(self):
        self.ensure_one()
        report_name = "cd_receivable_payment_history_group_by_customer"
        if len(self.bank_id):
            report_name = "cd_receivable_payment_history_group_by_bank"
        return report_name

    @api.multi
    def _get_domain(self):
        self.ensure_one()
        dom = []
        if self.partner_ids:
            dom += [('loan_agreement_id.borrower_partner_id', 'in',
                     self.partner_ids.ids)]
        if self.bank_id:
            dom += [('loan_agreement_id.bank_id.bank', '=',
                     self.bank_id.id)]
        if self.bank_branch_id:
            dom += [('loan_agreement_id.bank_id.bank_branch', '=',
                     self.bank_branch_id.id)]
        # Check for history view
        dom += [('loan_agreement_id.supplier_invoice_id.date_paid', '!=',
                 False),
                ('loan_agreement_id.supplier_invoice_id.date_paid', '<=',
                 self.date_report)]
        return dom

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        data = {'parameters': {}}
        dom = self._get_domain()
        data['ids'] = \
            self.env['cd.receivable.payment.history.view'].search(dom).ids
        date_report = datetime.strptime(self.date_report, '%Y-%m-%d')
        data['parameters']['date_report'] = date_report.strftime('%d/%m/%Y')
        user = self.env.user.with_context(lang="th_TH").display_name
        data['parameters']['user'] = user
        data['parameters']['date_run'] = time.strftime('%d/%m/%Y')
        return data

    @api.multi
    def run_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': self._get_report_name(),
            'datas': self._get_datas(),
        }
