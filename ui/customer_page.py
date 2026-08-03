import streamlit as st

def render(system):
    # Set the title of the page
    st.title("Customer Account Management")

    # Grab the AccountManager instance from the system passed in by app.py
    account_manager = system.account_manager

    # Check if someone is currently logged in
    # (We save this in session_state when they successfully log in)
    user_info = st.session_state.get('current_user')

    # If there is a user logged in AND their role is CUSTOMER, show the profile view
    if user_info and user_info.get('role') == 'CUSTOMER':
        # Extract the Customer object from the session state dictionary
        customer = user_info['customer_data']

        # Display a welcome message
        st.subheader(f"Welcome back, {customer.full_name}!")

        # Create two tabs for the logged-in user
        tab1, tab2 = st.tabs(["Update Profile", "Change Password"])

        # LOGGED IN TAB 1: UPDATE PROFILE
        with tab1:
            # Create text inputs pre-filled with the customer's current data
            up_name = st.text_input("Full Name", value=customer.full_name)
            up_email = st.text_input("Email", value=customer.email)
            up_phone = st.text_input("Phone Number", value=customer.phone)
            up_address = st.text_area("Delivery Address", value=customer.address)

            # When the user clicks the "Save Profile" button
            if st.button("Save Profile"):
                # Call the manager to update the details and save to JSON
                success, msg = account_manager.update_profile(
                    customer.customer_id, up_name, up_email, up_phone, up_address
                )

                # Show a green success message or a red error message
                if success:
                    st.success(msg)
                else:
                    st.error(msg)


        # LOGGED IN TAB 2: CHANGE PASSWORD
        with tab2:
            # Create password inputs (the text will be hidden as dots)
            old_pass = st.text_input("Old Password", type="password")
            new_pass = st.text_input("New Password", type="password")

            # When the user clicks the "Change Password" button
            if st.button("Change Password"):
                # Call the manager to verify the old password and save the new one
                success, msg = account_manager.change_password(customer.customer_id, old_pass, new_pass)

                if success:
                    st.success(msg)
                else:
                    st.error(msg)


        # LOGOUT BUTTON
        # Add some space, then show a red (primary) logout button
        st.write("---")
        if st.button("Logout", type="primary"):
            # Clear the session state and refresh the page to show the login screen again
            st.session_state.current_user = None
            st.rerun()

    # If NO ONE is logged in, show the Login/Register view
    else:
        # Create two tabs for guests
        tab1, tab2 = st.tabs(["Login", "Register New Account"])

        # GUEST TAB 1: LOGIN
        with tab1:
            st.subheader("Login to SmartFM")

            # Input fields for login
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login"):
                # Prevent submission if fields are empty
                if not login_user or not login_pass:
                    st.warning("Please enter both username and password.")
                else:
                    # Check credentials against the database
                    result = account_manager.validate_login(login_user, login_pass)

                    if result:
                        # If valid, save the user info to session state and refresh the page
                        st.success(f"Welcome back! Logged in as {result['role']}")
                        st.session_state.current_user = result
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")


        # GUEST TAB 2: REGISTER
        with tab2:
            st.subheader("Create a New Account")

            # Input fields for registration
            reg_user = st.text_input("Username")
            reg_pass = st.text_input("Password", type="password")
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            reg_phone = st.text_input("Phone Number")
            reg_address = st.text_area("Delivery Address")

            if st.button("Register"):
                # Prevent submission if any field is empty
                if not all([reg_user, reg_pass, reg_name, reg_email, reg_phone, reg_address]):
                    st.warning("Please fill out all fields.")
                else:
                    # Attempt to register the user
                    success, message = account_manager.register_customer(
                        reg_user, reg_pass, reg_name, reg_email, reg_phone, reg_address
                    )

                    if success:
                        st.success(message)
                        st.info("You can now go to the Login tab to sign in.")
                    else:
                        # Usually happens if the username is already taken
                        st.error(message)