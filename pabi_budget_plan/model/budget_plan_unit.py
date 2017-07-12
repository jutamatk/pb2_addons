# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class BudgetPlanUnit(BPCommon, LogCommon, models.Model):
    _name = 'budget.plan.unit'
    _inherit = ['mail.thread']
    _description = "Unit - Budget Plan"

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    plan_summary_revenue_line_ids = fields.One2many(
        'budget.plan.unit.summary',
        'plan_id',
        string='Summary by Activity Group',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
        help="Summary by Activity Group View",
    )
    plan_summary_expense_line_ids = fields.One2many(
        'budget.plan.unit.summary',
        'plan_id',
        string='Summary by Activity Group',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
        help="Summary by Activity Group View",
    )
    # Select Dimension - Section
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='section_id.org_id',
        readonly=True,
        store=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        related='section_id.division_id',
        readonly=True,
        store=True,
    )

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('section_id')._ids
        # Find sections
        sections = self.env['res.section'].search([('id', 'not in', _ids)])
        plan_ids = []
        for section in sections:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'section_id': section.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids


class BudgetPlanUnitLine(BPLMonthCommon, ActivityCommon, models.Model):
    _name = 'budget.plan.unit.line'
    _description = "Unit - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='unit_base',  # Unit
    )
    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    section_id = fields.Many2one(
        related='plan_id.section_id',
        store=True,
        readonly=True,
    )
    unit = fields.Float(
        string='Unit',
    )
    activity_unit_price = fields.Float(
        string='Unit Price',
    )
    activity_unit = fields.Float(
        string='Activity Unit',
    )
    total_budget = fields.Float(
        string='Total Budget',
    )

    @api.multi
    def _write(self, vals):  # Use _write, as it triggered on related field
        res = super(BudgetPlanUnitLine, self)._write(vals)
        print self.section_id
        if not self._context.get('MyModelLoopBreaker', False):
            self.update_related_dimension({'section_id': self.section_id.id})
        return res


class BudgetPlanUnitSummary(models.Model):
    _name = 'budget.plan.unit.summary'
    _auto = False
    _order = 'budget_method desc, activity_group_id'

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    m1 = fields.Float(
        string='Oct',
    )
    m2 = fields.Float(
        string='Nov',
    )
    m3 = fields.Float(
        string='Dec',
    )
    m4 = fields.Float(
        string='Jan',
    )
    m5 = fields.Float(
        string='Feb',
    )
    m6 = fields.Float(
        string='Mar',
    )
    m7 = fields.Float(
        string='Apr',
    )
    m8 = fields.Float(
        string='May',
    )
    m9 = fields.Float(
        string='Jun',
    )
    m10 = fields.Float(
        string='July',
    )
    m11 = fields.Float(
        string='Aug',
    )
    m12 = fields.Float(
        string='Sep',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select min(id) id, plan_id, activity_group_id, budget_method,
            sum(m1) m1, sum(m2) m2, sum(m3) m3, sum(m4) m4,
            sum(m5) m5, sum(m6) m6, sum(m7) m7, sum(m8) m8, sum(m9) m9,
            sum(m10) m10, sum(m11) m11, sum(m12) m12,
            sum(planned_amount) planned_amount
            from budget_plan_unit_line l
            group by plan_id, activity_group_id, budget_method
        )""" % (self._table, ))
