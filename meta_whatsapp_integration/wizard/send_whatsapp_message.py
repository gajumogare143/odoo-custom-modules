from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SendWhatsAppMessage(models.TransientModel):
    _name = 'send.whatsapp.message'
    _description = 'Send WhatsApp Message Wizard'

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
    partner_id = fields.Many2one('res.partner', 'Contact')
    to_number = fields.Char('To Number', required=True)
    
    message_type = fields.Selection([
        ('text', 'Text Message'),
        ('template', 'Template Message')
    ], string='Message Type', default='text', required=True)
    
    # Text Message
    message_text = fields.Text('Message Text')
    
    # Template Message
    template_id = fields.Many2one('whatsapp.template', 'Template')
    template_parameters = fields.Text('Template Parameters', 
                                      help='Comma-separated parameters for template')
    template_preview = fields.Text('Template Preview', readonly=True)
    
    @api.model
    def _get_default_account(self):
        return self.env['whatsapp.business.account'].get_default_account()
    
    @api.onchange('template_id', 'template_parameters')
    def _onchange_template_preview(self):
        if self.template_id:
            parameters = []
            if self.template_parameters:
                parameters = [p.strip() for p in self.template_parameters.split(',')]
            self.template_preview = self.template_id.preview_template(parameters)
    
    def action_send_message(self):
        """Send WhatsApp message"""
        self.ensure_one()
        
        if not self.business_account_id:
            raise UserError(_('Please select a WhatsApp Business Account.'))
        
        if self.message_type == 'text':
            if not self.message_text:
                raise UserError(_('Please enter message text.'))
            
            result = self.business_account_id.send_message(
                to_number=self.to_number,
                message_type='text',
                text=self.message_text
            )
        
        elif self.message_type == 'template':
            if not self.template_id:
                raise UserError(_('Please select a template.'))
            
            parameters = []
            if self.template_parameters:
                parameters = [p.strip() for p in self.template_parameters.split(',')]
            
            template_payload = self.template_id.get_template_payload(parameters)
            
            result = self.business_account_id.send_message(
                to_number=self.to_number,
                message_type='template',
                template=template_payload
            )
        
        if result.get('success'):
            # Update partner if exists
            if self.partner_id:
                self.env['whatsapp.message'].search([
                    ('message_id', '=', result.get('message_id'))
                ]).write({'partner_id': self.partner_id.id})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('WhatsApp message sent successfully!'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('Failed to send message: %s') % result.get('error', 'Unknown error'))