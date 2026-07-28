class Branch:
    """
    Data-holder class representing an ABC-Trans branch office.

    Attributes:
        branch_id   (str) : Unique system-generated identifier.
        name        (str) : Branch name (e.g. "Hanoi North Branch").
        address     (str) : Physical address of the branch.
        region      (str) : Geographic region (e.g. "North", "South").
        manager_id  (str) : ID of the Branch Manager (future use).
        phone       (str) : Branch contact phone number.
    """

    def __init__(
        self,
        branch_id: str,
        name: str,
        address: str,
        region: str,
        phone: str,
        manager_id: str = None
    ):
        self.branch_id  = branch_id
        self.name       = name
        self.address    = address
        self.region     = region
        self.phone      = phone
        self.manager_id = manager_id

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Branch object to a dictionary for JSON storage."""
        return {
            "branch_id"  : self.branch_id,
            "name"       : self.name,
            "address"    : self.address,
            "region"     : self.region,
            "phone"      : self.phone,
            "manager_id" : self.manager_id
        }

    @staticmethod
    def from_dict(data: dict) -> "Branch":
        """Create a Branch object from a dictionary loaded from JSON."""
        return Branch(
            branch_id  = data["branch_id"],
            name       = data["name"],
            address    = data["address"],
            region     = data["region"],
            phone      = data["phone"],
            manager_id = data.get("manager_id")
        )

    def __repr__(self) -> str:
        return (
            f"Branch(id={self.branch_id}, "
            f"name={self.name}, "
            f"region={self.region})"
        )