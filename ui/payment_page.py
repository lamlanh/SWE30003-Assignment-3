import streamlit as st


PAYMENT_METHODS = {
    "Card": "card",
    "Bank Transfer": "bank_transfer",
    "Cash": "cash",
}


def _status_badge(status: str) -> str:
    css_class = f"badge-{status.lower()}"
    return f"<span class='{css_class}'>{status}</span>"


def render(system) -> None:
    """
    Render the Payment Processing page.

    Args:
        system: The initialised SmartFM system. Uses system.payment_processor
                and system.order_manager (the latter only for the
                Staff/Admin "generate invoice" flow).
    """
    st.markdown("# 💳 Process Payment & Receipt")
    st.divider()

    payment_processor = system.payment_processor
    if payment_processor is None:
        st.error("Payment system is not available yet.")
        return

    current_user = st.session_state.get("current_user") or {}
    role = current_user.get("role", "")

    if role == "CUSTOMER":
        customer_id = current_user["customer_data"].customer_id
        if not customer_id:
            st.error("Could not determine your customer account. Please log in again.")
            return
    else:
        customer_id = None  # staff/admin see everyone's invoices by default

    tab_names = ["💵 Unpaid Invoices"]
    if role in ("STAFF", "ADMIN"):
        tab_names.append("🧾 Generate Invoice")
    tabs = st.tabs(tab_names)

    # -------------------------------------------------------------------
    # Tab 1 — Unpaid invoices → pay → receipt
    # -------------------------------------------------------------------
    with tabs[0]:
        unpaid = payment_processor.list_unpaid_invoices()
        if customer_id:
            unpaid = [inv for inv in unpaid if inv.customer_id == customer_id]

        if not unpaid:
            st.info("No unpaid invoices.")
        else:
            for inv in unpaid:
                with st.container():
                    st.markdown(
                        f"**{inv.invoice_id}** — {inv.amount_vnd:,.0f} VND "
                        f"{_status_badge(inv.status)}",
                        unsafe_allow_html=True
                    )
                    st.caption(
                        f"Order: {inv.order_id} · Customer: {inv.customer_id} · "
                        f"Issued: {inv.date_issued}"
                    )

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        method_label = st.selectbox(
                            "Payment method",
                            list(PAYMENT_METHODS.keys()),
                            key=f"method_{inv.invoice_id}"
                        )
                    with col2:
                        st.write("")  # vertical spacer to align the button
                        pay_clicked = st.button(
                            "Pay Now", key=f"pay_{inv.invoice_id}",
                            use_container_width=True
                        )

                    if pay_clicked:
                        try:
                            receipt = payment_processor.process_payment(
                                inv.invoice_id,
                                payment_method=PAYMENT_METHODS[method_label]
                            )
                            st.success(
                                f"✅ Payment successful — receipt "
                                f"**{receipt.receipt_id}** generated."
                            )
                            with st.expander("View Receipt", expanded=True):
                                st.markdown(f"**Receipt ID:** {receipt.receipt_id}")
                                st.markdown(f"**Invoice ID:** {receipt.invoice_id}")
                                st.markdown(f"**Amount:** {receipt.amount_vnd:,.0f} VND")
                                st.markdown(f"**Payment Method:** {receipt.payment_method}")
                                st.markdown(f"**Customer:** {receipt.customer_id}")
                        except Exception as e:
                            st.error(f"Payment failed: {e}")

                    st.divider()

    # -------------------------------------------------------------------
    # Tab 2 — Generate invoice for an order (Staff/Admin only)
    # -------------------------------------------------------------------
    if role in ("STAFF", "ADMIN"):
        with tabs[1]:
            order_manager = system.order_manager
            if order_manager is None:
                st.error("Order system is not available yet.")
                return

            # Only orders without an invoice yet are eligible
            eligible_orders = [
                o for o in order_manager.list_orders()
                if o.status in ("PENDING", "CONFIRMED") and not o.invoice_id
            ]

            if not eligible_orders:
                st.info("No orders currently need an invoice.")
            else:
                options = {
                    f"{o.order_id} — {o.cargo_description} ({o.customer_id})": o
                    for o in eligible_orders
                }
                choice = st.selectbox("Select order", list(options.keys()))
                amount_vnd = st.number_input(
                    "Invoice Amount (VND)", min_value=0.0, step=10000.0
                )

                if st.button("Generate Invoice", use_container_width=True):
                    if amount_vnd <= 0:
                        st.error("Invoice amount must be greater than 0.")
                    else:
                        try:
                            order = options[choice]
                            invoice = payment_processor.create_invoice(order, amount_vnd)
                            st.success(
                                f"✅ Invoice **{invoice.invoice_id}** created for "
                                f"order {invoice.order_id}."
                            )
                        except Exception as e:
                            st.error(f"Could not create invoice: {e}")