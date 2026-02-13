from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_whatsapp_quotation(self):
        self.ensure_one()

        if not self.partner_id.whatsapp_number:
            raise UserError("Customer WhatsApp number not found.")

        account = self.env['whatsapp.business.account'].get_default_account()
        if not account:
            raise UserError("No default WhatsApp Business Account found.")

        # Generate PDF
        report = self.env.ref('sale.action_report_saleorder')
        pdf_content, _ = report._render_qweb_pdf(self.id)
        pdf_base64 = base64.b64encode(pdf_content).decode()

        result = account.send_message(
            to_number=self.partner_id.whatsapp_number,
            message_type='document',
            document={
                "filename": f"{self.name}.pdf",
                "document": pdf_base64,
                "caption": f"Quotation {self.name}"
            }
        )

        if not result.get('success'):
            raise UserError(result.get('error'))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Quotation sent successfully on WhatsApp!',
                'type': 'success',
            }
        }