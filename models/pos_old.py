# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_verify_delivery = fields.Boolean(string='Home Delivery')

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_home_delivery = fields.Boolean('Use as Home Delivery', help='if you use this journal as home delivery, it will not create any payment entries for that order')

class PosOrder(models.Model):
    _inherit = 'pos.order'
    _description = "Point of Sale Orders"

    def _check_journal(self, orders):
        # check journal is home delivery True
        for st in orders.get('statement_ids'):
            journal = self.env['account.journal'].browse(st[2].get('journal_id'))
            if journal and not journal.is_home_delivery:
                return False
        return True

    

############################################# 222222222222222222 ###########################################################################

    @api.model
    def _process_order(self, pos_order):    
		# call super    
		journal_list = self.env['account.journal']    
		for payments in pos_order['statement_ids']:        
			journal_list |= self.env['account.journal'].browse(payments[2].get('journal_id'))    
		if journal_list.filtered(lambda x: not x.is_home_delivery):        
			super(PosOrder, self)._process_order(pos_order)    
		else:        
			# call my updated code        
			prec_acc = self.env['decimal.precision'].precision_get('Account')        
			pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])        

			if pos_session.state == 'closing_control' or pos_session.state == 'closed':            
				pos_order['pos_session_id'] = self._get_valid_session(pos_order).id        
			order = self.create(self._order_fields(pos_order))        
			journal_ids = set()        
			for payments in pos_order['statement_ids']:            
				delivery_journal = self.env['account.journal'].browse(payments[2].get('journal_id'))            
				if delivery_journal and not delivery_journal.is_home_delivery:                
					if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):                    
						order.add_payment(self._payment_fields(payments[2]))            
				journal_ids.add(payments[2].get('journal_id'))        
			if pos_session.sequence_number <= pos_order['sequence_number']:            
				pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})            
				pos_session.refresh()        
			if not float_is_zero(pos_order['amount_return'], prec_acc):            
				cash_journal_id = pos_session.cash_journal_id.id            
				if not cash_journal_id:                
					# Select for change one of the cash journals used in this                
					# payment                
					cash_journal = self.env['account.journal'].search([('type', '=', 'cash'),('id', 'in', list(journal_ids)),], limit=1)                
					
					if not cash_journal:                    
						# If none, select for change one of the cash journals of the POS                    
						# This is used for example when a customer pays by credit card                    
						# an amount higher than total amount of the order and gets cash back                    
						cash_journal = [statement.journal_id for statement in pos_session.statement_ids if statement.journal_id.type == 'cash']                    
						if not cash_journal:                        
							raise UserError(_("No cash statement found for this session. Unable to record returned cash."))                
					cash_journal_id = cash_journal[0].id            
				
				order.add_payment({                
					'amount': -pos_order['amount_return'],                
					'payment_date': fields.Datetime.now(),                
					'payment_name': _('return'),                
					'journal': cash_journal_id,            
				})        
				return order


############################################# 222222222222222222 end ###########################################################################


