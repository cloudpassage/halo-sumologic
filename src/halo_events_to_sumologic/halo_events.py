import cloudpassage
import operator
import os
import re
from multiprocessing.dummy import Pool as ThreadPool
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


class HaloEvents(object):
    """Initialize with Halo key and secret."""
    def __init__(self, key, secret, concurrency):
        self.concurrency = concurrency
        self.integration = self.get_integration_string()
        session = cloudpassage.HaloSession(key, secret, integration_string=self.integration)
        session.authenticate_client()
        self.helper = cloudpassage.HttpHelper(session)
        return

    def get_all_event_pages(self, since, until, pages):
        """Wraps threaded retrieval of events from Halo API.

        Args:
            since (str): Beginning timestamp.
            until (str): Ending timestamp.
            pages (int): Number of pages to retrieve.

        Returns:
            list: List of events from Halo API.
        """
        end_page = pages + 1
        page_getter = self.get_page_of_events
        pages = [self.generate_page_url(since, until, x)
                 for x in range(1, end_page)]
        pool = ThreadPool(self.concurrency)
        results = pool.map(page_getter, pages)
        items = []
        for page in results:
            items.extend(page)
        result = sorted(items, key=operator.itemgetter("created_at"))
        return result

    @classmethod
    def generate_page_url(cls, since, until, page_no):
        """Generates a URL for a page of events.

        Args:
             since (str): Starting timestamp.
             until (str): Ending timestamp.
             page_no (int): page number to be included in URL.

        Returns:
            str: URL for one page of events.
        """
        base_url = "/v1/events/"
        params = {"since": since, "until": until, "page": page_no}
        return "{path}?{opts}".format(path=base_url,
                                      opts=urlencode(dict(params)))

    def get_page_of_events(self, page_url):
        """Get a single page of events.

        Args:
            get_tup (tuple): contains key, secret, since, until, and page no.

        Returns:
            list: List of events from Halo API.
        """
        try:
            retval = self.helper.get(page_url)["events"]
        except cloudpassage.CloudPassageResourceExistence:
            retval = []
        return retval

    def get_integration_string(self):
        """Return integration string for this tool."""
        return "Halo-events-to-sumologic/%s" % self.get_tool_version()

    def get_tool_version(self):
        """Get version of this tool from the __init__.py file."""
        here_path = os.path.abspath(os.path.dirname(__file__))
        init_file = os.path.join(here_path, "__init__.py")
        ver = 0
        with open(init_file, 'r') as i_f:
            rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
            ver = rx_compiled.search(i_f.read()).group(1)
        return ver