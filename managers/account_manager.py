from utils.json_helper import load_data, save_data                                                               
from utils.id_generator import generate_new_id                                                                   
from models.customer import Customer                                                                             
import hashlib                                                                                                   
                                                                                                                    
class AccountManager:                                                                                            
    def __init__(self):                                                                                          
        # Load all customers from the JSON file into memory when the manager starts                              
        self.customers = self._load_customers()                                                                  
                                                                                                                    
    def _load_customers(self):                                                                                   
        """Private helper to load and convert JSON dictionaries into Customer objects."""                        
        data = load_data('customers.json')                                                                       
        return [Customer.from_dict(cust) for cust in data]                                                       
                                                                                                                    
    def save_customers(self):                                                                                    
        """Converts Customer objects back to dictionaries and saves to JSON."""                                  
        data = [cust.to_dict() for cust in self.customers]                                                       
        save_data('customers.json', data)                                                                        
                                                                                                                    
    # =========================================================================                                  
    # STUBS FOR OTHER TEAM MEMBERS TO IMPLEMENT LATER                                                                           
    # You can call these right now without the app crashing                                              
    # =========================================================================                                  

    def register_customer(self, username, password, full_name, email, phone, address):
        """Registers a new customer after validating the username."""                                            
                                                                                                                     
        # 1. Check if username already exists                                                                    
        for existing_cust in self.customers:                                                                     
            if existing_cust.username == username:                                                               
                return False, "Username already exists. Please choose another."                                  
                                                                                                                    
        # 2. Hash the password for security                                                                      
        # We use SHA-256 to scramble the password so we never store plain text                                   
        password_hash = hashlib.sha256(password.encode()).hexdigest()                                            
                                                                                                                    
        # 3. Generate a new ID (e.g., CUST-001)                                                                  
        # We need to pass it a list of dictionaries, not Customer objects,                                       
        # so we convert self.customers to dicts temporarily just for the ID generator                            
        customer_dicts = [cust.to_dict() for cust in self.customers]                                             
        new_id = generate_new_id(customer_dicts, "customer_id", "CUST")                                          
                                                                                                                    
        # 4. Create the new Customer object                                                                      
        new_customer = Customer(                                                                                 
            customer_id=new_id,                                                                                  
            username=username,                                                                                   
            password_hash=password_hash,                                                                         
            full_name=full_name,                                                                                 
            email=email,                                                                                         
            phone=phone,                                                                                         
            address=address                                                                                      
        )                                                                                                        
                                                                                                                    
        # 5. Save the customer to memory and write to the JSON file                                              
        self.customers.append(new_customer)                                                                      
        self.save_customers()                                                                                    
                                                                                                                    
        return True, "Registration successful!"
    
    def validate_login(self, username, password):
        """                                                                                                      
        Validates login credentials.                                                                             
        Returns the user's role/object if successful, or False if invalid.                                       
        """                                                                                                      
        # 1. Check for the hardcoded default accounts first (from README)                                        
        if username == "admin" and password == "admin123":                                                       
            return {"role": "ADMIN", "username": "admin"}                                                        
                                                                                                                    
        if username == "staff" and password == "staff123":                                                       
            return {"role": "STAFF", "username": "staff"}                                                        
                                                                                                                    
        # 2. If it's not a staff/admin, check the registered customers                                           
        # Hash the password they typed in so we can compare it to the stored hash                                
        password_hash = hashlib.sha256(password.encode()).hexdigest()                                            

        for customer in self.customers:
            if customer.username == username and customer.password_hash == password_hash:
                # Login successful! Return the customer object and their role
                return {"role": "CUSTOMER", "customer_data": customer}

        # 3. If no match is found
        return False

    def get_customer_by_id(self, customer_id):
        """
        Searches the memory for a specific customer.
        Returns the Customer object if found, or None if not found.
        """
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer

        return None