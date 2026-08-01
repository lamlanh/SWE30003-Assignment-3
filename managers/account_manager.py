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
        """
        TODO: 
        1. Check if the username already exists (return an error message if so).
        2. Hash the password (using the hashlib library).
        3. Generate a new ID using generate_new_id().
        4. Create a new Customer object.
        5. Add it to self.customers and call self.save_customers().
        """
        pass

    def validate_login(self, username, password):
        """
        TODO:
        1. Check if username and password match 'admin' or 'staff' (from README).
        2. If not, check if it matches a customer in self.customers (remember to hash the 
            input password to compare it with the stored hash!).
        3. Return the user role or Customer object if successful, else False.
        """
        pass

    def get_customer_by_id(self, customer_id):
        """
        TODO:
        Search self.customers for a matching ID and return the Customer object.
        """
        pass