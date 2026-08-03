from managers.account_manager import AccountManager
from managers.order_manager import OrderManager
from managers.payment_processor import PaymentProcessor
from managers.shipment_manager import ShipmentManager
from managers.fleet_manager import FleetManager
# =====================================================================
# TODO for Members 3:
# Uncomment these imports when you create your manager files!
# =====================================================================
# from managers.shipment_manager import ShipmentManager
# from managers.fleet_manager import FleetManager


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

        # Initialize Member 2's managers
        self.order_manager = OrderManager()
        self.payment_processor = PaymentProcessor(order_manager=self.order_manager)

        # Initialize Member 3's managers
        self.fleet_manager = FleetManager()
        self.shipment_manager = ShipmentManager()

        # =====================================================================
        # TODO for Members 3:
        # Uncomment these lines when you create your manager classes!
        # =====================================================================
        # self.fleet_manager = FleetManager()
        # self.shipment_manager = ShipmentManager()