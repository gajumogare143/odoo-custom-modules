from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosWhatsAppReceipt(models.TransientModel):
    _name = 'pos.whatsapp.receipt'
    _description = 'Send POS Receipt via WhatsApp'

    message_type = fields.Selection([('text', 'Text'), ('template', 'Template')], default='text')
    show_text_field = fields.Boolean(compute='_compute_visibility')
    show_template_field = fields.Boolean(compute='_compute_visibility')

    @api.depends('message_type')
    def _compute_visibility(self):
        for rec in self:
            rec.show_text_field = rec.message_type == 'text'
            rec.show_template_field = rec.message_type == 'template'


    business_account_id = fields.Many2one('whatsapp.business.account', 'Business Account',
                                          required=True, default=lambda self: self._get_default_account())
    pos_order_id = fields.Many2one('pos.order', 'POS Order', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    to_number = fields.Char('WhatsApp Number', required=True)
    
    message_type = fields.Selection([
        ('text', 'Text Receipt'),
        ('template', 'Template Receipt')
    ], string='Message Type', default='text', required=True)
    
    # Text Receipt
    receipt_text = fields.Text('Receipt Text', compute='_compute_receipt_text')
    custom_message = fields.Text('Additional Message')
    
    # Template Receipt
    template_id = fields.Many2one('whatsapp.template', 'Receipt Template')
    
    @api.model
    def _get_default_account(self):
        return self.env['whatsapp.business.account'].get_default_account()
    
    @api.depends('pos_order_id')
    def _compute_receipt_text(self):
        for record in self:
            if record.pos_order_id:
                record.receipt_text = record.pos_order_id.get_receipt_text()
            else:
                record.receipt_text = ''
    
    def action_send_receipt(self):
        """Send POS receipt via WhatsApp"""
        self.ensure_one()
        
        if not self.business_account_id:
            raise UserError(_('Please select a WhatsApp Business Account.'))
        
        if self.message_type == 'text':
            message_text = self.receipt_text
            if self.custom_message:
                message_text = f"{self.custom_message}\n\n{message_text}"
            
            result = self.business_account_id.send_message(
                to_number=self.to_number,
                message_type='text',
                text=message_text
            )
        
        elif self.message_type == 'template':
            if not self.template_id:
                raise UserError(_('Please select a receipt template.'))
            
            # Prepare template parameters from POS order
            parameters = [
                self.pos_order_id.name,  # Order number
                self.pos_order_id.date_order.strftime('%d/%m/%Y'),  # Date
                f"₹{self.pos_order_id.amount_total:.2f}",  # Total amount
            ]
            
            template_payload = self.template_id.get_template_payload(parameters)
            
            result = self.business_account_id.send_message(
                to_number=self.to_number,
                message_type='template',
                template=template_payload
            )
        
        if result.get('success'):
            # Update POS order
            self.pos_order_id.write({
                'whatsapp_receipt_sent': True,
                'whatsapp_message_id': result.get('message_id')
            })
            
            # Update message with partner
            self.env['whatsapp.message'].search([
                ('message_id', '=', result.get('message_id'))
            ]).write({'partner_id': self.partner_id.id})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Receipt sent via WhatsApp successfully!'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('Failed to send receipt: %s') % result.get('error', 'Unknown error'))