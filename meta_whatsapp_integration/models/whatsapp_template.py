from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WhatsAppTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'WhatsApp Message Template'
    _rec_name = 'name'

    name = fields.Char('Template Name', required=True)
    template_id = fields.Char('Template ID', help='Template ID from Meta')
    business_account_id = fields.Many2one('whatsapp.business.account', 'Business Account')
    
    category = fields.Selection([
        ('AUTHENTICATION', 'Authentication'),
        ('MARKETING', 'Marketing'),
        ('UTILITY', 'Utility')
    ], string='Category', required=True, default='UTILITY')
    
    language = fields.Selection([
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('gu', 'Gujarati'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('bn', 'Bengali'),
        ('pa', 'Punjabi')
    ], string='Language', default='en', required=True)
    
    status = fields.Selection([
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
        ('DISABLED', 'Disabled')
    ], string='Status', default='PENDING', readonly=True)
    
    # Template Structure
    header_type = fields.Selection([
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document')
    ], string='Header Type')
    
    header_text = fields.Char('Header Text')
    body_text = fields.Text('Body Text', required=True)
    footer_text = fields.Char('Footer Text')
    
    # Parameters
    parameter_count = fields.Integer('Parameter Count', compute='_compute_parameter_count')
    parameter_names = fields.Text('Parameter Names', help='Comma-separated parameter names')
    
    # Buttons
    button_type = fields.Selection([
        ('QUICK_REPLY', 'Quick Reply'),
        ('CALL_TO_ACTION', 'Call to Action'),
        ('URL', 'URL')
    ], string='Button Type')
    
    button_text = fields.Char('Button Text')
    button_url = fields.Char('Button URL')
    button_phone = fields.Char('Button Phone')
    
    active = fields.Boolean('Active', default=True)
    
    @api.depends('body_text', 'header_text')
    def _compute_parameter_count(self):
        for record in self:
            count = 0
            if record.header_text:
                count += record.header_text.count('{{')
            if record.body_text:
                count += record.body_text.count('{{')
            record.parameter_count = count
    
    def get_template_payload(self, parameters=None):
        """Get template payload for Meta API"""
        self.ensure_one()
        
        payload = {
            'name': self.name,
            'language': {'code': self.language}
        }
        
        if parameters:
            components = []
            
            # Header parameters
            if self.header_text and '{{' in self.header_text:
                header_params = []
                param_count = self.header_text.count('{{')
                for i in range(param_count):
                    if i < len(parameters):
                        header_params.append({'type': 'text', 'text': parameters[i]})
                
                if header_params:
                    components.append({
                        'type': 'header',
                        'parameters': header_params
                    })
            
            # Body parameters
            if self.body_text and '{{' in self.body_text:
                body_params = []
                param_count = self.body_text.count('{{')
                start_idx = len(components[0]['parameters']) if components else 0
                
                for i in range(param_count):
                    param_idx = start_idx + i
                    if param_idx < len(parameters):
                        body_params.append({'type': 'text', 'text': parameters[param_idx]})
                
                if body_params:
                    components.append({
                        'type': 'body',
                        'parameters': body_params
                    })
            
            if components:
                payload['components'] = components
        
        return payload
    
    def preview_template(self, parameters=None):
        """Preview template with parameters"""
        self.ensure_one()
        
        preview_text = self.body_text or ''
        
        if parameters:
            # Replace parameters in preview
            param_list = parameters if isinstance(parameters, list) else parameters.split(',')
            for i, param in enumerate(param_list):
                preview_text = preview_text.replace(f'{{{{{i+1}}}}}', param.strip())
        
        return preview_text