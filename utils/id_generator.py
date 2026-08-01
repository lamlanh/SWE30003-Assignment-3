def generate_new_id(data_list, id_field, prefix):                                                
    """                                                                                          
    Generates a new sequential ID based on existing data.                                        
    Format: PREFIX-XXX (e.g., CUST-001, ORD-005)                                                 
                                                                                                    
    Args:                                                                                        
        data_list (list): The list of dictionaries loaded from JSON.                             
        id_field (str): The dictionary key where the ID is stored (e.g., 'customer_id').         
        prefix (str): The prefix for the ID (e.g., 'CUST').                                      
                                                                                                    
    Returns:                                                                                     
        str: The newly generated ID.                                                             
    """                                                                                          
    # If the list is empty, return the very first ID                                             
    if not data_list:                                                                            
        return f"{prefix}-001"                                                                   
    
    highest_num = 0
    
    # Loop through all existing items to find the highest number
    for item in data_list:
        current_id = item.get(id_field, "")
        
        # Make sure the ID matches our expected prefix format
        if current_id.startswith(f"{prefix}-"):
            try:
                # Split 'CUST-005' into ['CUST', '005'] and take the number
                num_part = int(current_id.split("-")[1])
                if num_part > highest_num:
                    highest_num = num_part
            except (IndexError, ValueError):
                # Ignore items that are formatted incorrectly
                continue

    # Add 1 to the highest number found
    next_num = highest_num + 1
    
    # Format with leading zeros (e.g., 5 becomes '005')
    return f"{prefix}-{next_num:03d}"