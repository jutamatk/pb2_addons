# -*- coding: utf-8 -*-
import time
from openerp import fields, models, api
from openerp import tools


class BudgetCarryOver(models.Model):
    _name = 'budget.carry.over'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    doctype = fields.Selection(
        [('all', 'All'),
         ('purchase_request', 'Purchase Request'),
         ('sale_order', 'Sales Order'),
         ('purchase_order', 'Purchase Order'),
         ('employee_expense', 'Expense'), ],
        string='Document Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Carry to Fiscal Year',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    line_ids = fields.One2many(
        'budget.carry.over.line',
        'carry_over_id',
        string='Carry Over Lines',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    line_view_ids = fields.One2many(
        'budget.carry.over.line.view',
        'carry_over_id',
        string='Carry Over Lines',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        default='draft',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
    )

    @api.multi
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('commit_amount'))

    @api.model
    def default_get(self, fields):
        res = super(BudgetCarryOver, self).default_get(fields)
        Fiscal = self.env['account.fiscalyear']
        if not res.get('fiscalyear_id', False):
            fiscals = Fiscal.search([
                ('date_start', '>', time.strftime('%Y-%m-%d'))],
                order='date_start')
            if fiscals:
                res['fiscalyear_id'] = fiscals[0].id
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetCarryOver, self).write(vals)
        if 'doctype' in vals or 'fiscalyear_id' in vals:
            self.compute_commit_docs()
        return res

    @api.model
    def create(self, vals):
        res = super(BudgetCarryOver, self).create(vals)
        res.name = '{:03d}'.format(res.id)
        res.compute_commit_docs()
        return res

    @api.multi
    def compute_commit_docs(self):
        """ This method, based on criteria, list all documents with,
        - Doctype as selected
        - commit_amount > 0
        - fiscalyear before selected year only
        """
        self = self.sudo()
        for rec in self:
            rec.line_ids.unlink()
            lines = []
            doctypes = [rec.doctype]
            if rec.doctype == 'all':
                doctypes = ['purchase_request', 'sale_order',
                            'purchase_order', 'employee_expense']
            self._cr.execute("""
            select * from (
                select doctype, document, document_line,
                    purchase_request_line_id, sale_line_id,
                    purchase_line_id, expense_line_id,
                    sum(amount_consumed) amount_consumed
                from budget_consume_report rpt
                join account_fiscalyear fiscal
                    on rpt.fiscalyear_id = fiscal.id
                where fiscal.date_start < %s and doctype in %s
                and rpt.budget_commit_type != 'actual'
                group by doctype, document, document_line,
                    purchase_request_line_id, sale_line_id,
                    purchase_line_id, expense_line_id) a
            where a.amount_consumed > 0
            """, (rec.fiscalyear_id.date_start, tuple(doctypes)))
            result = self._cr.dictfetchall()
            for r in result:
                vals = {
                    'doctype': r['doctype'],
                    'name': r['document'],
                    'description': r['document_line'],
                    'purchase_request_line_id': r['purchase_request_line_id'],
                    'sale_line_id': r['sale_line_id'],
                    'purchase_line_id': r['purchase_line_id'],
                    'expense_line_id': r['expense_line_id'],
                    'commit_amount': r['amount_consumed'], }
                lines.append((0, 0, vals))
            rec.write({'line_ids': lines})

    @api.multi
    def action_carry_over(self):
        self = self.sudo()
        for rec in self:
            sale_lines = rec.line_ids.mapped('sale_line_id')
            request_lines = \
                rec.line_ids.mapped('purchase_request_line_id')
            expense_lines = rec.line_ids.mapped('expense_line_id')
            purchase_lines = rec.line_ids.mapped('purchase_line_id')
            # All commits
            commits = sale_lines.mapped('budget_commit_ids') + \
                purchase_lines.mapped('budget_commit_ids') + \
                request_lines.mapped('budget_commit_ids') + \
                expense_lines.mapped('budget_commit_ids')
            commits.write({'monitor_fy_id': rec.fiscalyear_id.id})
        self.write({'state': 'done'})


class BudgetCarryOverLine(models.Model):
    _name = 'budget.carry.over.line'

    doctype = fields.Selection(
        [('purchase_request', 'Purchase Request'),
         ('sale_order', 'Sales Order'),
         ('purchase_order', 'Purchase Order'),
         ('employee_expense', 'Expense'), ],
        string='Document Type',
        readonly=True,
    )
    carry_over_id = fields.Many2one(
        'budget.carry.over',
        string='Carry Over',
        index=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Document',
        readonly=True,
    )
    description = fields.Char(
        string='Description',
        readonly=True,
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        compute='_compute_chartfield',
        store=True,
    )
    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string='Purchase Request Line',
        readonly=True,
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
        readonly=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        readonly=True,
    )
    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
        readonly=True,
    )
    commit_amount = fields.Float(
        string='Commitment',
        readonly=True,
    )

    @api.multi
    @api.depends('purchase_request_line_id', 'sale_line_id',
                 'purchase_line_id', 'expense_line_id')
    def _compute_chartfield(self):
        for rec in self:
            doc_line = rec.expense_line_id or \
                rec.purchase_request_line_id or \
                rec.purchase_line_id or rec.sale_line_id
            rec.chartfield_id = doc_line.chartfield_id


class BudgetCarryOverLineView(models.Model):
    _name = 'budget.carry.over.line.view'
    _auto = False
    _order = 'name'

    carry_over_id = fields.Many2one(
        'budget.carry.over',
        string='Carry Over',
        readonly=True,
    )
    budget_id = fields.Reference(
        [('res.section', 'Section'),
         ('res.project', 'Project'),
         ('res.invest.asset', 'Asset'),
         ('res.invest.construction.phase', 'Construction'),
         ('res.personnel.costcenter', 'Personnel')],
        string='Document Line',
        compute='_compute_budget_id',
        readonly=True,
    )
    doctype = fields.Selection(
        [('purchase_request', 'Purchase Request'),
         ('sale_order', 'Sales Order'),
         ('purchase_order', 'Purchase Order'),
         ('employee_expense', 'Expense'), ],
        string='Document Type',
        readonly=True,
    )
    name = fields.Char(
        string='Name',
        readonly=True,
    )
    description = fields.Char(
        string='Description',
        readonly=True,
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        readonly=True,
    )
    chartfield_type = fields.Selection(
        [('sc:', 'Section'),
         ('pj:', 'Project'),
         ('cp:', 'Construction Phase'),
         ('ia:', 'Invest Asset'),
         ('pc:', 'Personnel'), ],
        string='Type',
        related='chartfield_id.type',
    )
    commit_amount = fields.Float(
        string='Commitment',
        readonly=True,
    )

    @api.multi
    def _compute_budget_id(self):
        for rec in self:
            rec.budget_id = '%s,%s' % (rec.chartfield_id.model,
                                       rec.chartfield_id.res_id)

    def _get_sql_view(self):
        sql_view = """
            SELECT id, doctype, carry_over_id,
                commit_amount, name, description, chartfield_id
            FROM budget_carry_over_line
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(), ))
