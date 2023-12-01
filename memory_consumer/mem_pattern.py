"""
Implements class for representing time dependent pattern (pattern) of memory consumption.
"""
import csv
from datetime import datetime, timedelta
import random


class MemPattern:
    """Implements time-dependent pattern of memory consumption.

    It reads from specially prepared csv file amount of memory that needs
    to be allocated at specific time. Additionally, the amount of memory can be
    changed +/- of some percent of its original value (noise).

    Parameters
    ----------
    pattern_file_name : `str`
        csv file name with time-dependent values
    noise_percent : `int`, default=0
        percent of which the returned value can be changed
    """

    def __init__(self, pattern_file_name: str, noise_percent: int = 0):
        self.noise_percent = noise_percent
        self.pattern_file_name = pattern_file_name
        with open(pattern_file_name, mode="r", encoding="utf-8") as pattern_file:
            reader = csv.reader(pattern_file)
            header = next(reader, None)
            # pattern_type is detected from csv header column (without last column)
            self.pattern_type = header[:-1]
            self._data = {}
            res = 0
            i = 0
            for item in reader:
                key = tuple(int(v) for v in item[:-1])
                self._data[key] = int(item[-1])
                # smallest_unit_resolution is detected as difference of two first rows column[-2]
                if i == 0:
                    res = int(item[-2])
                if i == 1:
                    self.smallest_unit_resolution = int(item[-2]) - res
                i += 1
        # how long is the pattern duration in the smallest time units used
        self.pattern_duration = len(self._data) * self.smallest_unit_resolution

    def __repr__(self):
        return (
            f"MemPattern: {self.pattern_file_name}, type={self.pattern_type}, "
            f"noise +/- {self.noise_percent}%, "
            f"smallest unit resolution={self.smallest_unit_resolution}{self.pattern_type[-1]}, "
            f"pattern size={len(self._data)} points, "
            f"pattern duration (period)={self.get_pattern_duration_in_seconds()}s"
        )

    def _noise_value(self, value: int) -> int:
        """Returns noised value +/-self.noise_percent*value

        Parameters
        ----------
        value : int
            Input value.

        Returns
        -------
        int
            Returns noised value +/-self.noise_percent*value.
            The returned value is cut to be greater than 1.
        """
        if self.noise_percent == 0:
            return value
        margin = value * self.noise_percent // 100
        noised_value = random.randint(max(0, value - margin), value + margin)
        return noised_value

    def _build_key(self, d_t: datetime) -> tuple:
        """Builds key for input datetime to search for pattern value.

        The key is a tuple depending on pattern type.
        Is adjusted to smallest_unit_resolution.

        Parameters
        ----------
        d_t : datetime :
            Input datetime for which is computed key.

        Returns
        -------
        tuple
            Tuple consisting of (day, hour, minute, second) of d_t.
            Tuple length depends on pattern type and might be
            (day, hour, minute), (minute, second) (minute,), (second,).
        """
        if self.pattern_type == ["s"]:
            return (
                (d_t.second // self.smallest_unit_resolution)
                * self.smallest_unit_resolution,
            )
        if self.pattern_type == ["m"]:
            return (
                (d_t.minute // self.smallest_unit_resolution)
                * self.smallest_unit_resolution,
            )
        if self.pattern_type == ["m", "s"]:
            return (
                d_t.minute,
                (d_t.second // self.smallest_unit_resolution)
                * self.smallest_unit_resolution,
            )
        if self.pattern_type == ["h", "m"]:
            return (
                d_t.hour,
                (d_t.minute // self.smallest_unit_resolution)
                * self.smallest_unit_resolution,
            )
        if self.pattern_type == ["d", "h", "m"]:
            return (
                d_t.weekday(),
                d_t.hour,
                (d_t.minute // self.smallest_unit_resolution)
                * self.smallest_unit_resolution,
            )
        return None, None

    def get_pattern_duration_in_seconds(self) -> int:
        """
        Returns how long is the RAM usage pattern in seconds
        Returns
        -------
        int:
            number of second of the period of the RAM usage pattern
        """
        if self.pattern_type[-1] == "m":
            return self.pattern_duration * 60
        return self.pattern_duration

    def get_time_shift_from_start(self, date_time: datetime = None) -> timedelta:
        """
        Returns time shift between date_time and starting datetime of RAM usage pattern

        Parameters
        ----------
        date_time: datetime
            datetime from which time shift is computed,
            if not provided datetime.now() is used

        Returns
        -------
        timedelta:
            time shift between date_time argument and starting point of RAM usage pattern
        """
        d_t = date_time
        if date_time is None:
            d_t = datetime.now()
        dt_start = d_t
        if self.pattern_type == ["s"]:
            dt_start = datetime(
                d_t.year, d_t.month, d_t.day, d_t.hour, d_t.minute, 0, d_t.microsecond
            )
        elif self.pattern_type == ["m"]:
            dt_start = datetime(
                d_t.year, d_t.month, d_t.day, d_t.hour, 0, 0, d_t.microsecond
            )
        elif self.pattern_type == ["m", "s"]:
            dt_start = datetime(
                d_t.year, d_t.month, d_t.day, d_t.hour, 0, 0, d_t.microsecond
            )
        elif self.pattern_type == ["h", "m"]:
            dt_start = datetime(d_t.year, d_t.month, d_t.day, 0, 0, 0, d_t.microsecond)
        elif self.pattern_type == ["d", "h", "m"]:
            dt_start = datetime(d_t.year, d_t.month, d_t.day, 0, 0, 0, d_t.microsecond)
            dt_start = dt_start - timedelta(days=dt_start.weekday())
        return d_t - dt_start

    def get_value(self, date_time: datetime = None) -> int:
        """Compute required value for provided date_time.

        Parameters
        ----------
        date_time : datetime
            Datetime for which value is computed or for the current datetime if not provided.

        Returns
        -------
        int
            Amount of memory to be allocated according to loaded time-dependent pattern
            and according to set noise_percent.
        """
        d_t = date_time
        if date_time is None:
            d_t = datetime.now()
        key = self._build_key(d_t)
        value = self._data.get(key, None)
        noised_value = self._noise_value(value)
        return noised_value
