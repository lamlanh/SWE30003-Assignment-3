from managers.account_manager import AccountManager                                                              
                                                                                                                     
# =====================================================================                                          
# TODO for Members 2 & 3:                                                                                        
# Uncomment these imports when you create your manager files!                                                    
# =====================================================================                                          
# from managers.order_manager import OrderManager                                                                
# from managers.shipment_manager import ShipmentManager                                                          
# from managers.fleet_manager import FleetManager                                                                
# from managers.payment_processor import PaymentProcessor                                                        
                                                                                                                    
class SmartFMSystem:                                                                                             
    """                                                                                                          
    The Core Bootstrap Controller.                                                                               
    This acts as the central hub. It creates exactly one instance of every manager                               
    and holds them here so the UI can easily access them.
    """
    def __init__(self):
        print("Starting up SmartFM System...")
        
        # Initialize Member 1's manager
        self.account_manager = AccountManager()
        
        # =====================================================================
        # TODO for Members 2 & 3: 
        # Uncomment these lines when you create your manager classes!
        # =====================================================================
        # self.order_manager = OrderManager()
        # self.fleet_manager = FleetManager()
        # self.shipment_manager = ShipmentManager()
        # self.payment_processor = PaymentProcessor()