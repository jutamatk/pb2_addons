# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField


class BudgetMonitorReport(ChartField, models.Model):
    _inherit = 'budget.monitor.report'

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )

    def _get_dimension(self):
        dimensions = super(BudgetMonitorReport, self)._get_dimension()
        dimensions += ', charge_type'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
