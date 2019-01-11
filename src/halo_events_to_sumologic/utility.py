import json


class Utility(object):
    """General-purpose non-API-abstraction functionality."""
    @classmethod
    def generate_payload(cls, event_list):
        """Return a tuple with event list and last timetamp.

        Args:
            event_list (list): List of events in json format.

        Returns:
            tuple: tuple[0] contains a atring representation of event_list,
                and tuple[1] contains the last timestamp from event_list.
        """
        data = "\n".join([json.dumps(x, ensure_ascii=False).replace('\n', ' ')
                         for x in event_list])
        last_tstamp = event_list[-1]["created_at"]
        return (data, last_tstamp)

    @classmethod
    def generate_batches(cls, batch_size, events):
        """Return a list of tuples.

        This method returns a list of tuples where the first item in the tuple
        is a batch of events, converted to newline-delimited string. The second
        item in the tuple is an ISO-8601 timestamp extracted from the last
        event in the batch.

        Args:
            batch_size (str): Number of events to put into a single batch.
            events (list): List of events from Halo API.

        Returns:
            list: List of tuples.
        """
        batches = []
        while events:
            batches.append(cls.generate_payload(events[:batch_size]))
            del events[:batch_size]
        return batches
