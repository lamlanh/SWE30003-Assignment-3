import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("models", "storage"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from models.vehicle import Vehicle, STATUS_AVAILABLE, STATUS_ASSIGNED, STATUS_MAINTENANCE
from models.driver import Driver, STATUS_AVAILABLE as DRV_AVAILABLE, STATUS_ASSIGNED as DRV_ASSIGNED, STATUS_ON_LEAVE
from models.branch import Branch
from storage.file_storage import FileStorage


class FleetManager:
    """
    Manages vehicle and driver records for SmartFM.

    Responsibilities (from CRC Card 4):
        - Add, update, or decommission a vehicle record
        - Add, update, or deactivate a driver record
        - Check vehicle availability for a given cargo weight
        - Check driver availability
        - Assign a vehicle and driver to a confirmed order
        - Flag vehicles under maintenance

    Collaborators:
        - Vehicle (data-holder)
        - Driver  (data-holder)
        - Branch  (data-holder)
        - FileStorage
        - OrderManager
        - ScheduleManager
    """

    def __init__(self):
        """Initialise FleetManager and load data from JSON."""
        self._storage  = FileStorage()

        # In-memory dictionaries
        self._vehicles = {}   # { vehicle_id: Vehicle }
        self._drivers  = {}   # { driver_id: Driver }
        self._branches = {}   # { branch_id: Branch }

        # ID counters
        self._vehicle_counter = 1
        self._driver_counter  = 1
        self._branch_counter  = 1

        self._load()

        # Seed default branch and sample data if empty
        if not self._branches:
            self._seed_default_data()

    # -----------------------------------------------------------------------
    # Load / Save
    # -----------------------------------------------------------------------
    def _load(self) -> None:
        """Load all fleet records from JSON into memory."""
        raw_vehicles = self._storage.load_vehicles()
        self._vehicles = {
            vid: Vehicle.from_dict(data)
            for vid, data in raw_vehicles.items()
        }

        raw_drivers = self._storage.load_drivers()
        self._drivers = {
            did: Driver.from_dict(data)
            for did, data in raw_drivers.items()
        }

        raw_branches = self._storage.load_branches()
        self._branches = {
            bid: Branch.from_dict(data)
            for bid, data in raw_branches.items()
        }

        # Set counters based on loaded data
        self._vehicle_counter = len(self._vehicles) + 1
        self._driver_counter  = len(self._drivers)  + 1
        self._branch_counter  = len(self._branches) + 1

    def save(self) -> None:
        """Save all fleet records from memory to JSON."""
        self._storage.save_vehicles({
            vid: v.to_dict() for vid, v in self._vehicles.items()
        })
        self._storage.save_drivers({
            did: d.to_dict() for did, d in self._drivers.items()
        })
        self._storage.save_branches({
            bid: b.to_dict() for bid, b in self._branches.items()
        })

    # -----------------------------------------------------------------------
    # Default seed data
    # -----------------------------------------------------------------------
    def _seed_default_data(self) -> None:
        """
        Seed a default branch, vehicles, and drivers on first run.
        This ensures the system has data to work with immediately.
        """
        # Default branch
        branch = Branch(
            branch_id = "BRANCH-001",
            name      = "Hanoi Central Branch",
            address   = "123 Tran Duy Hung, Hanoi, Vietnam",
            region    = "North",
            phone     = "024-3456-7890"
        )
        self._branches["BRANCH-001"] = branch

        # Default vehicles
        vehicles = [
            Vehicle("VEH-001", "51A-12345", "SMALL",  1000.0, "BRANCH-001"),
            Vehicle("VEH-002", "51A-67890", "MEDIUM", 5000.0, "BRANCH-001"),
            Vehicle("VEH-003", "51B-11111", "LARGE",  15000.0,"BRANCH-001"),
        ]
        for v in vehicles:
            self._vehicles[v.vehicle_id] = v

        # Default drivers
        drivers = [
            Driver("DRV-001", "Nguyen Van An",  "B2-123456", "2028-12-31", "0901234567", "BRANCH-001"),
            Driver("DRV-002", "Tran Thi Bich",  "B2-654321", "2027-06-30", "0907654321", "BRANCH-001"),
            Driver("DRV-003", "Le Van Cuong",   "C-789012",  "2029-03-31", "0903456789", "BRANCH-001"),
        ]
        for d in drivers:
            self._drivers[d.driver_id] = d

        self._vehicle_counter = len(self._vehicles) + 1
        self._driver_counter  = len(self._drivers)  + 1
        self._branch_counter  = len(self._branches) + 1

        self.save()

    # -----------------------------------------------------------------------
    # ID generators
    # -----------------------------------------------------------------------
    def _generate_vehicle_id(self) -> str:
        vid = f"VEH-{self._vehicle_counter:03d}"
        self._vehicle_counter += 1
        return vid

    def _generate_driver_id(self) -> str:
        did = f"DRV-{self._driver_counter:03d}"
        self._driver_counter += 1
        return did

    # -----------------------------------------------------------------------
    # Vehicle management
    # -----------------------------------------------------------------------
    def add_vehicle(
        self,
        registration: str,
        vehicle_type: str,
        capacity_kg: float,
        branch_id: str
    ) -> tuple:
        """
        Add a new vehicle to the fleet.

        Args:
            registration (str)  : Vehicle registration/plate number.
            vehicle_type (str)  : SMALL, MEDIUM, or LARGE.
            capacity_kg  (float): Max cargo weight in kg.
            branch_id    (str)  : Branch this vehicle belongs to.

        Returns:
            tuple: (success: bool, message: str, vehicle: Vehicle or None)
        """
        if not registration.strip():
            return False, "Registration cannot be empty.", None

        if vehicle_type.upper() not in ("SMALL", "MEDIUM", "LARGE"):
            return False, "Vehicle type must be SMALL, MEDIUM, or LARGE.", None

        if capacity_kg <= 0:
            return False, "Capacity must be greater than 0 kg.", None

        # Check registration is unique
        if any(v.registration == registration.strip().upper()
               for v in self._vehicles.values()):
            return False, f"Vehicle '{registration}' already exists.", None

        vehicle_id = self._generate_vehicle_id()
        vehicle = Vehicle(
            vehicle_id   = vehicle_id,
            registration = registration.strip().upper(),
            vehicle_type = vehicle_type.upper(),
            capacity_kg  = capacity_kg,
            branch_id    = branch_id
        )
        self._vehicles[vehicle_id] = vehicle
        self.save()
        return True, f"Vehicle {vehicle_id} added successfully.", vehicle

    def update_vehicle_status(
        self,
        vehicle_id: str,
        new_status: str,
        maintenance_note: str = ""
    ) -> tuple:
        """
        Update a vehicle's status.

        Args:
            vehicle_id       (str): The vehicle to update.
            new_status       (str): New status (AVAILABLE/ASSIGNED/MAINTENANCE).
            maintenance_note (str): Reason if under maintenance.

        Returns:
            tuple: (success: bool, message: str)
        """
        vehicle = self._vehicles.get(vehicle_id)
        if not vehicle:
            return False, f"Vehicle {vehicle_id} not found."

        valid_statuses = (STATUS_AVAILABLE, STATUS_ASSIGNED, STATUS_MAINTENANCE)
        if new_status.upper() not in valid_statuses:
            return False, f"Invalid status. Choose: {', '.join(valid_statuses)}."

        vehicle.status           = new_status.upper()
        vehicle.maintenance_note = maintenance_note
        self.save()
        return True, f"Vehicle {vehicle_id} status updated to {new_status}."

    def remove_vehicle(self, vehicle_id: str) -> tuple:
        """
        Remove (decommission) a vehicle from the fleet.

        Args:
            vehicle_id (str): The vehicle to remove.

        Returns:
            tuple: (success: bool, message: str)
        """
        if vehicle_id not in self._vehicles:
            return False, f"Vehicle {vehicle_id} not found."

        if self._vehicles[vehicle_id].status == STATUS_ASSIGNED:
            return False, "Cannot remove a vehicle that is currently assigned."

        del self._vehicles[vehicle_id]
        self.save()
        return True, f"Vehicle {vehicle_id} removed from the fleet."

    # -----------------------------------------------------------------------
    # Driver management
    # -----------------------------------------------------------------------
    def add_driver(
        self,
        full_name: str,
        licence_number: str,
        licence_expiry: str,
        phone: str,
        branch_id: str
    ) -> tuple:
        """
        Add a new driver to the fleet.

        Args:
            full_name      (str): Driver's full name.
            licence_number (str): Driver's licence number.
            licence_expiry (str): Licence expiry date (YYYY-MM-DD).
            phone          (str): Driver's contact phone.
            branch_id      (str): Branch this driver belongs to.

        Returns:
            tuple: (success: bool, message: str, driver: Driver or None)
        """
        if not full_name.strip():
            return False, "Driver name cannot be empty.", None
        if not licence_number.strip():
            return False, "Licence number cannot be empty.", None
        if not phone.strip():
            return False, "Phone number cannot be empty.", None

        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(licence_expiry, "%Y-%m-%d")
        except ValueError:
            return False, "Licence expiry must be in YYYY-MM-DD format.", None

        # Check licence number is unique
        if any(d.licence_number == licence_number.strip()
               for d in self._drivers.values()):
            return False, f"Licence number '{licence_number}' already exists.", None

        driver_id = self._generate_driver_id()
        driver = Driver(
            driver_id      = driver_id,
            full_name      = full_name.strip(),
            licence_number = licence_number.strip(),
            licence_expiry = licence_expiry,
            phone          = phone.strip(),
            branch_id      = branch_id
        )
        self._drivers[driver_id] = driver
        self.save()
        return True, f"Driver {driver_id} added successfully.", driver

    def update_driver_status(
        self,
        driver_id: str,
        new_status: str,
        leave_note: str = ""
    ) -> tuple:
        """
        Update a driver's status.

        Args:
            driver_id  (str): The driver to update.
            new_status (str): New status (AVAILABLE/ASSIGNED/ON_LEAVE).
            leave_note (str): Reason for leave if ON_LEAVE.

        Returns:
            tuple: (success: bool, message: str)
        """
        driver = self._drivers.get(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."

        valid = (DRV_AVAILABLE, DRV_ASSIGNED, STATUS_ON_LEAVE)
        if new_status.upper() not in valid:
            return False, f"Invalid status. Choose: {', '.join(valid)}."

        driver.status     = new_status.upper()
        driver.leave_note = leave_note
        self.save()
        return True, f"Driver {driver_id} status updated to {new_status}."

    def remove_driver(self, driver_id: str) -> tuple:
        """
        Remove (deactivate) a driver from the fleet.

        Args:
            driver_id (str): The driver to remove.

        Returns:
            tuple: (success: bool, message: str)
        """
        if driver_id not in self._drivers:
            return False, f"Driver {driver_id} not found."

        if self._drivers[driver_id].status == DRV_ASSIGNED:
            return False, "Cannot remove a driver that is currently assigned."

        del self._drivers[driver_id]
        self.save()
        return True, f"Driver {driver_id} removed from the fleet."

    # -----------------------------------------------------------------------
    # Availability checks
    # -----------------------------------------------------------------------
    def get_available_vehicles(self, cargo_weight_kg: float = 0) -> list:
        """
        Return a list of available vehicles that can carry the cargo weight.

        Args:
            cargo_weight_kg (float): Required cargo weight in kg (0 = any).

        Returns:
            list: List of available Vehicle objects sorted by capacity.
        """
        available = [
            v for v in self._vehicles.values()
            if v.is_available() and v.can_carry(cargo_weight_kg)
        ]
        return sorted(available, key=lambda v: v.capacity_kg)

    def get_available_drivers(self) -> list:
        """
        Return a list of available drivers with valid licences.

        Returns:
            list: List of available Driver objects.
        """
        return [
            d for d in self._drivers.values()
            if d.is_available() and d.is_licence_valid()
        ]

    # -----------------------------------------------------------------------
    # Assignment
    # -----------------------------------------------------------------------
    def assign_vehicle(self, vehicle_id: str) -> tuple:
        """
        Mark a vehicle as ASSIGNED.

        Args:
            vehicle_id (str): The vehicle to assign.

        Returns:
            tuple: (success: bool, message: str)
        """
        vehicle = self._vehicles.get(vehicle_id)
        if not vehicle:
            return False, f"Vehicle {vehicle_id} not found."
        if not vehicle.is_available():
            return False, f"Vehicle {vehicle_id} is not available."

        vehicle.status = STATUS_ASSIGNED
        self.save()
        return True, f"Vehicle {vehicle_id} assigned."

    def assign_driver(self, driver_id: str) -> tuple:
        """
        Mark a driver as ASSIGNED.

        Args:
            driver_id (str): The driver to assign.

        Returns:
            tuple: (success: bool, message: str)
        """
        driver = self._drivers.get(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."
        if not driver.is_available():
            return False, f"Driver {driver_id} is not available."

        driver.status = DRV_ASSIGNED
        self.save()
        return True, f"Driver {driver_id} assigned."

    def release_vehicle(self, vehicle_id: str) -> None:
        """Release a vehicle back to AVAILABLE status."""
        vehicle = self._vehicles.get(vehicle_id)
        if vehicle:
            vehicle.status = STATUS_AVAILABLE
            self.save()

    def release_driver(self, driver_id: str) -> None:
        """Release a driver back to AVAILABLE status."""
        driver = self._drivers.get(driver_id)
        if driver:
            driver.status = DRV_AVAILABLE
            self.save()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------
    def get_vehicle(self, vehicle_id: str):
        """Return a Vehicle by ID or None."""
        return self._vehicles.get(vehicle_id)

    def get_driver(self, driver_id: str):
        """Return a Driver by ID or None."""
        return self._drivers.get(driver_id)

    def get_all_vehicles(self) -> list:
        """Return all vehicles."""
        return list(self._vehicles.values())

    def get_all_drivers(self) -> list:
        """Return all drivers."""
        return list(self._drivers.values())

    def get_all_branches(self) -> list:
        """Return all branches."""
        return list(self._branches.values())

    def get_default_branch_id(self) -> str:
        """Return the first branch ID (default branch)."""
        if self._branches:
            return list(self._branches.keys())[0]
        return "BRANCH-001"

    def __repr__(self) -> str:
        return (
            f"FleetManager("
            f"vehicles={len(self._vehicles)}, "
            f"drivers={len(self._drivers)})"
        )