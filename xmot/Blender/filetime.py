from calendar import timegm
from datetime import datetime, timezone

EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
HUNDREDS_OF_NS = 10000000

def to_winfiletime(dt: datetime) -> int:
	if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
		dt = dt.replace(tzinfo=timezone.utc)
	filetime = EPOCH_AS_FILETIME + (timegm(dt.timetuple()) * HUNDREDS_OF_NS)
	return filetime + (dt.microsecond * 10)


def to_datetime(filetime: int) -> datetime:
	s, ns100 = divmod(filetime - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
	return datetime.utcfromtimestamp(s).replace(microsecond=(ns100 // 10))