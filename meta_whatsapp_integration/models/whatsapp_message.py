from odoo import models, fields, api


class WhatsAppMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'WhatsApp Message'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    business_account_id = fields.Many2one('whatsapp.business.account', 'Business Account', required=True)
    message_id = fields.Char('Message ID', help='WhatsApp Message ID from Meta API')
    partner_id = fields.Many2one('res.partner', 'Contact')
    to_number = fields.Char('To Number', required=True)
    from_number = fields.Char('From Number')
    
    message_type = fields.Selection([
        ('text', 'Text'),
        ('template', 'Template'),
        ('document', 'Document'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('location', 'Location'),
        ('interactive', 'Interactive')
    ], string='Message Type', default='text')
    
    content = fields.Text('Message Content')
    template_name = fields.Char('Template Name')
    
    status = fields.Selection([
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('received', 'Received')
    ], string='Status', default='sent')
    
    direction = fields.Selection([
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound')
    ], string='Direction', default='outbound')
    
    error_message = fields.Text('Error Message')
    webhook_data = fields.Text('Webhook Data')
    
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('partner_id', 'to_number', 'message_type', 'content')
    def _compute_display_name(self):
        for record in self:
            if record.partner_id:
                name = record.partner_id.name
            else:
                name = record.to_number or record.from_number
            
            content_preview = (record.content or '')[:50]
            if len(record.content or '') > 50:
                content_preview += '...'
            
            record.display_name = f"{name} - {record.message_type} - {content_preview}"
    
    @api.model
    def process_webhook_message(self, webhook_data):
        """Process incoming webhook message from Meta"""
        try:
            # Parse webhook data and create message record
            # This would be called from webhook controller
            pass
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error processing webhook message: {str(e)}")