############################################# 111111111111111111 ###########################################################################
    '''@api.model    
    def _process_order(self, pos_order):        
        # call super        
        journal_list = self.env['account.journal']        
        for payments in pos_order['statement_ids']:            
            journal_list |= self.env['account.journal'].browse(payments[2].get('journal_id'))        
        if journal_list.filtered(lambda x: not x.is_home_delivery):            
            super(PosOrder, self)._process_order(pos_order)        
        
        # call my updated code        
        prec_acc = self.env['decimal.precision'].precision_get('Account')        
        pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])        
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':            
            pos_order['pos_session_id'] = self._get_valid_session(pos_order).id        
        order = self.create(self._order_fields(pos_order))        
        journal_ids = set()        
        for payments in pos_order['statement_ids']:            
            delivery_journal = self.env['account.journal'].browse(payments[2].get('journal_id'))            
            if delivery_journal and not delivery_journal.is_home_delivery:                
                if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):                    
                    order.add_payment(self._payment_fields(payments[2]))            
            journal_ids.add(payments[2].get('journal_id'))        
        if pos_session.sequence_number <= pos_order['sequence_number']:            
            pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})            
            pos_session.refresh()        
        if not float_is_zero(pos_order['amount_return'], prec_acc):            
            cash_journal_id = pos_session.cash_journal_id.id            
            
            if not cash_journal_id:                
                # Select for change one of the cash journals used in this                
                # payment                
                cash_journal = self.env['account.journal'].search([('type', '=', 'cash'),('id', 'in', list(journal_ids)),], limit=1)                
            
            if not cash_journal:                    
                # If none, select for change one of the cash journals of the POS                    
                # This is used for example when a customer pays by credit card                    
                # an amount higher than total amount of the order and gets cash back                    
                cash_journal = [statement.journal_id for statement in pos_session.statement_ids if statement.journal_id.type == 'cash']                    
            
            if not cash_journal:                        
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))                
            cash_journal_id = cash_journal[0].id            
            
            order.add_payment({                
                'amount': -pos_order['amount_return'],                
                'payment_date': fields.Datetime.now(),                
                'payment_name': _('return'),                
                'journal': cash_journal_id,            
            })        
            
            return order'''
#################################################1111111111111 end #######################################################################    


############################################### 0000000000000 #########################################################################     
    '''@api.model
    def _process_order(self, pos_order):
        prec_acc = self.env['decimal.precision'].precision_get('Account')
        pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            pos_order['pos_session_id'] = self._get_valid_session(pos_order).id
        order = self.create(self._order_fields(pos_order))
        journal_ids = set()
        for payments in pos_order['statement_ids']:
            delivery_journal = self.env['account.journal'].browse(payments[2].get('journal_id'))
            if delivery_journal and not delivery_journal.is_home_delivery:
                if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                    order.add_payment(self._payment_fields(payments[2]))
            journal_ids.add(payments[2].get('journal_id'))
        if pos_session.sequence_number <= pos_order['sequence_number']:
            pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})
            pos_session.refresh()

        if not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_journal_id = pos_session.cash_journal_id.id
            if not cash_journal_id:
                # Select for change one of the cash journals used in this
                # payment
                cash_journal = self.env['account.journal'].search([
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1)
                if not cash_journal:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal = [statement.journal_id for statement in pos_session.statement_ids if statement.journal_id.type == 'cash']
                    if not cash_journal:
                        raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                cash_journal_id = cash_journal[0].id
            order.add_payment({
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Datetime.now(),
                'payment_name': _('return'),
                'journal': cash_journal_id,
            })
        return order'''

############################################### 0000000000000 end #########################################################################

    
    @api.model
    def create_from_ui(self, orders):
        pos_order_ids = super(PosOrder, self).create_from_ui(orders)
        for order in pos_order_ids:
            order_rec = self.browse(order)
            ref_order = [o['data'] for o in orders if o['data'].get('name') == order_rec.pos_reference]
            if ref_order:
                to_invoice = all([o['to_invoice'] for o in orders if o['data'].get('name') == order_rec.pos_reference])
                is_delivery = self._check_journal(ref_order[0])
                if is_delivery and not to_invoice:
                    order_rec.write({'state': 'done'})
            delivery_ids = self.env['pos.delivery.order'].sudo().search([('order_no', '=', order_rec.pos_reference)])
            if delivery_ids:
                delivery_ids.write({'pos_order_id': order})
        return pos_order_ids
    
    
    
    def test_paid(self):
        for order in self:
            pos_session = self.env['pos.session'].browse(order.session_id.id)
            for payments in pos_session.statement_ids:
                if payments.journal_id and not payments.journal_id.is_home_delivery:
                    continue
                if payments.journal_id and payments.journal_id.is_home_delivery:
                    return True
        return super(PosOrder, self).test_paid()
