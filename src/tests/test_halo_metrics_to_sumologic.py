import halo_metrics_to_sumologic.halo_metrics_to_sumologic as halo_metrics_to_sumologic
import halo_metrics_to_sumologic as halo_metrics

def test_integration_string():
    assert halo_metrics_to_sumologic.get_integration_string() == "Halo-metrics-to-sumologic/%s" % halo_metrics.__version__
