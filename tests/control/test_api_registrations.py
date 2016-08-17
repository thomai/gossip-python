from control.api_registrations import APIRegistrationHandler

__author__ = ''


def test_api_registrations():

    registrations = APIRegistrationHandler()
    registrations.register(500, "192.168.1.1:7001")
    registrations.register(500, "192.168.1.1:7002")
    registrations.register(500, "192.168.1.1:7003")
    registrations.register(500, "192.168.1.1:7004")
    registrations.register(501, "192.168.1.1:7001")
    registrations.register(501, "192.168.1.1:7002")

    registrations.unregister("192.168.1.1:7002")

    assert "192.168.1.1:7002" not in registrations.get_registrations(500)
    assert "192.168.1.1:7002" not in registrations.get_registrations(501)
    assert "192.168.1.1:7001" in registrations.get_registrations(501)
    print(registrations._api_registrations)

    registrations.unregister("192.168.1.1:7001")
    registrations.unregister("192.168.1.1:7003")
    registrations.unregister("192.168.1.1:7004")
    assert len(registrations.get_registrations(501)) == 0
    assert len(registrations.get_registrations(501)) == 0
