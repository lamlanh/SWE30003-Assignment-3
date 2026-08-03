import streamlit as st


# ---------------------------------------------------------------------------
# Status badge helper (reuses the badge-* CSS classes defined in app.py)
# ---------------------------------------------------------------------------
def _status_badge(status: str) -> str:
    css_class = f"badge-{status.lower()}"
    return f"<span class='{css_class}'>{status}</span>"


def render(system) -> None:
    """
    Render the Place Shipment Order page.

    Args:
        system: The initialised SmartFM system. Uses system.order_manager.
    """
    st.markdown("# 📦 Place Shipment Order")
    st.divider()

    order_manager = system.order_manager
    if order_manager is None:
        st.error("Order system is not available yet.")
        return

    current_user = st.session_state.get("current_user") or {}
    role = current_user.get("role", "")

    # -------------------------------------------------------------------
    # Work out which customer this page is acting on behalf of
    # -------------------------------------------------------------------
    if role == "CUSTOMER":
        customer_id = current_user["customer_data"].customer_id
        if not customer_id:
            st.error("Could not determine your customer account. Please log in again.")
            return
        st.caption(f"Placing order as customer **{customer_id}**.")
    else:
        # Staff/Admin can place an order on behalf of any customer.
        customer_id = st.text_input(
            "Customer ID (e.g. CUST-001)",
            key="order_customer_id_input",
            help="Enter the customer this order is being placed for."
        )

    tab_new, tab_history = st.tabs(["📝 New Order", "📋 Order History"])

    # -------------------------------------------------------------------
    # Tab 1 — New order form
    # -------------------------------------------------------------------
    with tab_new:
        with st.form("new_order_form", clear_on_submit=True):
            cargo_description = st.text_area("Cargo Description")
            cargo_weight_kg = st.number_input(
                "Cargo Weight (kg)", min_value=0.0, step=1.0
            )
            col1, col2 = st.columns(2)
            with col1:
                pickup_address = st.text_input("Pickup Address")
            with col2:
                delivery_address = st.text_input("Delivery Address")
            preferred_date = st.date_input("Preferred Pickup Date")

            submitted = st.form_submit_button("Submit Order", use_container_width=True)

        if submitted:
            if not customer_id:
                st.error("A customer ID is required before an order can be placed.")
            elif not cargo_description.strip():
                st.error("Cargo description cannot be empty.")
            elif not pickup_address.strip() or not delivery_address.strip():
                st.error("Pickup and delivery addresses are required.")
            else:
                try:
                    order = order_manager.create_order(
                        customer_id=customer_id,
                        cargo_description=cargo_description.strip(),
                        cargo_weight_kg=cargo_weight_kg,
                        pickup_address=pickup_address.strip(),
                        delivery_address=delivery_address.strip(),
                        preferred_date=preferred_date.strftime("%Y-%m-%d"),
                    )
                    st.success(f"✅ Order **{order.order_id}** created successfully.")
                except Exception as e:
                    st.error(f"Could not create order: {e}")

    # -------------------------------------------------------------------
    # Tab 2 — Order history
    # -------------------------------------------------------------------
    with tab_history:
        if role == "CUSTOMER":
            orders = order_manager.list_orders_for_customer(customer_id) if customer_id else []
        else:
            orders = order_manager.list_orders()
            if customer_id:
                orders = [o for o in orders if o.customer_id == customer_id]

        if not orders:
            st.info("No orders found.")
        else:
            for o in sorted(orders, key=lambda x: x.created_date, reverse=True):
                with st.container():
                    st.markdown(
                        f"**{o.order_id}** — {o.cargo_description} "
                        f"({o.cargo_weight_kg:g} kg)  {_status_badge(o.status)}",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"🚚 {o.pickup_address}  →  {o.delivery_address}")
                    st.caption(
                        f"Preferred date: {o.preferred_date} · "
                        f"Placed: {o.created_date} · Customer: {o.customer_id}"
                    )

                    if o.status == "PENDING":
                        if st.button("❌ Cancel Order", key=f"cancel_{o.order_id}"):
                            try:
                                order_manager.cancel_order(o.order_id)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not cancel order: {e}")

                    st.divider()