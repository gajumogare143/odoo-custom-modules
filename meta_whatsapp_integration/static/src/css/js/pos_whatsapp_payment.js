/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useState } from "@odoo/owl";

patch(PaymentScreen.prototype, {

    setup() {
        super.setup();
        this.state = useState({
            whatsappNumber: "",
        });
    },

    async sendWhatsAppReceipt() {
        if (!this.state.whatsappNumber) {
            alert("Please enter WhatsApp number");
            return;
        }

        const order = this.currentOrder;

        await this.rpc({
            model: "pos.order",
            method: "action_send_whatsapp_receipt",
            args: [order.backendId, this.state.whatsappNumber],
        });

        alert("Receipt sent on WhatsApp!");
    },
});