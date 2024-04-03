from django.contrib.auth import get_user_model


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


def generate_random_password():
    User = get_user_model()
    return get_user_model().objects.make_random_password()