from datetime import datetime, timezone

def convert_to_unix_timestamp(str_timestamp):
    # Format of the input timestamp
    format_str = '%Y-%m-%d %H:%M:%S'

    # Convert string to datetime object
    datetime_obj = datetime.strptime(str_timestamp, format_str)

    # Convert to UTC and get the Unix timestamp
    unix_timestamp = datetime_obj.replace(tzinfo=timezone.utc).timestamp()
    return int(unix_timestamp)
