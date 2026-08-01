from datetime import datetime                                                                    
                                                                                                     
class Customer:                                                                                  
    def __init__(self, customer_id, username, password_hash, full_name, email, phone, address,   
    registered_date=None):                                                                             
        self.customer_id = customer_id                                                           
        self.username = username                                                                 
        self.password_hash = password_hash                                                       
        self.full_name = full_name                                                               
        self.email = email                                                                       
        self.phone = phone                                                                       
        self.address = address                                                                   
                                                                                                    
        # If no date is provided, use the current date and time                                  
        if registered_date is None:                                                              
            self.registered_date = datetime.now().isoformat()
        else:
            self.registered_date = registered_date

    def to_dict(self):
        """Converts the Customer object into a dictionary so it can be saved to JSON."""         
        return {
            "customer_id": self.customer_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "registered_date": self.registered_date
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Customer object from a dictionary loaded from JSON."""
        return cls(
            customer_id=data.get("customer_id"),
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            registered_date=data.get("registered_date")
        )