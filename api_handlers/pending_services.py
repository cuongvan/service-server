from threading import Lock

_building_services = set()
_building_services_lock = Lock()

def new_building_service(service_name: str) -> bool:
    # true: ok
    # false: service already exists
    with _building_services_lock:
        if service_name in _building_services:
            return False
        else:
            _building_services.add(service_name)
            return True

# def service_is_building(service_name: str) -> bool:
#     with _building_services_lock:
#         return service_name in _building_services

def build_service_done(service_name: str):
    with _building_services_lock:
        _building_services.remove(service_name)

_removing_services = set()
_removing_services_lock = Lock()

def new_removing_service(service_name: str) -> bool:
    # true: ok
    # false: service already exists
    with _removing_services_lock:
        if service_name in _removing_services:
            return False
        else:
            _removing_services.add(service_name)
            return True

def service_is_being_removed(service_name: str) -> bool:
    with _removing_services_lock:
        return service_name in _removing_services

def remove_service_done(service_name: str):
    with _removing_services_lock:
        _removing_services.remove(service_name)
