from halo_events_to_sumologic.halo_events import HaloEvents
import halo_events_to_sumologic as halo_events_package

def test_integration_string(monkeypatch):
    HaloEvents.helper = None
    halo_events = HaloEvents("fake_key", "fake_secret", "fake_concurrency")
    assert halo_events.get_integration_string() == "Halo-events-to-sumologic/%s" % halo_events_package.__version__