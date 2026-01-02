"""Timecode class for handling timecode calculations."""

# Standard Library Imports
from __future__ import annotations

import math
import sys
from fractions import Fraction
from typing import TYPE_CHECKING

from .helpers import _Framerate, _Timestamp

if TYPE_CHECKING:
    from collections.abc import Iterator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
    
#%%
class Timecode:
    """The main timecode class.

    Does all the calculation over frames, so the main data it holds is frames,
    then when required it converts the frames to a timecode by using the frame
    rate setting.
    
    Args:
        framerate (Fraction | str | int | float): The frame rate of the
            Timecode instance. If a str is given it should be one of ['23.976',
            '23.98', '24', '25', '29.97', '30', '50', '59.94', '60',
            'NUMERATOR/DENOMINATOR', 'ms'] where "ms" equals to 1000 fps.
            Otherwise, any integer or Fractional value is accepted. Can not be
            skipped. Setting the framerate will automatically set the
            :attr:`.drop_frame` attribute to correct value.
        start_timecode (None | str | Timecode): The start timecode. Use this to
            be able to set the timecode of this Timecode instance. It can be
            skipped and then the frames attribute will define the timecode, and
            if it is also skipped then the start_second attribute will define
            the start timecode, and if start_seconds is also skipped then the
            default value of '00:00:00:00' will be used. When using 'ms' frame
            rate, timecodes like '00:11:01.040' use '.040' as frame number.
            When used with other frame rates, '.040' represents a fraction of a
            second. So '00:00:00.040' at 25fps is 1 frame.
        start_seconds (int | float): A float or integer value showing the
            seconds.
        frames (int): Timecode objects can be initialized with an integer
            number showing the total frames.
        force_non_drop_frame (bool): If True, uses Non-Dropframe calculation
            for NTSC-rate multiples of 29.97 (59.94, 119.88) only. Has no
            meaning for any other framerate. It is False by default.
        reference_time_on_display (bool): If True, specify the raster scan time
            reference to the top of the display rather than the bottom.
            True: The 1st frame wall-clock time is 0.0 sec.
            False (default): The 1st frame wall-clock time is 1/fps sec: the
            drawing duration of the 1st frame is included.
            This parameter affects the reference for start_seconds.
    """
    def __init__(
        self,
        framerate: _Framerate,
        start_timecode: str | Self | None = None,
        start_seconds: None | float = None,
        frames: int | None = None,
        force_non_drop_frame: bool = False,
        reference_time_on_display: bool = False,
    ) -> None:
        self.fraction_frame = False
        self.usec_timestamps = False
        self.drop_frame = False

        self.framerate = framerate
        
        # Do not set drop_frame to true in the framerate setter: the user
        # could be switching NTSC rates with force_non_drop_frame=True
        # clearing drop_frame every time would be an annoyance.
        if not force_non_drop_frame and (self._int_framerate % 30) == 0:
            self.drop_frame = self._is_ntsc_rate
        
        # if true, the first frame display at t=0 sec and not t=1/fps
        # this impacts start_seconds and the time getters.
        self.reference_time_on_display = reference_time_on_display
        
        self._dispatch_set_frames(start_timecode=start_timecode,
                                  start_seconds=start_seconds,
                                  frames=frames)
        # set a default
        if getattr(self, "_frames", None) is None:
            self.frames = self.tc_to_frames("00:00:00:00")
            
    ####
        
    def _dispatch_set_frames(self, **kwargs) -> None:
        """Helper to dispatch the arguments to set the Timecode frames count.
        
        Args:
            kwargs (dict): dictionary of possible input values to set the frame
            count. The following order of priority applies:
                1. start_timecode: Timecode string, or Timecode object.
                2. frames: frames count of the Timecode.
                3. start_seconds: float or fraction in seconds.
        """
        if (start_timecode := kwargs.get("start_timecode")) is not None:
            self.frames = self.tc_to_frames(start_timecode)
        elif (frames := kwargs.get("frames")) is not None:
            self.frames = frames
        elif (start_seconds := kwargs.get("start_seconds")) is not None:
            if self.reference_time_on_display:
                start_seconds += Fraction(1, self._int_framerate)

            if start_seconds <= 0:
                raise ValueError("``start_seconds`` argument can not be 0")
            self.frames = self.seconds_to_tc(start_seconds)
    #### 

    @staticmethod
    def _check_ntsc_rate(fps: Fraction) -> tuple[bool, int]:
        """Check if framerate is NTSC (multiple of 24000/1001 or 30000/1001).

        NTSC rates follow the pattern: nominal_rate * 1000/1001
        Examples: 23.976, 29.97, 47.952, 59.94, 71.928, 89.91, 95.904, 119.88

        Args:
            fps (float): The framerate to check.

        Returns:
            tuple: (is_ntsc, int_framerate) where is_ntsc is True if this is an
                NTSC rate, and int_framerate is the rounded integer framerate.
        """
        # Calculate what the integer framerate would be if this is NTSC
        int_fps = round(fps * 1001 / 1000)

        # Calculate what the NTSC rate would be for this integer framerate
        expected_ntsc = int_fps * 1000 / 1001

        # Check if the input matches expected NTSC rate (within tolerance)
        is_ntsc = abs(fps - expected_ntsc) < 0.005

        return is_ntsc, int_fps

    @property
    def framerate(self) -> Fraction:
        """Framerate getter.

        Returns:
            Fraction: The Timecode framerate, as a fraction of two integers.
        """
        return self._framerate

    @framerate.setter
    def framerate(self, new_framerate: _Framerate) -> None:
        """Set a framerate to the Timecode instance.

        Args:
            new_framerate (_Framerate): The framerate to use

        The provided rate is converted to a fraction. Special values "ms" and
        "frames" are accepted to specify 1/1000 or 1/1 (resp.)

        """
        if isinstance(new_framerate, str):
            if new_framerate == "ms":
                new_framerate = 1000
            elif new_framerate == "frames":
                new_framerate = 1
        
        if isinstance(new_framerate, (tuple, list)):
            new_framerate = tuple(map(int, new_framerate))
            new_fps = Fraction(*new_framerate)
        else:
            new_fps = Fraction(new_framerate)
        if new_fps.numerator <= 0:
            raise ValueError("Invalid framerate (zero or negative).")
        
        self.ms_frame = (new_fps == 1000)
        if not self.ms_frame:
            self._is_ntsc_rate, self._int_framerate = \
                __class__._check_ntsc_rate(new_fps)
        else:
            self._is_ntsc_rate, self._int_framerate = False, int(new_fps)

        # Fix ambiguous values like 23976/1000 or 23.98.
        if self._is_ntsc_rate and new_fps.denominator != 1001:
            new_fps = Fraction(self._int_framerate * 1000, 1001)

        # No more a NTSC framerate. Only clear as the TC could be forced to NDF
        if self.drop_frame and \
            (not self._is_ntsc_rate or (self._int_framerate % 30) > 0):
            self.drop_frame = False
        self._framerate = new_fps

    def to_systemtime(self) -> _Timestamp:
        """Convert a Timecode to the video system timestamp.

        For NTSC rates, the video system time is not the wall-clock one.

        Returns:
            _Timestamp of the "system time" of the Timecode.
        """
        display_delay = int(not self.reference_time_on_display)
        hh, mm, ss, ff = self.frames_to_tc(self.frames, skip_rollover=True)
        ts = ss + 60 * (mm + 60 * hh)
        ts += Fraction((ff + display_delay), self._int_framerate)
        return _Timestamp(ts, usec_precision=self.usec_timestamps)

    def to_realtime(self) -> _Timestamp:
        """Convert a Timecode to the wall-clock (real time) timestamp.

        For NTSC rates, the real time value differs from the system time.

        Returns:
            _Timestamp of the "real time" of the Timecode.
        """
        ts = Fraction(self.frames, self.framerate)
        ts -= Fraction(int(self.reference_time_on_display), self.framerate)
        return _Timestamp(ts, usec_precision=self.usec_timestamps)

    @property
    def frames(self) -> int:
        """Return the _frames attribute value.

        Returns:
            int: The frames attribute value.
        """
        return self._frames  # type: ignore

    @frames.setter
    def frames(self, frames: int) -> None:
        """Set the_frames attribute.

        Args:
            frames (int): A positive int bigger than zero showing the number of frames
                that this Timecode represents.
        """
        # validate the frames value
        if not isinstance(frames, int):
            raise TypeError(
                f"{self.__class__.__name__}.frames should be a positive integer bigger "
                f"than zero, not a {frames.__class__.__name__}"
            )

        if frames <= 0:
            raise ValueError(
                f"{self.__class__.__name__}.frames should be a positive "
                f"integer bigger than zero, not {frames}"
            )
        self._frames = frames
        
    def set_timecode(self, timecode: str | Timecode) -> None:
        """Set the frames by using the given timecode.

        Args:
            timecode (str | Timecode): Either a str representation of a
                Timecode or a Timecode instance.
        """
        self.frames = self.tc_to_frames(timecode)

    def seconds_to_tc(self, seconds: float | Fraction) -> int:
        """Return the number of frames in the given seconds using the current instance.

        Args:
            seconds (float): The seconds to set hte timecode to. This uses the integer
                frame rate for proper calculation.

        Returns:
            int: The number of frames in the given seconds.
        """
        return int(seconds * self._int_framerate)

    def tc_to_frames(self, timecode: str | Timecode) -> int:
        """Convert the given Timecode to frames.

        Args:
            timecode (str | Timecode): Either a str representing a Timecode or
                a Timecode instance.

        Returns:
            int: The number of frames in the given Timecode.
        """
        # timecode could be a Timecode instance
        if isinstance(timecode, Timecode):
            return timecode.frames

        hours, minutes, seconds, frames = map(int, self.parse_timecode(timecode))

        if isinstance(timecode, int):
            time_tokens = [hours, minutes, seconds, frames]
            timecode = ":".join(str(t) for t in time_tokens)

            if self.drop_frame:
                timecode = ";".join(timecode.rsplit(":", 1))

        # Number of drop frames is 6% of framerate rounded to nearest integer
        drop_frames = round(self.framerate * 0.066666) if self.drop_frame else 0

        # We don't need the exact framerate anymore, we just need it rounded to
        # nearest integer
        ifps = self._int_framerate

        # Number of frames per hour (non-drop)
        hour_frames = ifps * 60 * 60

        # Number of frames per minute (non-drop)
        minute_frames = ifps * 60

        # Total number of minutes
        total_minutes = (60 * hours) + minutes

        # Handle case where frames are fractions of a second
        if len(timecode.split(".")) == 2 and not self.ms_frame:
            self.fraction_frame = True
            fraction = timecode.rsplit(".", 1)[1]

            frames = round(float("." + fraction) * float(self.framerate))

        frame_number = (
            (hour_frames * hours)
            + (minute_frames * minutes)
            + (ifps * seconds)
            + frames
        ) - (drop_frames * (total_minutes - (total_minutes // 10)))

        return frame_number + 1  # frames

    def frames_to_tc(
        self, frames: int, skip_rollover: bool = False
    ) -> tuple[int, int, int, int | float]:
        """Convert frames back to timecode.

        Args:
            frames (int): Number of frames.
            skip_rollover (bool): If True, the frame number will not rollover
                after 24 hours.

        Returns:
            tuple: A tuple containing the hours, minutes, seconds and frames
        """
        if self.drop_frame:
            # Number of frames to drop on the minute marks is the nearest
            # integer to 6% of the framerate
            ffps = round(self.framerate, 2)
            drop_frames = round(ffps * 0.066666)
        else:
            ffps = self._int_framerate
            drop_frames = 0

        # Number of frames per ten minutes
        frames_per_10_minutes = round(ffps * 60 * 10)

        # Number of frames in a day - timecode rolls over after 24 hours
        frames_per_24_hours = round(ffps * 60 * 60 * 24)

        # Number of frames per minute is the round of the framerate * 60 minus
        # the number of dropped frames
        frames_per_minute = int(self._int_framerate * 60) - drop_frames

        frame_number = frames - 1

        # If frame_number is greater than 24 hrs, next operation will rollover
        # clock
        if not skip_rollover:
            frame_number %= frames_per_24_hours

        if self.drop_frame:
            d = frame_number // frames_per_10_minutes
            m = frame_number % frames_per_10_minutes
            if m > drop_frames:
                frame_number += (drop_frames * 9 * d) + drop_frames * (
                    (m - drop_frames) // frames_per_minute
                )
            else:
                frame_number += drop_frames * 9 * d

        ifps = self._int_framerate

        frs: int | float = frame_number % ifps
        if self.fraction_frame:
            frs = round(frs / ifps, 3)

        secs = int((frame_number // ifps) % 60)
        mins = int(((frame_number // ifps) // 60) % 60)
        hrs = int(((frame_number // ifps) // 60) // 60)

        return hrs, mins, secs, frs
    def tc_to_string(self, hrs: int, mins: int, secs: int, frs: float) -> str:
        """Return the string representation of a Timecode with given info.

        Args:
            hrs (int): The hours portion of the Timecode.
            mins (int): The minutes portion of the Timecode.
            secs (int): The seconds portion of the Timecode.
            frs (int | float): The frames portion of the Timecode.

        Returns:
            str: The string representation of this Timecode.
        """
        if self.fraction_frame:
            return f"{hrs:02d}:{mins:02d}:{secs + frs:06.3f}"

        ff = "{:02d}"
        if self.ms_frame:
            ff = "{:03d}"

        return ("{:02d}:{:02d}:{:02d}{}" + ff).format(
            hrs, mins, secs, self.frame_delimiter, frs
        )

    @classmethod
    def parse_timecode(cls, timecode: int | str) -> tuple[int, int, int, int]:
        """Parse the given timecode string.

        This uses the frame separator do decide if this is a NDF, DF or a
        or milliseconds/fraction_of_seconds based Timecode.

        '00:00:00:00' will result a NDF Timecode where, '00:00:00;00' will result a DF
        Timecode or '00:00:00.000' will be a milliseconds/fraction_of_seconds based
        Timecode.

        Args:
            timecode (int | str): If an integer is given it is converted to hex
                and the hours, minutes, seconds and frames are extracted from the hex
                representation. If a str is given it should follow one of the SMPTE
                timecode formats.ß

        Returns:
            (int, int, int, int): A tuple containing the hours, minutes, seconds and
                frames part of the Timecode.
        """
        if isinstance(timecode, int):
            hex_repr = hex(timecode)
            # fix short string
            hex_repr = f"0x{hex_repr[2:].zfill(8)}"
            hrs, mins, secs, frs = tuple(
                map(int, [hex_repr[i : i + 2] for i in range(2, 10, 2)])
            )

        else:
            bfr = timecode.replace(";", ":").replace(".", ":").split(":")
            hrs = int(bfr[0])
            mins = int(bfr[1])
            secs = int(bfr[2])
            frs = int(bfr[3])

        return hrs, mins, secs, frs

    @property
    def frame_delimiter(self) -> str:
        """Return correct frame deliminator symbol based on the framerate.

        Returns:
            str: The frame deliminator, ";" if this is a drop frame timecode, "." if
                this is a millisecond based Timecode or ":" in any other case.
        """
        if self.drop_frame:
            return ";"

        if self.ms_frame or self.fraction_frame:
            return "."

        return ":"

    def __iter__(self) -> Iterator[Self]:
        """Yield an iterator.

        Yields:
            Timecode: Yields this Timecode instance.
        """
        yield self

    def next(self) -> Self:
        """Add one frame to this Timecode to go the next frame.

        Returns:
            Timecode: Returns self. So, this is the same Timecode instance with this
                one.
        """
        self.add_frames(1)
        return self

    def set_fractional(self, state: bool) -> None:
        """Set if the Timecode is to be represented with fractional seconds.

        Args:
            state (bool): If set to True the current Timecode instance will be
                represented with a fractional seconds (will have a "." in the frame
                separator).
        """
        self.fraction_frame = state

    def back(self) -> Self:
        """Subtract one frame from this Timecode to go back one frame.

        Returns:
            Timecode: Returns self. So, this is the same Timecode instance with this
                one.
        """
        self.sub_frames(1)
        return self

    def add_frames(self, frames: int) -> None:
        """Add or subtract frames from the number of frames of this Timecode.

        Args:
            frames (int): The number to subtract from or add to the number of frames of
                this Timecode instance.
        """
        self.frames += frames

    def sub_frames(self, frames: int) -> None:
        """Add or subtract frames from the number of frames of this Timecode.

        Args:
            frames (int): The number to subtract from or add to the number of frames of
                this Timecode instance.
        """
        self.add_frames(-frames)

    def mult_frames(self, frames: int) -> None:
        """Multiply frames.

        Args:
            frames (int): Multiply the frames with this number.
        """
        self.frames *= frames

    def div_frames(self, frames: int) -> None:
        """Divide the number of frames to the given number.

        Args:
            frames (int): The other number to divide the number of frames of this
                Timecode instance to.
        """
        self.frames = int(self.frames / frames)

    def _copy_props_from(self, other: Timecode) -> None:
        self.drop_frame = other.drop_frame
        self.fraction_frame = other.fraction_frame
        self.usec_timestamps = other.usec_timestamps
        self.reference_time_on_display = other.reference_time_on_display

    def __eq__(self, other: int | str | Timecode | object) -> bool:
        """Override the equality operator.

        Args:
            other (int | str | Timecode): Either and int representing the
                number of frames, a str representing the start time of a
                Timecode with the same frame rate of this one, or a Timecode to
                compare with the number of frames.

        Returns:
            bool: True if the other is equal to this Timecode instance.
        """
        if isinstance(other, Timecode):
            return self.framerate == other.framerate and self.frames == other.frames
        if isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.__eq__(new_tc)
        if isinstance(other, int):
            return self.frames == other
        return False

    def __ge__(self, other: int | str | Timecode | object) -> bool:
        """Override greater than or equal to operator.

        Args:
            other (int | str | Timecode): Either and int representing the
                number of frames, a str representing the start time of a
                Timecode with the same frame rate of this one, or a Timecode to
                compare with the number of frames.

        Returns:
            bool: True if the other is greater than or equal to this Timecode
                instance.
        """
        if isinstance(other, Timecode):
            return self.framerate == other.framerate and self.frames >= other.frames
        if isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.frames >= new_tc.frames
        if isinstance(other, int):
            return self.frames >= other
        raise TypeError(
            "'>=' not supported between instances of 'Timecode' and "
            f"'{other.__class__.__name__}'"
        )

    def __gt__(self, other: int | str | Timecode) -> bool:
        """Override greater than operator.

        Args:
            other (int | str, Timecode): Either and int representing the number
                of frames, a str representing the start time of a Timecode with
                the same frame rate of this one, or a Timecode to compare with
                the number of frames.

        Returns:
            bool: True if the other is greater than this Timecode instance.
        """
        if isinstance(other, Timecode):
            return self.framerate == other.framerate and self.frames > other.frames
        if isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.frames > new_tc.frames
        if isinstance(other, int):
            return self.frames > other
        raise TypeError(
            "'>' not supported between instances of 'Timecode' and "
            f"'{other.__class__.__name__}'"
        )

    def __le__(self, other: int | str | Timecode | object) -> bool:
        """Override less or equal to operator.

        Args:
            other (int | str | Timecode): Either and int representing the number of
                frames, a str representing the start time of a Timecode with the same
                frame rate of this one, or a Timecode to compare with the number of
                frames.

        Returns:
            bool: True if the other is less than or equal to this Timecode instance.
        """
        if isinstance(other, Timecode):
            return self.framerate == other.framerate and self.frames <= other.frames
        if isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.frames <= new_tc.frames
        if isinstance(other, int):
            return self.frames <= other
        raise TypeError(
            "'<' not supported between instances of 'Timecode' and "
            f"'{other.__class__.__name__}'"
        )

    def __lt__(self, other: int | str | Timecode) -> bool:
        """Override less than operator.

        Args:
            other (int | str | Timecode): Either and int representing the number of
                frames, a str representing the start time of a Timecode with the same
                frame rate of this one, or a Timecode to compare with the number of
                frames.

        Returns:
            bool: True if the other is less than this Timecode instance.
        """
        if isinstance(other, Timecode):
            return self.framerate == other.framerate and self.frames < other.frames
        if isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.frames < new_tc.frames
        if isinstance(other, int):
            return self.frames < other
        raise TypeError(
            "'<=' not supported between instances of 'Timecode' and "
            f"'{other.__class__.__name__}'"
        )

    def __add__(self, other: int | Timecode) -> Timecode:
        """Return a new Timecode with the given timecode or frames added to this one.

        Args:
            other (int | Timecode): Either and int value or a Timecode in which
                the frames are used for the calculation.

        Raises:
            TimecodeError: If the other is not an int or Timecode.

        Returns:
            Timecode: The resultant Timecode instance.
        """
        # duplicate current one
        tc = Timecode(self.framerate, frames=self.frames)
        tc._copy_props_from(self)

        if isinstance(other, Timecode):
            tc.add_frames(other.frames)
        elif isinstance(other, int):
            tc.add_frames(other)
        else:
            raise TimecodeError(
                f"Type {other.__class__.__name__} not supported for arithmetic."
            )

        return tc

    def __sub__(self, other: int | Timecode) -> Timecode:
        """Return a new Timecode instance with subtracted value.

        Args:
            other (int | Timecode): The number to subtract, either an integer or
                another Timecode in which the number of frames is subtracted.

        Raises:
            TimecodeError: If the other is not an int or Timecode.

        Returns:
            Timecode: The resultant Timecode instance.
        """
        if isinstance(other, Timecode):
            subtracted_frames = self.frames - other.frames
        elif isinstance(other, int):
            subtracted_frames = self.frames - other
        else:
            raise TimecodeError(
                f"Type {other.__class__.__name__} not supported for arithmetic."
            )
        tc = Timecode(self.framerate, frames=abs(subtracted_frames))
        tc._copy_props_from(self)
        return tc

    def __mul__(self, other: int | Timecode) -> Timecode:
        """Return a new Timecode instance with multiplied value.

        Args:
            other (int | Timecode): The multiplier either an integer or another
                Timecode in which the number of frames is used as the multiplier.

        Raises:
            TimecodeError: If the other is not an int or Timecode.

        Returns:
            Timecode: The resultant Timecode instance.
        """
        if isinstance(other, Timecode):
            multiplied_frames = self.frames * other.frames
        elif isinstance(other, int):
            multiplied_frames = self.frames * other
        else:
            raise TimecodeError(
                f"Type {other.__class__.__name__} not supported for arithmetic."
            )
        tc = Timecode(self.framerate, frames=multiplied_frames)
        tc._copy_props_from(self)
        return tc

    def __div__(self, other: int | Timecode) -> Timecode:
        """Return a new Timecode instance with divided value.

        Args:
            other (int | Timecode): The denominator either an integer or another
                Timecode in which the number of frames is used as the denominator.

        Raises:
            TimecodeError: If the other is not an int or Timecode.

        Returns:
            Timecode: The resultant Timecode instance.
        """
        if isinstance(other, Timecode):
            div_frames = int(self.frames / other.frames)
        elif isinstance(other, int):
            div_frames = int(self.frames / other)
        else:
            raise TimecodeError(
                f"Type {other.__class__.__name__} not supported for arithmetic."
            )
        tc = Timecode(self.framerate, frames=div_frames)
        tc._copy_props_from(self)
        return tc

    def __truediv__(self, other: int | Timecode) -> Timecode:
        """Return a new Timecode instance with divided value.

        Args:
            other (int | Timecode): The denominator either an integer or another
                Timecode in which the number of frames is used as the denominator.

        Returns:
            Timecode: The resultant Timecode instance.
        """
        return self.__div__(other)

    def __float__(self) -> float:
        """Convert this Timecode instance to a float representation (seconds).

        Returns:
            float: The float representation (seconds).
        """
        offset = int(self.reference_time_on_display)
        seconds = float((self.frames - offset)/self._int_framerate)
        return math.nextafter(seconds, math.inf)

    def __str__(self) -> str:
        """Return the actual Timecode as a string.

        Returns:
            str: The string of this Timecode.
        """
        return self.tc_to_string(*self.frames_to_tc(self.frames))
        
    def __repr__(self) -> str:
        """Return the string representation of this Timecode instance.

        Returns:
            str: The string representation of this Timecode instance.
        """
        # use frames= as that is agnostic to drop_frame
        return f"{__class__.__name__}('{self.framerate}', frames={self.frames})"

    @property
    def hrs(self) -> int:
        """Return the hours part of the timecode.

        Returns:
            int: The hours part of the timecode.
        """
        hrs, _, _, _ = self.frames_to_tc(self.frames)
        return hrs

    @property
    def mins(self) -> int:
        """Return the minutes part of the timecode.

        Returns:
            int: The minutes part of the timecode.
        """
        _, mins, _, _ = self.frames_to_tc(self.frames)
        return mins

    @property
    def secs(self) -> int:
        """Return the seconds part of the timecode.

        Returns:
            int: The seconds part of the timecode.
        """
        _, _, secs, _ = self.frames_to_tc(self.frames)
        return secs

    @property
    def frs(self) -> int | float:
        """Return the frames part of the timecode.

        Returns:
            int: The frames part of the timecode.
        """
        _, _, _, frs = self.frames_to_tc(self.frames)
        return frs

    @property
    def frame_number(self) -> int:
        """Return the 0-based frame number of the current timecode instance.

        Returns:
            int: 0-based frame number.
        """
        return self.frames - 1


    @property
    def float(self) -> float:
        """Return the seconds as float.

        Returns:
            float: The seconds as float.
        """
        return float(self)
####

#%%
class TimecodeBuilder:
    """Helper class to pre-configure instantiation of Timecodes.
    
    A list of kwargs of class Timecode can be provided to the builder, which
    will be used when the builder instance is called to create new Timecodes.
    
    Args:
        kwargs (dict): list of pre-configured arguments for the Timecodes
        instantiated by calling this builder. Refer to Timecode docu.
    """

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> Timecode:
        """Create a Timecode combining the preconfigured and user arguments.
        
        Returns:
            Timecode: timecode instance given the arguments.
        """
        kwargs = self.kwargs | kwargs
        return Timecode(*args, **kwargs)
####

#%%
class TimecodeError(Exception):
    """Raised when an error occurred in timecode calculation."""

