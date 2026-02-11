from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_number = fields.Char('WhatsApp Number', help='WhatsApp number with country code')
    whatsapp_opt_in = fields.Boolean('WhatsApp Opt-in', default=False,
                                     help='Customer has opted in for WhatsApp messages')
    whatsapp_message_count = fields.Integer('WhatsApp Messages', compute='_compute_whatsapp_message_count')
    
    @api.depends('whatsapp_number')
    def _compute_whatsapp_message_count(self):
        for partner in self:
            if partner.whatsapp_number:
                count = self.env['whatsapp.message'].search_count([
                    '|', ('to_number', '=', partner.whatsapp_number),
                         ('from_number', '=', partner.whatsapp_number)
                ])
                partner.whatsapp_message_count = count
            else:
                partner.whatsapp_message_count = 0
    
    @api.constrains('whatsapp_number')
    def _check_whatsapp_number(self):
        for partner in self:
            if partner.whatsapp_number:
                # Basic validation for WhatsApp number
                clean_number = re.sub(r'[^\d+]', '', partner.whatsapp_number)
                if not re.match(r'^\+?[1-9]\d{1,14}$', clean_number):
                    raise UserError(_('Please enter a valid WhatsApp number with country code.'))
    
    def action_send_whatsapp_message(self):
        """Open wizard to send WhatsApp message"""
        self.ensure_one()
        
        if not self.whatsapp_number:
            raise UserError(_('No WhatsApp number found for this contact.'))
        
        if not self.whatsapp_opt_in:
            raise UserError(_('Customer has not opted in for WhatsApp messages.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send WhatsApp Message'),
            'res_model': 'send.whatsapp.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_to_number': self.whatsapp_number,
            }
        }
    
    def action_view_whatsapp_messages(self):
        """View WhatsApp messages for this contact"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('WhatsApp Messages'),
            'res_model': 'whatsapp.message',
            'view_mode': 'tree,form',
            'domain': [
                '|', ('to_number', '=', self.whatsapp_number),
                     ('from_number', '=', self.whatsapp_number)
            ],
            'context': {'default_partner_id': self.id}
        }
    
    @api.model
    def find_partner_by_whatsapp(self, whatsapp_number):
        """Find partner by WhatsApp number"""
        clean_number = re.sub(r'[^\d+]', '', whatsapp_number)
        
        # Try exact match first
        partner = self.search([('whatsapp_number', '=', clean_number)], limit=1)
        
        if not partner:
            # Try without country code
            if clean_number.startswith('91') and len(clean_number) > 10:
                local_number = clean_number[2:]
                partner = self.search([('whatsapp_number', 'ilike', local_number)], limit=1)
        
        return partner