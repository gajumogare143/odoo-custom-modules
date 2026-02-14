class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_send_whatsapp_po(self):
        self.ensure_one()

        if not self.partner_id.whatsapp_number:
            raise UserError("Vendor WhatsApp number not found.")

        account = self.env['whatsapp.business.account'].get_default_account()

        report = self.env.ref('purchase.action_report_purchase_order')
        pdf_content, _ = report._render_qweb_pdf(self.id)
        pdf_base64 = base64.b64encode(pdf_content).decode()

        result = account.send_message(
            to_number=self.partner_id.whatsapp_number,
            message_type='document',
            document={
                "filename": f"{self.name}.pdf",
                "document": pdf_base64,
                "caption": f"Purchase Order {self.name}"
            }
        )

        if not result.get('success'):
            raise UserError(result.get('error'))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Purchase Order sent successfully on WhatsApp!',
                'type': 'success',
            }
        }
