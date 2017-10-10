# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.tools import float_compare
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def validate(self):
        # Dr / Cr should be non zero
        self.validate_drcr_amount()
        self.validate_period_vs_date()
        res = super(AccountMove, self).validate()
        return res

    @api.multi
    def validate_drcr_amount(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        for rec in self:
            lines = rec.line_id
            if not lines:
                continue
            debit = sum(lines.mapped('debit'))
            credit = sum(lines.mapped('credit'))
            if not debit or not credit:
                raise ValidationError(
                    _('Zero amount on Dr/Cr on entry, %s') % rec.ref)
            if float_compare(debit, credit, prec) != 0:
                raise ValidationError(
                    _('Entry not balance, %s') % rec.ref)

    @api.multi
    def validate_period_vs_date(self):
        Period = self.env['account.period']
        for rec in self:
            valid_period = Period.find(dt=rec.date)
            if rec.period_id != valid_period:
                raise ValidationError(
                    _('Period and date conflict on entry, %s') % rec.ref)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
