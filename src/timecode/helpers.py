"""Helper class for Timecode handling and byproducts."""

from __future__ import annotations

import sys
from fractions import Fraction
from typing import NewType

if sys.version_info >= (3, 11):
    _frate_type = Fraction | str | float | tuple[int, int]
else:
    from typing import Union
    _frate_type = Union[Fraction, str, float, tuple[int, int]]

_Framerate = NewType("_Framerate", _frate_type)

class _Timestamp:
    def __init__(self, ts: Fraction, usec_precision: bool = False) -> None:
        if ts < 0:
            raise ValueError(f"Timestamp cannot be negative, got {ts}.")
        self.usec_precision = usec_precision
        self._exact_ts = ts
        
    def __float__(self) -> float:
        """Convert this _Timestamp instance to a float (timestamp in seconds).
        
        Returns:
            float: timestamp value in seconds of this instance
        """
        return float(self._exact_ts)    
    
    def total_seconds(self) -> float:
        """Return the time in seconds of this Timestamp instance as a float.
        
        Returns:
            float: timestamp value in seconds of this instance
            
        Truncation is possible, it's not an exact representation.
        """
        return float(self)
    
    def exact(self) -> Fraction:
        """Return the time in seconds of this Timestamp instance as a fraction.
        
        Returns:
            Fraction: exact timestamp value in seconds of this instance.
        """
        return self._exact_ts
    
    def __eq__(self, other: _Timestamp | float | Fraction) -> bool:
        """Equal implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts == other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts == other
        if isinstance(other, (float, int)):
            return float(self) == other
        return NotImplemented

    def __ne__(self, other: _Timestamp | float | Fraction) -> bool:
        """Not equal implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts != other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts != other
        if isinstance(other, (float, int)):
            return float(self) != other
        return NotImplemented

    def __lt__(self, other: _Timestamp | float | Fraction) -> bool:
        """Less than implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts < other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts < other
        if isinstance(other, (float, int)):
            return float(self) < other
        return NotImplemented

    def __gt__(self, other: _Timestamp | float | Fraction) -> bool:
        """Greater than implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts > other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts > other
        if isinstance(other, (float, int)):
            return float(self) > other
        return NotImplemented

    def __le__(self, other: _Timestamp | float | Fraction) -> bool:
        """Less or equal implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts <= other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts <= other
        if isinstance(other, (float, int)):
            return float(self) <= other
        return NotImplemented
    
    def __ge__(self, other: _Timestamp | float | Fraction) -> bool:
        """Greater or equal implementation for _Timestamp instance.
        
        Args:
            other (_Timestamp | int | float | Fraction): object to compare 
            instance to.

        Returns:
            Result of the operation.
        """
        if isinstance(other, __class__):
            return self._exact_ts >= other._exact_ts
        if isinstance(other, Fraction):
            return self._exact_ts >= other
        if isinstance(other, (float, int)):
            return float(self) >= other
        return NotImplemented

    def __str__(self) -> str:
        """Convert the _Timestamp instance to a timestamp string.
        
        Returns:
            string: Timestamp string of this _Timestamp instance.
        """
        hh = int(self._exact_ts // 3600)
        mm = int(self._exact_ts // 60) % 60
        ss = int(self._exact_ts % 60)
        decimal_part = (self._exact_ts - int(self._exact_ts))*1000
        
        if self.usec_precision:
            s_decimal_part = f"{round(decimal_part*1000):>06}"
        else:
            s_decimal_part = f"{round(decimal_part):03}"
        return f"{hh:02d}:{mm:02d}:{ss:02d}.{s_decimal_part}"

    def __repr__(self) -> str:
        """Represent a _Timestamp instance.
        
        Returns:
            string: representation of this _Timestamp instance.
        """
        usec_part = f", usec_precision={self.usec_precision}" * self.usec_precision
        return f"{__class__.__name__}({self._exact_ts}{usec_part})"
####
