import cloudpassage
import operator
from multiprocessing.dummy import Pool as ThreadPool
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


class HaloEvents(object):
    """Initialize with Halo key and secret."""
    def __init__(self, key, secret, concurrency):
        self.concurrency = concurrency
        session = cloudpassage.HaloSession(key, secret)
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
