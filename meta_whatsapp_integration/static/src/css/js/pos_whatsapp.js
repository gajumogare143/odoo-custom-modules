/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { useService } from "@web/core/utils/hooks";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    async sendWhatsAppReceipt() {
        const order = this.currentOrder;
        
        if (!order.get_partner()) {
            this.notification.add("Please select a customer first.", {
                type: "warning",
            });
            return;
        }

        if (!order.get_partner().whatsapp_number) {
            this.notification.add("Customer doesn't have a WhatsApp number.", {
                type: "warning",
            });
            return;
        }

        try {
            const result = await this.orm.call(
                "pos.order",
                "action_send_whatsapp_receipt",
                [order.backendId]
            );
            
            if (result && result.type === "ir.actions.act_window") {
                // Open wizard
                this.env.services.action.doAction(result);
            }
        } catch (error) {
            console.error("Error sending WhatsApp receipt:", error);
            this.notification.add("Failed to send WhatsApp receipt.", {
                type: "danger",
            });
        }
    },
});