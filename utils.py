def create_response_data(status, message, data):
    return {
        "status": status,
        "message": message,
        "data": data
    }
def create_response_list_data(status, count,message, data):
    return {
        "status": status,
        "count": count,
        "message": message,
        "data": data
    }
