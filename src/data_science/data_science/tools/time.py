from datetime import datetime, timezone


def get_timestamp_isoformat():
    """
    Generate a timestampt in iso format.
    """
    dt = datetime.utcnow().replace(microsecond=0).isoformat("T") + "Z"
    return dt


def get_timestamp_unix():
    """
    Generate a timestampt in unix format.
    ########.###
    """
    dt = datetime.utcnow().replace()
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return timestamp
