from datetime import datetime


class Customer:
    """
    Data-holder class representing a registered ABC-Trans customer.

    Attributes:
        customer_id     (str)  : Unique system-generated identifier.
        username        (str)  : Unique login username.
        password_hash   (str)  : Hashed password string.
        full_name       (str)  : Customer's full name.
        email           (str)  : Customer's email address.
        phone           (str)  : Customer's phone number.
        address         (str)  : Customer's primary delivery address.
        registered_date (str)  : ISO format date when account was created.
        is_active       (bool) : Whether the account is active.
    """

    def __init__(
        self,
        customer_id: str,
        username: str,
        password_hash: str,
        full_name: str,
        email: str,
        phone: str,
        address: str,
        registered_date: str = None,
        is_active: bool = True
    ):
        self.customer_id     = customer_id
        self.username        = username
        self.password_hash   = password_hash
        self.full_name       = full_name
        self.email           = email
        self.phone           = phone
        self.address         = address
        self.registered_date = registered_date or datetime.now().strftime("%Y-%m-%d")
        self.is_active       = is_active

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Customer object to a dictionary for JSON storage."""
        return {
            "customer_id"     : self.customer_id,
            "username"        : self.username,
            "password_hash"   : self.password_hash,
            "full_name"       : self.full_name,
            "email"           : self.email,
            "phone"           : self.phone,
            "address"         : self.address,
            "registered_date" : self.registered_date,
            "is_active"       : self.is_active
        }

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        """Create a Customer object from a dictionary loaded from JSON."""
        return Customer(
            customer_id     = data["customer_id"],
            username        = data["username"],
            password_hash   = data["password_hash"],
            full_name       = data["full_name"],
            email           = data["email"],
            phone           = data["phone"],
            address         = data["address"],
            registered_date = data.get("registered_date"),
            is_active       = data.get("is_active", True)
        )

    def __repr__(self) -> str:
        return (
            f"Customer(id={self.customer_id}, "
            f"username={self.username}, "
            f"name={self.full_name})"
        )