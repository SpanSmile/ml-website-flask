def get_authority_label(authority_value):
    authority_map = {
        0: 'Admin',
        1: 'Teacher',
        2: 'Student'
    }
    return authority_map.get(authority_value, 'Unknown')