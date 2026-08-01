import streamlit as st                                                                                           
                                                                                                                     
def render_page():                                                                                               
    st.title("Customer Account Management")                                                                   
                                                                                                                    
    # We access the AccountManager that was created by SmartFMSystem on startup                                  
    account_manager = st.session_state.system.account_manager                                                    
                                                                                                                    
    # Create two tabs on the screen                                                                              
    tab1, tab2 = st.tabs(["Login", "Register New Account"])                                                      
                                                                                                                                                                 
    # TAB 1: LOGIN FORM                                                                                                                                                          
    with tab1:                                                                                                   
        st.subheader("Login to SmartFM")                                                                         
                                                                                                                    
        # Streamlit creates input boxes for us                                                                   
        login_user = st.text_input("Username", key="login_user")                                                 
        login_pass = st.text_input("Password", type="password", key="login_pass")                                
                                                                                                                    
        if st.button("Login"):                                                                                   
            if not login_user or not login_pass:                                                                 
                st.warning("Please enter both username and password.")                                           
            else:                                                                                                
                # Call the validate_login function we wrote earlier!                                             
                result = account_manager.validate_login(login_user, login_pass)                                  
                                                                                                                    
                if result:                                                                                       
                    st.success(f"Welcome back! Logged in as {result['role']}")                                   
                    # Save the user's logged-in status so other pages know who they are                          
                    st.session_state.current_user = result                                                       
                else:                                                                                            
                    st.error("Invalid username or password.")                                                    

    # TAB 2: REGISTRATION FORM
    with tab2:
        st.subheader("Create a New Account")
        
        reg_user = st.text_input("Username")
        reg_pass = st.text_input("Password", type="password")
        reg_name = st.text_input("Full Name")
        reg_email = st.text_input("Email")
        reg_phone = st.text_input("Phone Number")
        reg_address = st.text_area("Delivery Address")
        
        if st.button("Register"):
            # Basic validation to ensure fields aren't empty
            if not all([reg_user, reg_pass, reg_name, reg_email, reg_phone, reg_address]):
                st.warning("Please fill out all fields.")
            else:
                # Call the register_customer function we wrote earlier!
                success, message = account_manager.register_customer(
                    reg_user, reg_pass, reg_name, reg_email, reg_phone, reg_address
                )

                if success:
                    st.success(message)
                    st.info("You can now go to the Login tab to sign in.")
                else:
                    st.error(message)