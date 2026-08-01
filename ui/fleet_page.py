import streamlit as st
from datetime import date


def render(system) -> None:
    """
    Render the Fleet Dispatch page.

    Args:
        system: The initialised SmartFMSystem instance.
    """
    # Access control — staff and admin only
    role = st.session_state.get("role", "")
    if not st.session_state.get("logged_in") or role not in ("STAFF", "ADMIN"):
        st.error("🔒 Access denied. This page is for Staff and Admin only.")
        st.info("Please log in with a staff account from the Customer Account page.")
        return

    fleet    = system.fleet_manager
    shipment = system.shipment_manager
    orders   = system.order_manager

    st.markdown("# 🚛 Fleet Dispatch")
    st.markdown("*Manage vehicles, drivers, and assign resources to orders.*")
    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🚗 Vehicles",
        "👷 Drivers",
        "📋 Dispatch",
        "📍 Tracking"
    ])

    # -----------------------------------------------------------------------
    # TAB 1 — Fleet Overview
    # -----------------------------------------------------------------------
    with tab1:
        _render_overview(fleet)

    # -----------------------------------------------------------------------
    # TAB 2 — Vehicles
    # -----------------------------------------------------------------------
    with tab2:
        _render_vehicles(fleet)

    # -----------------------------------------------------------------------
    # TAB 3 — Drivers
    # -----------------------------------------------------------------------
    with tab3:
        _render_drivers(fleet)

    # -----------------------------------------------------------------------
    # TAB 4 — Dispatch
    # -----------------------------------------------------------------------
    with tab4:
        _render_dispatch(fleet, shipment, orders)

    # -----------------------------------------------------------------------
    # TAB 5 — Shipment Tracking
    # -----------------------------------------------------------------------
    with tab5:
        _render_tracking(shipment, fleet, orders)


# ---------------------------------------------------------------------------
# Tab 1 — Overview
# ---------------------------------------------------------------------------
def _render_overview(fleet) -> None:
    """Render fleet summary metrics."""
    st.markdown("### 📊 Fleet Overview")

    summary = fleet.get_fleet_summary()

    # Vehicle metrics
    st.markdown("#### 🚗 Vehicles")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total",       summary["total_vehicles"])
    col2.metric("✅ Available", summary["available_vehicles"])
    col3.metric("🔵 Assigned",  summary["assigned_vehicles"])
    col4.metric("🔴 Maintenance",summary["maintenance_vehicles"])

    st.divider()

    # Driver metrics
    st.markdown("#### 👷 Drivers")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total",       summary["total_drivers"])
    col6.metric("✅ Available", summary["available_drivers"])
    col7.metric("🔵 Assigned",  summary["assigned_drivers"])
    col8.metric("🟡 On Leave",  summary["on_leave_drivers"])

    st.divider()

    # Branch info
    branches = fleet.get_all_branches()
    if branches:
        st.markdown("#### 🏢 Branches")
        for b in branches:
            st.markdown(
                f"<div style='background:#1e2130;padding:12px;border-radius:8px;"
                f"border:1px solid #2d3147;margin:4px 0'>"
                f"<b>{b.name}</b> ({b.branch_id}) — {b.region}<br>"
                f"📍 {b.address} | ☎️ {b.phone}</div>",
                unsafe_allow_html=True
            )


# ---------------------------------------------------------------------------
# Tab 2 — Vehicles
# ---------------------------------------------------------------------------
def _render_vehicles(fleet) -> None:
    """Render vehicle list, add vehicle form, and status update."""
    st.markdown("### 🚗 Vehicle Management")

    # ── View all vehicles ──
    vehicles = fleet.get_all_vehicles()
    if not vehicles:
        st.info("No vehicles in the fleet yet.")
    else:
        st.markdown(f"**{len(vehicles)} vehicle(s) registered**")
        for v in vehicles:
            status_color = {
                "AVAILABLE"  : "#10b981",
                "ASSIGNED"   : "#3b82f6",
                "MAINTENANCE": "#ef4444"
            }.get(v.status, "#888")

            with st.expander(
                f"🚗 {v.vehicle_id} — {v.registration} "
                f"| {v.vehicle_type} | {v.capacity_kg:,.0f} kg"
            ):
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**ID:** {v.vehicle_id}")
                col2.markdown(f"**Registration:** {v.registration}")
                col3.markdown(
                    f"**Status:** <span style='color:{status_color}'>"
                    f"● {v.status}</span>",
                    unsafe_allow_html=True
                )
                col4, col5, col6 = st.columns(3)
                col4.markdown(f"**Type:** {v.vehicle_type}")
                col5.markdown(f"**Capacity:** {v.capacity_kg:,.0f} kg")
                col6.markdown(f"**Branch:** {v.branch_id}")
                if v.maintenance_note:
                    st.warning(f"🔧 Maintenance note: {v.maintenance_note}")

    st.divider()

    # ── Add new vehicle ──
    with st.expander("➕ Add New Vehicle", expanded=False):
        st.markdown("**Register a new vehicle to the fleet.**")
        with st.form("add_vehicle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                registration = st.text_input(
                    "Registration / Plate No. *",
                    placeholder="e.g. 51A-12345"
                )
                vehicle_type = st.selectbox(
                    "Vehicle Type *",
                    ["", "SMALL (up to 1,000 kg)",
                     "MEDIUM (up to 5,000 kg)",
                     "LARGE (up to 15,000 kg)"]
                )
            with col2:
                # Auto-suggest capacity based on type
                capacity_kg = st.number_input(
                    "Capacity (kg) *",
                    min_value=1.0,
                    value=1000.0,
                    step=100.0
                )

            submitted = st.form_submit_button(
                "➕ Add Vehicle", use_container_width=True
            )

            if submitted:
                # Validate empty fields
                if not registration.strip():
                    st.error("❌ Registration cannot be empty.")
                elif not vehicle_type:
                    st.error("❌ Please select a vehicle type.")
                else:
                    # Extract just the type keyword
                    vtype = vehicle_type.split()[0]
                    branch_id = fleet.get_default_branch_id()
                    success, message, vehicle = fleet.add_vehicle(
                        registration = registration,
                        vehicle_type = vtype,
                        capacity_kg  = capacity_kg,
                        branch_id    = branch_id
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    st.divider()

    # ── Update vehicle status ──
    with st.expander("🔧 Update Vehicle Status", expanded=False):
        st.markdown("**Change a vehicle's operational status.**")
        vehicles = fleet.get_all_vehicles()
        if not vehicles:
            st.info("No vehicles available to update.")
        else:
            with st.form("update_vehicle_form"):
                vehicle_options = {
                    f"{v.vehicle_id} — {v.registration} [{v.status}]": v.vehicle_id
                    for v in vehicles
                    if v.status != "ASSIGNED"
                }
                if not vehicle_options:
                    st.info("All vehicles are currently assigned.")
                else:
                    selected_label = st.selectbox(
                        "Select Vehicle",
                        list(vehicle_options.keys())
                    )
                    new_status = st.selectbox(
                        "New Status",
                        ["AVAILABLE", "MAINTENANCE"]
                    )
                    maintenance_note = st.text_input(
                        "Maintenance Note (required if MAINTENANCE)",
                        placeholder="e.g. Engine repair needed"
                    )
                    submitted = st.form_submit_button(
                        "🔄 Update Status", use_container_width=True
                    )
                    if submitted:
                        if new_status == "MAINTENANCE" and not maintenance_note.strip():
                            st.error("❌ Please provide a maintenance note.")
                        else:
                            vid = vehicle_options[selected_label]
                            success, message = fleet.update_vehicle_status(
                                vehicle_id       = vid,
                                new_status       = new_status,
                                maintenance_note = maintenance_note
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")


# ---------------------------------------------------------------------------
# Tab 3 — Drivers
# ---------------------------------------------------------------------------
def _render_drivers(fleet) -> None:
    """Render driver list, add driver form, and status update."""
    st.markdown("### 👷 Driver Management")

    # ── View all drivers ──
    drivers = fleet.get_all_drivers()
    if not drivers:
        st.info("No drivers in the fleet yet.")
    else:
        st.markdown(f"**{len(drivers)} driver(s) registered**")
        for d in drivers:
            status_color = {
                "AVAILABLE": "#10b981",
                "ASSIGNED" : "#3b82f6",
                "ON_LEAVE" : "#f59e0b"
            }.get(d.status, "#888")

            licence_warning = "" if d.is_licence_valid() else " ⚠️ EXPIRED"

            with st.expander(
                f"👷 {d.driver_id} — {d.full_name} | {d.status}"
            ):
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**ID:** {d.driver_id}")
                col2.markdown(f"**Name:** {d.full_name}")
                col3.markdown(
                    f"**Status:** <span style='color:{status_color}'>"
                    f"● {d.status}</span>",
                    unsafe_allow_html=True
                )
                col4, col5, col6 = st.columns(3)
                col4.markdown(f"**Licence:** {d.licence_number}")
                col5.markdown(
                    f"**Expiry:** {d.licence_expiry}{licence_warning}"
                )
                col6.markdown(f"**Phone:** {d.phone}")
                if d.leave_note:
                    st.warning(f"📝 Leave note: {d.leave_note}")
                if not d.is_licence_valid():
                    st.error("⚠️ This driver's licence has expired.")

    st.divider()

    # ── Add new driver ──
    with st.expander("➕ Add New Driver", expanded=False):
        st.markdown("**Register a new driver to the fleet.**")
        with st.form("add_driver_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name      = st.text_input("Full Name *", placeholder="e.g. Nguyen Van A")
                licence_number = st.text_input("Licence Number *", placeholder="e.g. B2-123456")
            with col2:
                licence_expiry = st.date_input(
                    "Licence Expiry Date *",
                    min_value=date.today(),
                    value=date(2028, 12, 31)
                )
                phone = st.text_input("Phone Number *", placeholder="e.g. 0901234567")

            submitted = st.form_submit_button(
                "➕ Add Driver", use_container_width=True
            )
            if submitted:
                if not full_name.strip():
                    st.error("❌ Full name cannot be empty.")
                elif not licence_number.strip():
                    st.error("❌ Licence number cannot be empty.")
                elif not phone.strip():
                    st.error("❌ Phone number cannot be empty.")
                else:
                    branch_id = fleet.get_default_branch_id()
                    success, message, driver = fleet.add_driver(
                        full_name      = full_name,
                        licence_number = licence_number,
                        licence_expiry = licence_expiry.strftime("%Y-%m-%d"),
                        phone          = phone,
                        branch_id      = branch_id
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    st.divider()

    # ── Update driver status ──
    with st.expander("🔄 Update Driver Status", expanded=False):
        st.markdown("**Change a driver's operational status.**")
        drivers = fleet.get_all_drivers()
        if not drivers:
            st.info("No drivers available to update.")
        else:
            with st.form("update_driver_form"):
                driver_options = {
                    f"{d.driver_id} — {d.full_name} [{d.status}]": d.driver_id
                    for d in drivers
                    if d.status != "ASSIGNED"
                }
                if not driver_options:
                    st.info("All drivers are currently assigned.")
                else:
                    selected_label = st.selectbox(
                        "Select Driver",
                        list(driver_options.keys())
                    )
                    new_status = st.selectbox(
                        "New Status",
                        ["AVAILABLE", "ON_LEAVE"]
                    )
                    leave_note = st.text_input(
                        "Leave Note (required if ON_LEAVE)",
                        placeholder="e.g. Annual leave"
                    )
                    submitted = st.form_submit_button(
                        "🔄 Update Status", use_container_width=True
                    )
                    if submitted:
                        if new_status == "ON_LEAVE" and not leave_note.strip():
                            st.error("❌ Please provide a leave note.")
                        else:
                            did = driver_options[selected_label]
                            success, message = fleet.update_driver_status(
                                driver_id  = did,
                                new_status = new_status,
                                leave_note = leave_note
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")


# ---------------------------------------------------------------------------
# Tab 4 — Dispatch
# ---------------------------------------------------------------------------
def _render_dispatch(fleet, shipment, orders) -> None:
    """Render the vehicle and driver assignment form for pending orders."""
    st.markdown("### 📋 Dispatch — Assign Vehicle & Driver")
    st.markdown(
        "*Select a pending order and assign an available "
        "vehicle and driver to fulfil it.*"
    )

    # Get pending orders
    pending = orders.get_pending_orders()

    if not pending:
        st.info("✅ No pending orders at this time. All orders have been dispatched.")
        return

    st.markdown(f"**{len(pending)} pending order(s) awaiting dispatch:**")

    with st.form("dispatch_form"):
        # Order selection
        order_options = {
            f"{o.order_id} | {o.cargo_description} | "
            f"{o.cargo_weight_kg} kg | {o.preferred_date}": o.order_id
            for o in pending
        }
        selected_order_label = st.selectbox(
            "Select Pending Order *",
            list(order_options.keys())
        )

        # Get selected order details
        selected_order_id = order_options[selected_order_label]
        selected_order    = orders.get_order(selected_order_id)

        if selected_order:
            st.markdown(
                f"<div style='background:#1e2130;padding:12px;"
                f"border-radius:8px;border:1px solid #2d3147;margin:8px 0'>"
                f"<b>📦 Order Details</b><br>"
                f"Cargo: {selected_order.cargo_description}<br>"
                f"Weight: {selected_order.cargo_weight_kg} kg<br>"
                f"Pickup: {selected_order.pickup_address}<br>"
                f"Delivery: {selected_order.delivery_address}<br>"
                f"Date: {selected_order.preferred_date}"
                f"</div>",
                unsafe_allow_html=True
            )

        st.divider()

        col1, col2 = st.columns(2)

        # Vehicle selection
        with col1:
            st.markdown("**🚗 Available Vehicles**")
            cargo_weight = selected_order.cargo_weight_kg if selected_order else 0
            avail_vehicles = fleet.get_available_vehicles(cargo_weight)

            if not avail_vehicles:
                st.warning(
                    f"⚠️ No vehicles available for "
                    f"{cargo_weight} kg cargo."
                )
                vehicle_options = {"No vehicles available": None}
            else:
                vehicle_options = {
                    f"{v.vehicle_id} | {v.registration} | "
                    f"{v.vehicle_type} | {v.capacity_kg:,.0f} kg": v.vehicle_id
                    for v in avail_vehicles
                }

            selected_vehicle_label = st.selectbox(
                "Select Vehicle *",
                list(vehicle_options.keys())
            )

        # Driver selection
        with col2:
            st.markdown("**👷 Available Drivers**")
            avail_drivers = fleet.get_available_drivers()

            if not avail_drivers:
                st.warning("⚠️ No drivers currently available.")
                driver_options = {"No drivers available": None}
            else:
                driver_options = {
                    f"{d.driver_id} | {d.full_name} | "
                    f"Licence: {d.licence_number}": d.driver_id
                    for d in avail_drivers
                }

            selected_driver_label = st.selectbox(
                "Select Driver *",
                list(driver_options.keys())
            )

        st.divider()

        submitted = st.form_submit_button(
            "🚀 Confirm Dispatch Assignment",
            use_container_width=True
        )

        if submitted:
            vehicle_id = vehicle_options.get(selected_vehicle_label)
            driver_id  = driver_options.get(selected_driver_label)

            # Validation
            if not vehicle_id:
                st.error("❌ Please select a valid vehicle.")
            elif not driver_id:
                st.error("❌ Please select a valid driver.")
            else:
                # Get customer name for notification
                from managers.account_manager import AccountManager
                acct = AccountManager()
                customer = acct.get_by_id(selected_order.customer_id)
                customer_name = customer.full_name if customer else selected_order.customer_id

                # Assign vehicle and driver via OrderManager
                success, message = orders.assign_vehicle_and_driver(
                    order_id      = selected_order_id,
                    vehicle_id    = vehicle_id,
                    driver_id     = driver_id,
                    customer_name = customer_name
                )
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


# ---------------------------------------------------------------------------
# Tab 5 — Shipment Tracking
# ---------------------------------------------------------------------------
def _render_tracking(shipment, fleet, orders) -> None:
    """Render active shipment tracking view."""
    st.markdown("### 📍 Shipment Tracking")

    all_shipments = shipment.get_all_shipments()

    if not all_shipments:
        st.info("No shipments recorded yet.")
        return

    # Filter options
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "ASSIGNED", "IN_TRANSIT", "DELIVERED"]
    )

    if status_filter != "All":
        filtered = [s for s in all_shipments if s.status == status_filter]
    else:
        filtered = all_shipments

    st.markdown(f"**{len(filtered)} shipment(s) found**")

    for s in filtered:
        order  = orders.get_order(s.order_id)
        vehicle = fleet.get_vehicle(s.vehicle_id)
        driver  = fleet.get_driver(s.driver_id)

        status_color = {
            "ASSIGNED"  : "#3b82f6",
            "IN_TRANSIT": "#f59e0b",
            "DELIVERED" : "#10b981"
        }.get(s.status, "#888")

        with st.expander(
            f"📍 {s.shipment_id} — Order {s.order_id} | "
            f"{s.status}"
        ):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Shipment:** {s.shipment_id}")
            col2.markdown(f"**Order:** {s.order_id}")
            col3.markdown(
                f"**Status:** <span style='color:{status_color}'>"
                f"● {s.status}</span>",
                unsafe_allow_html=True
            )

            col4, col5, col6 = st.columns(3)
            col4.markdown(
                f"**Vehicle:** "
                f"{vehicle.registration if vehicle else s.vehicle_id}"
            )
            col5.markdown(
                f"**Driver:** "
                f"{driver.full_name if driver else s.driver_id}"
            )
            col6.markdown(f"**Assigned:** {s.assigned_date}")

            if order:
                st.markdown(
                    f"**Route:** {order.pickup_address} → "
                    f"{order.delivery_address}"
                )

            if s.delivered_date:
                st.markdown(f"**Delivered:** {s.delivered_date}")

            # Tracking events
            if s.tracking_events:
                st.markdown("**📋 Tracking History:**")
                for event in reversed(s.tracking_events):
                    st.markdown(
                        f"<div style='background:#1e2130;padding:8px 12px;"
                        f"border-radius:6px;border-left:3px solid #2d6df6;"
                        f"margin:4px 0;font-size:13px'>"
                        f"🕐 {event.get('timestamp','')} — "
                        f"<b>{event.get('milestone','')}</b><br>"
                        f"{event.get('notes','')}</div>",
                        unsafe_allow_html=True
                    )

            # Update shipment status buttons
            if s.status == "ASSIGNED":
                if st.button(
                    f"🚗 Mark IN TRANSIT — {s.shipment_id}",
                    key=f"transit_{s.shipment_id}"
                ):
                    ok, msg = shipment.mark_in_transit(s.shipment_id)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            elif s.status == "IN_TRANSIT":
                if st.button(
                    f"✅ Mark DELIVERED — {s.shipment_id}",
                    key=f"delivered_{s.shipment_id}"
                ):
                    ok, msg = shipment.mark_delivered(s.shipment_id)
                    if ok:
                        # Release vehicle and driver
                        fleet.release_vehicle(s.vehicle_id)
                        fleet.release_driver(s.driver_id)
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")