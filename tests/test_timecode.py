#!-*- coding: utf-8 -*-
import pytest

from timecode import Timecode, TimecodeError

from fractions import Fraction
import random

@pytest.mark.parametrize(
    "args,kwargs",
    [
        [["12", "00:00:00:00"], {}],
        [["23.976", "00:00:00:00"], {}],
        [["23.98", "00:00:00:00"], {}],
        [["24", "00:00:00:00"], {}],
        [["25", "00:00:00:00"], {}],
        [["29.97", "00:00:00;00"], {}],
        [["30", "00:00:00:00"], {}],
        [["50", "00:00:00:00"], {}],
        [["59.94", "00:00:00;00"], {}],
        [["60", "00:00:00:00"], {}],
        [["72", "00:00:00:00"], {}],
        [["96", "00:00:00:00"], {}],
        [["100", "00:00:00:00"], {}],
        [["119.88", "00:00:00;00"], {}],
        [["120", "00:00:00:00"], {}],
        [["ms", "03:36:09.230"], {}],
        [["24"], {"start_timecode": None, "frames": 12000}],
        [["23.976"], {}],
        [["23.98"], {}],
        [["24"], {}],
        [["25"], {}],
        [["29.97"], {}],
        [["30"], {}],
        [["50"], {}],
        [["59.94"], {}],
        [["60"], {}],
        [["ms"], {}],
        [["23.976", 421729315], {}],
        [["23.98", 421729315], {}],
        [["24", 421729315], {}],
        [["25", 421729315], {}],
        [["29.97", 421729315], {}],
        [["30", 421729315], {}],
        [["50", 421729315], {}],
        [["59.94", 421729315], {}],
        [["60", 421729315], {}],
        [["ms", 421729315], {}],
        [["24000/1000", "00:00:00:00"], {}],
        [["24000/1001", "00:00:00;00"], {}],
        [["30000/1000", "00:00:00:00"], {}],
        [["30000/1001", "00:00:00;00"], {}],
        [["60000/1000", "00:00:00:00"], {}],
        [["60000/1001", "00:00:00;00"], {}],
        [["72000/1000", "00:00:00:00"], {}],
        [["96000/1000", "00:00:00:00"], {}],
        [["100000/1000", "00:00:00:00"], {}],
        [["120000/1000", "00:00:00:00"], {}],
        [["120000/1001", "00:00:00;00"], {}],
        [[(24000, 1000), "00:00:00:00"], {}],
        [[(24000, 1001), "00:00:00;00"], {}],
        [[(30000, 1000), "00:00:00:00"], {}],
        [[(30000, 1001), "00:00:00;00"], {}],
        [[(60000, 1000), "00:00:00:00"], {}],
        [[(60000, 1001), "00:00:00;00"], {}],
        [[(72000, 1000), "00:00:00:00"], {}],
        [[(96000, 1000), "00:00:00:00"], {}],
        [[(100000, 1000), "00:00:00:00"], {}],
        [[(120000, 1000), "00:00:00:00"], {}],
        [[(120000, 1001), "00:00:00;00"], {}],
        [[12], {"frames": 12000}],
        [[24], {"frames": 12000}],
        [[23.976, "00:00:00:00"], {}],
        [[23.98, "00:00:00:00"], {}],
        [[24, "00:00:00:00"], {}],
        [[25, "00:00:00:00"], {}],
        [[29.97, "00:00:00;00"], {}],
        [[30, "00:00:00:00"], {}],
        [[50, "00:00:00:00"], {}],
        [[59.94, "00:00:00;00"], {}],
        [[60, "00:00:00:00"], {}],
        [[1000, "03:36:09.230"], {}],
        [[24], {"start_timecode": None, "frames": 12000}],
        [[23.976], {}],
        [[23.98], {}],
        [[24], {}],
        [[25], {}],
        [[29.97], {}],
        [[30], {}],
        [[50], {}],
        [[60], {}],
        [[1000], {}],
        [[24], {"frames": 12000}],
    ],
)
def test_instance_creation(args, kwargs):
    """Instance creation, none of these should raise any error."""
    tc = Timecode(*args, **kwargs)
    assert isinstance(tc, Timecode)


def test_2398_vs_23976():
    """Test 23.98 vs 23.976 fps."""
    tc1 = Timecode("23.98", "04:01:45:23")
    tc2 = Timecode("23.976", "04:01:45:23")
    assert tc1._frames == tc2._frames
    assert repr(tc1) == repr(tc2)


@pytest.mark.parametrize(
    "args,kwargs,expected_result,operator",
    [
        [["24", "01:00:00:00"], {}, "01:00:00:00", True],
        [["23.98", "20:00:00:00"], {}, "20:00:00:00", True],
        [["29.97", "00:09:00;00"], {}, "00:08:59;28", True],
        [["29.97", "00:09:00:00"], {"force_non_drop_frame": True}, "00:09:00:00", True],
        [["30", "00:10:00:00"], {}, "00:10:00:00", True],
        [["60", "00:00:09:00"], {}, "00:00:09:00", True],
        [["59.94", "00:00:20;00"], {}, "00:00:20;00", True],
        [["59.94", "00:00:20;00"], {}, "00:00:20:00", False],
        [["72", "00:00:09:00"], {}, "00:00:09:00", True],
        [["96", "00:00:09:00"], {}, "00:00:09:00", True],
        [["100", "00:00:09:00"], {}, "00:00:09:00", True],
        [["120", "00:00:09:00"], {}, "00:00:09:00", True],
        [["119.88", "00:00:20;00"], {}, "00:00:20;00", True],
        [["119.88", "00:00:20;00"], {}, "00:00:20:00", False],
        [["119.88", "01:30:45;100"], {}, "01:30:45;100", True],
        [
            ["119.88", "00:09:00:00"],
            {"force_non_drop_frame": True},
            "00:09:00:00",
            True,
        ],
        [["ms", "00:00:00.900"], {}, "00:00:00.900", True],
        [["ms", "00:00:00.900"], {}, "00:00:00:900", False],
        [["24"], {"frames": 49}, "00:00:02:00", True],
        [["59.94", "00:09:00:00"], {"force_non_drop_frame": True}, "00:09:00:00", True],
        [["59.94", "04:20:13;21"], {}, "04:20:13;21", True],
        [["59.94"], {"frames": 935866}, "04:20:13;21", True],
    ],
)
def test_repr_overload(args, kwargs, expected_result, operator):
    """Several timecode initialization."""
    tc = Timecode(*args, **kwargs)
    if operator:
        assert expected_result == tc.__str__()
    else:
        assert expected_result != tc.__str__()


def test_repr_overload_2():
    """Several timecode initialization."""
    tc1 = Timecode("59.94", frames=32401, force_non_drop_frame=True)
    tc2 = Timecode("59.94", "00:09:00:00", force_non_drop_frame=True)
    assert tc1 == tc2


@pytest.mark.parametrize(
    "args,kwargs,expected_repr,expected_frames,is_drop_frame",
    [
        [["29.97"], {}, "00:00:00;00", 1, None],
        [["29.97"], {"force_non_drop_frame": True}, "00:00:00:00", 1, None],
        [["29.97", "00:00:00;01"], {"force_non_drop_frame": True}, None, 2, None],
        [["29.97", "00:00:00:01"], {"force_non_drop_frame": True}, None, 2, None],
        [["29.97", "03:36:09;23"], {"force_non_drop_frame": False}, None, 388704, None],
        [["29.97", "03:36:09:23"], {"force_non_drop_frame": True}, None, 389094, None],
        [["29.97", "03:36:09;23"], {}, None, 388704, None],
        [["30", "03:36:09:23"], {}, None, 389094, None],
        [["25", "03:36:09:23"], {}, None, 324249, None],
        [["59.94", "03:36:09;23"], {}, None, 777384, None],
        [["60", "03:36:09:23"], {}, None, 778164, None],
        [["59.94", "03:36:09;23"], {}, None, 777384, None],
        [["72", "03:36:09:23"], {}, None, 933792, None],
        [["96", "03:36:09:23"], {}, None, 1245048, None],
        [["100", "03:36:09:23"], {}, None, 1296924, None],
        [["120", "03:36:09:23"], {}, None, 1556304, None],
        [["119.88", "03:36:09;23"], {}, None, 1554744, None],
        [["23.98", "03:36:09:23"], {}, None, 311280, None],
        [["24", "03:36:09:23"], {}, None, 311280, None],
        [["24"], {"frames": 12000}, "00:08:19:23", None, None],
        [["25", 421729315], {}, "19:23:14:23", None, None],
        [["29.97", 421729315], {}, "19:23:14;23", None, True],
        [["119.88"], {"frames": 1554744}, "03:36:09;23", None, True],
        [["23.98"], {"frames": 311280 * 720}, "01:59:59:23", None, None],
        [["23.98"], {"frames": 172800}, "01:59:59:23", None, None],
    ],
)
def test_timecode_str_repr_tests(
    args, kwargs, expected_repr, expected_frames, is_drop_frame
):
    """Several timecode initialization."""
    tc = Timecode(*args, **kwargs)
    if expected_repr is not None:
        assert expected_repr == tc.__str__()
    if expected_frames is not None:
        assert expected_frames == tc._frames
    if is_drop_frame is not None:
        if is_drop_frame is True:
            assert tc.drop_frame is True
        else:
            assert tc.drop_frame is False


def test_start_seconds_argument_is_zero():
    """ValueError is raised if the start_seconds parameters is zero."""
    with pytest.raises(ValueError) as cm:
        Timecode("29.97", start_seconds=0)

    assert str(cm.value) == "``start_seconds`` argument can not be 0"


@pytest.mark.parametrize(
    "args,kwargs,hrs,mins,secs,frs,str_repr",
    [
        [["ms", "03:36:09.230"], {}, 3, 36, 9, 230, None],
        [["29.97", "00:00:00;01"], {}, 0, 0, 0, 1, "00:00:00;01"],
        [["29.97", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["29.97", "03:36:09;23"], {}, 3, 36, 9, 23, None],
        [["30", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["25", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["59.94", "03:36:09;23"], {}, 3, 36, 9, 23, None],
        [["60", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["59.94", "03:36:09;23"], {}, 3, 36, 9, 23, None],
        [["72", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["96", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["100", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["120", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["119.88", "03:36:09;23"], {}, 3, 36, 9, 23, None],
        [["23.98", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["24", "03:36:09:23"], {}, 3, 36, 9, 23, None],
        [["ms", "03:36:09.230"], {}, 3, 36, 9, 230, None],
        [["24"], {"frames": 12000}, 0, 8, 19, 23, "00:08:19:23"],
    ],
)
def test_timecode_properties_test(args, kwargs, hrs, mins, secs, frs, str_repr):
    """Test hrs, mins, secs and frs properties."""
    tc = Timecode(*args, **kwargs)
    assert hrs == tc.hrs
    assert mins == tc.mins
    assert secs == tc.secs
    assert frs == tc.frs
    if str_repr is not None:
        assert str_repr == tc.__str__()


@pytest.mark.parametrize(
    "args,kwargs,frames, str_repr, tc_next",
    [
        [["29.97", "00:00:00;00"], {}, 1, None, None],
        [["29.97", "00:00:00;21"], {}, 22, None, None],
        [["29.97", "00:00:00;29"], {}, 30, None, None],
        [["29.97", "00:00:00;60"], {}, 61, None, None],
        [["29.97", "00:00:01;00"], {}, 31, None, None],
        [["29.97", "00:00:10;00"], {}, 301, None, None],
        [["29.97", "00:01:00;00"], {}, 1799, "00:00:59;28", None],
        [["29.97", "23:59:59;29"], {}, 2589408, None, None],
        [
            ["29.97", "01:00:00;00"],
            {"force_non_drop_frame": True},
            None,
            "01:00:00:00",
            None,
        ],
        [
            ["29.97", "01:00:00:00"],
            {"force_non_drop_frame": True},
            None,
            "01:00:00:00",
            None,
        ],
        [["29.97", "13:36:59;29"], {}, None, None, "13:37:00;02"],
        [["59.94", "13:36:59;59"], {}, None, "13:36:59;59", None],
        [["59.94", "13:36:59;59"], {}, None, None, "13:37:00;04"],
        [["59.94", "13:39:59;59"], {}, None, None, "13:40:00;00"],
        [["29.97", "13:39:59;29"], {}, None, None, "13:40:00;00"],
        [["89.91", "00:00:00;00"], {}, 1, None, None],
        [["89.91", "00:00:00;89"], {}, 90, None, None],
        [["89.91", "00:00:01;00"], {}, 91, None, None],
        [["89.91", "00:01:00;00"], {}, 5395, "00:00:59;84", None],
        [["89.91", "13:36:59;89"], {}, None, None, "13:37:00;06"],
        [["89.91", "13:39:59;89"], {}, None, None, "13:40:00;00"],
        [["119.88", "00:00:00;00"], {}, 1, None, None],
        [["119.88", "00:00:00;119"], {}, 120, None, None],
        [["119.88", "00:00:01;00"], {}, 121, None, None],
        [["119.88", "00:01:00;00"], {}, 7193, "00:00:59;112", None],
        [["119.88", "23:59:59;119"], {}, 10357632, None, None],
        [
            ["119.88", "01:00:00;00"],
            {"force_non_drop_frame": True},
            None,
            "01:00:00:00",
            None,
        ],
        [
            ["119.88", "01:00:00:00"],
            {"force_non_drop_frame": True},
            None,
            "01:00:00:00",
            None,
        ],
        [["119.88", "13:36:59;119"], {}, None, None, "13:37:00;08"],
        [["119.88", "13:39:59;119"], {}, None, None, "13:40:00;00"],
    ],
)
def test_ntsc_drop_frame_conversion(args, kwargs, frames, str_repr, tc_next):
    """Test timecode to frame conversion for NTSC drop frame rates (29.97, 59.94, 119.88)."""
    tc = Timecode(*args, **kwargs)
    if frames is not None:
        assert frames == tc._frames
    if str_repr is not None:
        assert str_repr == tc.__str__()
    if tc_next is not None:
        assert tc_next == tc.next().__str__()


@pytest.mark.parametrize("framerate", ["29.97", "59.94", "89.91", "119.88"])
def test_setting_ntsc_frame_rate_forces_drop_frame(framerate):
    """Setting NTSC drop frame rates forces the dropframe to True."""
    tc = Timecode(framerate)
    assert tc.drop_frame


def test_setting_framerate_to_ms_enables_ms_frame():
    """Setting the frame rate to ms forces the ms_frame to True."""
    tc = Timecode("ms")
    assert tc.ms_frame


def test_setting_framerate_to_1000_enables_ms_frame():
    """Setting the frame rate to 1000 forces the ms_frame to True."""
    tc = Timecode("1000")
    assert tc.ms_frame


def test_framerate_argument_is_frames():
    """Setting the framerate arg to 'frames' will set the integer frame rate to 1."""
    tc = Timecode("frames")
    assert tc._int_framerate == 1


@pytest.mark.parametrize(
    "args,kwargs,str_repr,next_range,last_tc_str_repr,frames",
    [
        [["29.97", "03:36:09;23"], {}, "03:36:09;23", 60, "03:36:11;23", 388764],
        [["30", "03:36:09:23"], {}, "03:36:09;23", 60, "03:36:11:23", 389154],
        [["25", "03:36:09:23"], {}, "03:36:09;23", 60, "03:36:12:08", 324309],
        [["59.94", "03:36:09;23"], {}, "03:36:09;23", 60, "03:36:10;23", 777444],
        [["60", "03:36:09:23"], {}, "03:36:09:23", 60, "03:36:10:23", 778224],
        [["59.94", "03:36:09:23"], {}, "03:36:09;23", 60, "03:36:10:23", 777444],
        [["72", "03:36:09:23"], {}, "03:36:09:23", 120, "03:36:10:71", 933912],
        [["96", "03:36:09:23"], {}, "03:36:09:23", 120, "03:36:10:47", 1245168],
        [["100", "03:36:09:23"], {}, "03:36:09:23", 120, "03:36:10:43", 1297044],
        [["120", "03:36:09:23"], {}, "03:36:09:23", 120, "03:36:10:23", 1556424],
        [["119.88", "03:36:09;23"], {}, "03:36:09;23", 120, "03:36:10;23", 1554864],
        [["23.98", "03:36:09:23"], {}, "03:36:09:23", 60, "03:36:12:11", 311340],
        [["24", "03:36:09:23"], {}, "03:36:09:23", 60, "03:36:12:11", 311340],
        [["ms", "03:36:09.230"], {}, "03:36:09.230", 60, "03:36:09.290", 12969291],
        [["24"], {"frames": 12000}, "00:08:19:23", 60, "00:08:22:11", 12060],
    ],
)
def test_iteration(args, kwargs, str_repr, next_range, last_tc_str_repr, frames):
    """Test iteration."""
    tc = Timecode(*args, **kwargs)
    assert tc == str_repr

    last_tc = None
    for x in range(next_range):
        last_tc = tc.next()
        assert last_tc is not None

    assert last_tc_str_repr == last_tc
    assert frames == tc._frames


@pytest.mark.parametrize(
    "args1,kwargs1,args2,kwargs2,custom_offset1,custom_offset2,str_repr1,str_repr2,frames1, frames2",
    [
        [
            ["29.97", "03:36:09;23"],
            {},
            ["29.97", "00:00:29;23"],
            {},
            894,
            894,
            "03:36:39;17",
            "03:36:39;17",
            389598,
            389598,
        ],
        [
            ["30", "03:36:09:23"],
            {},
            ["30", "00:00:29:23"],
            {},
            894,
            894,
            "03:36:39:17",
            "03:36:39:17",
            389988,
            389988,
        ],
        [
            ["25", "03:36:09:23"],
            {},
            ["25", "00:00:29:23"],
            {},
            749,
            749,
            "03:36:39:22",
            "03:36:39:22",
            324998,
            324998,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "03:36:38;47",
            "03:36:38;47",
            779148,
            779148,
        ],
        [
            ["60", "03:36:09:23"],
            {},
            ["60", "00:00:29:23"],
            {},
            1764,
            1764,
            "03:36:38:47",
            "03:36:38:47",
            779928,
            779928,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "03:36:38;47",
            "03:36:38;47",
            779148,
            779148,
        ],
        [
            ["72", "03:36:09:23"],
            {},
            ["72", "00:00:29:23"],
            {},
            2112,
            2112,
            "03:36:38:47",
            "03:36:38:47",
            935904,
            935904,
        ],
        [
            ["96", "03:36:09:23"],
            {},
            ["96", "00:00:29:23"],
            {},
            2808,
            2808,
            "03:36:38:47",
            "03:36:38:47",
            1247856,
            1247856,
        ],
        [
            ["100", "03:36:09:23"],
            {},
            ["100", "00:00:29:23"],
            {},
            2924,
            2924,
            "03:36:38:47",
            "03:36:38:47",
            1299848,
            1299848,
        ],
        [
            ["120", "03:36:09:23"],
            {},
            ["120", "00:00:29:23"],
            {},
            3504,
            3504,
            "03:36:38:47",
            "03:36:38:47",
            1559808,
            1559808,
        ],
        [
            ["119.88", "03:36:09;23"],
            {},
            ["119.88", "00:00:29;23"],
            {},
            3504,
            3504,
            "03:36:38;47",
            "03:36:38;47",
            1558248,
            1558248,
        ],
        [
            ["23.98", "03:36:09:23"],
            {},
            ["23.98", "00:00:29:23"],
            {},
            720,
            720,
            "03:36:39:23",
            "03:36:39:23",
            312000,
            312000,
        ],
        [
            ["ms", "03:36:09.230"],
            {},
            ["ms", "01:06:09.230"],
            {},
            3969231,
            720,
            "04:42:18.461",
            "03:36:09.950",
            16938462,
            12969951,
        ],
        [
            ["24"],
            {"frames": 12000},
            ["24"],
            {"frames": 485},
            485,
            719,
            "00:08:40:04",
            "00:08:49:22",
            12485,
            12719,
        ],
        [
            ["59.94", "04:20:13;21"],
            {},
            ["59.94", "23:59:59;59"],
            {},
            5178816,
            0,
            "04:20:13;21",
            "04:20:13;21",
            6114682,
            935866,
        ],
    ],
)
def test_op_overloads_add(
    args1,
    kwargs1,
    args2,
    kwargs2,
    custom_offset1,
    custom_offset2,
    str_repr1,
    str_repr2,
    frames1,
    frames2,
):
    """Test + operator overload."""
    tc = Timecode(*args1, **kwargs1)
    tc2 = Timecode(*args2, **kwargs2)
    assert custom_offset1 == tc2._frames
    d = tc + tc2
    f = tc + custom_offset2
    assert str_repr1 == d.__str__()
    assert frames1 == d._frames
    assert str_repr2 == f.__str__()
    assert frames2 == f._frames


@pytest.mark.parametrize(
    "args1,kwargs1,args2,kwargs2,custom_offset1,custom_offset2,str_repr1,str_repr2,frames1, frames2",
    [
        [
            ["29.97", "03:36:09;23"],
            {},
            ["29.97", "00:00:29;23"],
            {},
            894,
            894,
            "03:35:39;27",
            "03:35:39;27",
            387810,
            387810,
        ],
        [
            ["30", "03:36:09:23"],
            {},
            ["30", "00:00:29:23"],
            {},
            894,
            894,
            "03:35:39:29",
            "03:35:39:29",
            388200,
            388200,
        ],
        [
            ["25", "03:36:09:23"],
            {},
            ["25", "00:00:29:23"],
            {},
            749,
            749,
            "03:35:39:24",
            "03:35:39:24",
            323500,
            323500,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "03:35:39;55",
            "03:35:39;55",
            775620,
            775620,
        ],
        [
            ["60", "03:36:09:23"],
            {},
            ["60", "00:00:29:23"],
            {},
            1764,
            1764,
            "03:35:39:59",
            "03:35:39:59",
            776400,
            776400,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "03:35:39;55",
            "03:35:39;55",
            775620,
            775620,
        ],
        [
            ["72", "03:36:09:23"],
            {},
            ["72", "00:00:29:23"],
            {},
            2112,
            2112,
            "03:35:39:71",
            "03:35:39:71",
            931680,
            931680,
        ],
        [
            ["96", "03:36:09:23"],
            {},
            ["96", "00:00:29:23"],
            {},
            2808,
            2808,
            "03:35:39:95",
            "03:35:39:95",
            1242240,
            1242240,
        ],
        [
            ["100", "03:36:09:23"],
            {},
            ["100", "00:00:29:23"],
            {},
            2924,
            2924,
            "03:35:39:99",
            "03:35:39:99",
            1294000,
            1294000,
        ],
        [
            ["120", "03:36:09:23"],
            {},
            ["120", "00:00:29:23"],
            {},
            3504,
            3504,
            "03:35:39:119",
            "03:35:39:119",
            1552800,
            1552800,
        ],
        [
            ["119.88", "03:36:09;23"],
            {},
            ["119.88", "00:00:29;23"],
            {},
            3504,
            3504,
            "03:35:39;111",
            "03:35:39;111",
            1551240,
            1551240,
        ],
        [
            ["23.98", "03:36:09:23"],
            {},
            ["23.98", "00:00:29:23"],
            {},
            720,
            720,
            "03:35:39:23",
            "03:35:39:23",
            310560,
            310560,
        ],
        [
            ["23.98", "03:36:09:23"],
            {},
            ["23.98", "00:00:29:23"],
            {},
            720,
            720,
            "03:35:39:23",
            "03:35:39:23",
            310560,
            310560,
        ],
        [
            ["ms", "03:36:09.230"],
            {},
            ["ms", "01:06:09.230"],
            {},
            3969231,
            3969231,
            "02:29:59.999",
            "02:29:59.999",
            9000000,
            9000000,
        ],
        [
            ["24"],
            {"frames": 12000},
            ["24"],
            {"frames": 485},
            485,
            485,
            "00:07:59:18",
            "00:07:59:18",
            11515,
            11515,
        ],
    ],
)
def test_op_overloads_subtract(
    args1,
    kwargs1,
    args2,
    kwargs2,
    custom_offset1,
    custom_offset2,
    str_repr1,
    str_repr2,
    frames1,
    frames2,
):
    """Test - operator overload."""
    tc = Timecode(*args1, **kwargs1)
    tc2 = Timecode(*args2, **kwargs2)
    assert custom_offset1 == tc2._frames
    d = tc - tc2
    f = tc - custom_offset2
    assert str_repr1 == d.__str__()
    assert str_repr2 == f.__str__()
    assert frames1 == d._frames
    assert frames2 == f._frames


@pytest.mark.parametrize(
    "args1,kwargs1,args2,kwargs2,custom_offset1,custom_offset2,str_repr1,str_repr2,frames1, frames2",
    [
        [
            ["29.97", "00:00:09;23"],
            {},
            ["29.97", "00:00:29;23"],
            {},
            894,
            4,
            "02:26:09;29",
            "00:00:39;05",
            262836,
            1176,
        ],
        [
            ["30", "03:36:09:23"],
            {},
            ["30", "00:00:29:23"],
            {},
            894,
            894,
            "04:50:01:05",
            "04:50:01:05",
            347850036,
            347850036,
        ],
        [
            ["25", "03:36:09:23"],
            {},
            ["25", "00:00:29:23"],
            {},
            749,
            749,
            "10:28:20:00",
            "10:28:20:00",
            242862501,
            242862501,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "18:59:27;35",
            "18:59:27;35",
            1371305376,
            1371305376,
        ],
        [
            ["60", "03:36:09:23"],
            {},
            ["60", "00:00:29:23"],
            {},
            1764,
            1764,
            "19:00:21:35",
            "19:00:21:35",
            1372681296,
            1372681296,
        ],
        [
            ["59.94", "03:36:09;23"],
            {},
            ["59.94", "00:00:29;23"],
            {},
            1764,
            1764,
            "18:59:27;35",
            "18:59:27;35",
            1371305376,
            1371305376,
        ],
        [
            ["72", "03:36:09:23"],
            {},
            ["72", "00:00:29:23"],
            {},
            2112,
            2112,
            "00:40:31:71",
            "00:40:31:71",
            1972168704,
            1972168704,
        ],
        [
            ["96", "03:36:09:23"],
            {},
            ["96", "00:00:29:23"],
            {},
            2808,
            2808,
            "12:00:53:95",
            "12:00:53:95",
            3496094784,
            3496094784,
        ],
        [
            ["100", "03:36:09:23"],
            {},
            ["100", "00:00:29:23"],
            {},
            2924,
            2924,
            "21:54:17:75",
            "21:54:17:75",
            3792205776,
            3792205776,
        ],
        [
            ["120", "03:36:09:23"],
            {},
            ["120", "00:00:29:23"],
            {},
            3504,
            3504,
            "23:21:16:95",
            "23:21:16:95",
            5453289216,
            5453289216,
        ],
        [
            ["119.88", "03:36:09;23"],
            {},
            ["119.88", "00:00:29;23"],
            {},
            3504,
            3504,
            "23:19:28;95",
            "23:19:28;95",
            5447822976,
            5447822976,
        ],
        [
            ["ms", "03:36:09.230"],
            {},
            ["ms", "01:06:09.230"],
            {},
            3969231,
            3969231,
            "17:22:11.360",
            "17:22:11.360",
            51477873731361,
            51477873731361,
        ],
        [
            ["24"],
            {"frames": 12000},
            ["24"],
            {"frames": 485},
            485,
            485,
            "19:21:39:23",
            "19:21:39:23",
            5820000,
            5820000,
        ],
    ],
)
def test_op_overloads_mult(
    args1,
    kwargs1,
    args2,
    kwargs2,
    custom_offset1,
    custom_offset2,
    str_repr1,
    str_repr2,
    frames1,
    frames2,
):
    """Test * operator overload."""
    tc = Timecode(*args1, **kwargs1)
    tc2 = Timecode(*args2, **kwargs2)
    assert custom_offset1 == tc2._frames
    d = tc * tc2
    f = tc * custom_offset2
    assert str_repr1 == d.__str__()
    assert str_repr2 == f.__str__()
    assert frames1 == d._frames
    assert frames2 == f._frames


def test_op_overloads_mult_1():
    """Two Timecode multiplied, the framerate of the result is the same of left side."""
    tc1 = Timecode("23.98", "03:36:09:23")
    tc2 = Timecode("23.98", "00:00:29:23")
    tc3 = tc1 * tc2
    assert tc3.framerate == Fraction(24000, 1001)


def test_op_overloads_mult_2():
    """Two Timecode multiplied, the framerate of the result is the same of left side."""
    tc1 = Timecode("23.98", "03:36:09:23")
    assert tc1._frames == 311280
    tc2 = Timecode("23.98", "00:00:29:23")
    assert tc2._frames == 720
    tc3 = tc1 * tc2
    assert 224121600 == tc3._frames
    assert "01:59:59:23" == tc3.__str__()


def test_op_overloads_mult_3():
    """Timecode multiplied with integer."""
    tc1 = Timecode("23.98", "03:36:09:23")
    tc4 = tc1 * 720
    assert 224121600 == tc4._frames
    assert "01:59:59:23" == tc4.__str__()


def test_add_with_two_different_frame_rates():
    """Added TCs with different framerate, result framerate is same with left side."""
    tc1 = Timecode("29.97", "00:00:00;00")
    tc2 = Timecode("24", "00:00:00:10")
    tc3 = tc1 + tc2
    assert Fraction(30000, 1001) == tc3.framerate
    assert 12 == tc3._frames
    assert tc3 == "00:00:00;11"


@pytest.mark.parametrize(
    "args,kwargs,func,tc2",
    [
        [["24", "00:00:01:00"], {}, lambda x, y: x + y, "not suitable"],
        [["24", "00:00:01:00"], {}, lambda x, y: x - y, "not suitable"],
        [["24", "00:00:01:00"], {}, lambda x, y: x * y, "not suitable"],
        [["24", "00:00:01:00"], {}, lambda x, y: x / y, "not suitable"],
        [["24", "00:00:01:00"], {}, lambda x, y: x / y, 32.4],
    ],
)
def test_arithmetic_with_unsupported_type_raises_error(args, kwargs, func, tc2):
    """TimecodeError is raised if the other class is not suitable for the operation."""
    tc1 = Timecode(*args, **kwargs)
    with pytest.raises(TimecodeError) as cm:
        _ = func(tc1, tc2)

    assert str(cm.value) == "Type {} not supported for arithmetic.".format(
        tc2.__class__.__name__
    )


def test_div_method_working_properly_1():
    """__div__ method is working properly."""
    tc1 = Timecode("24", frames=100)
    tc2 = Timecode("24", frames=10)
    tc3 = tc1 / tc2
    assert tc3.frames == 10
    assert tc3 == "00:00:00:09"


def test_div_method_working_properly_2():
    """__div__ method is working properly."""
    tc1 = Timecode("24", "00:00:10:00")
    tc2 = tc1 / 10
    assert tc2 == "00:00:00:23"


@pytest.mark.parametrize(
    "args,frames,frame_number",
    [
        [["24", "00:00:00:00"], 1, 0],
        [["24", "00:00:01:00"], 25, 24],
        [["29.97", "00:01:00;00"], 1799, 1798],
        [["30", "00:01:00:00"], 1801, 1800],
        [["50", "00:01:00:00"], 3001, 3000],
        [["59.94", "00:01:00;00"], 3597, 3596],
        [["60", "00:01:00:00"], 3601, 3600],
        [["72", "00:01:00:00"], 4321, 4320],
        [["89.91", "00:01:00;00"], 5395, 5394],
        [["96", "00:01:00:00"], 5761, 5760],
        [["100", "00:01:00:00"], 6001, 6000],
        [["120", "00:01:00:00"], 7201, 7200],
        [["119.88", "00:01:00;00"], 7193, 7192],
    ],
)
def test_frame_number_attribute_value_is_correctly_calculated(
    args, frames, frame_number
):
    """Timecode.frame_number attribute is correctly calculated."""
    tc1 = Timecode(*args)
    assert frames == tc1._frames
    assert frame_number == tc1.frame_number


def test_24_hour_limit_in_24fps():
    """timecode will loop back to 00:00:00:00 after 24 hours in 24 fps."""
    tc1 = Timecode("24", "00:00:00:21")
    tc2 = Timecode("24", "23:59:59:23")
    assert "00:00:00:21" == (tc1 + tc2).__str__()
    assert "02:00:00:00" == (tc2 + 159840001).__str__()


def test_24_hour_limit_in_2997fps():
    """timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "00:00:00;21")
    assert tc1.drop_frame
    assert 22 == tc1._frames

    tc2 = Timecode("29.97", "23:59:59;29")
    assert tc2.drop_frame
    assert 2589408 == tc2._frames

    assert "00:00:00;21" == str(tc1)
    assert "23:59:59;29" == str(tc2)

    assert "00:00:00;21" == (tc1 + tc2).__str__()
    assert "02:00:00;00" == (tc2 + 215785).__str__()
    assert "02:00:00;00" == (tc2 + 215785 + 2589408).__str__()
    assert "02:00:00;00" == (tc2 + 215785 + 2589408 + 2589408).__str__()


def test_24_hour_limit_1():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("59.94", "23:59:59;29")
    assert 5178786 == tc1._frames


def test_24_hour_limit_2():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "23:59:59;29")
    assert 2589408 == tc1._frames


def test_24_hour_limit_3():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", frames=2589408)
    assert "23:59:59;29" == tc1.__str__()


def test_24_hour_limit_4():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "23:59:59;29")
    tc2 = tc1 + 1
    assert "00:00:00;00" == tc2.__str__()


def test_24_hour_limit_5():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "23:59:59;29")
    tc2 = tc1 + 21
    assert "00:00:00;20" == tc2.__str__()


def test_24_hour_limit_6():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "00:00:00;21")
    tc2 = Timecode("29.97", "23:59:59;29")
    tc3 = tc1 + tc2
    assert "00:00:00;21" == tc3.__str__()


def test_24_hour_limit_7():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "04:20:13;21")
    assert 467944 == tc1._frames
    assert "04:20:13;21" == tc1.__str__()


def test_24_hour_limit_8():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", frames=467944)
    assert 467944 == tc1._frames
    assert "04:20:13;21" == tc1.__str__()


def test_24_hour_limit_9():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", "23:59:59;29")
    assert 2589408 == tc1._frames
    assert "23:59:59;29" == tc1.__str__()


def test_24_hour_limit_10():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", frames=2589408)
    assert 2589408 == tc1._frames
    assert "23:59:59;29" == tc1.__str__()


def test_24_hour_limit_11():
    """Timecode will loop back to 00:00:00:00 after 24 hours in 29.97 fps."""
    tc1 = Timecode("29.97", frames=467944)
    tc2 = Timecode("29.97", "23:59:59;29")
    tc3 = tc1 + tc2
    assert "04:20:13;21" == tc3.__str__()


def test_framerate_can_be_changed():
    """Timecode is automatically updated if the framerate attribute is changed."""
    tc1 = Timecode("25", frames=100)
    assert "00:00:03:24" == tc1.__str__()
    assert 100 == tc1._frames

    tc1.framerate = "12"
    assert "00:00:08:03" == tc1.__str__()
    assert 100 == tc1._frames


@pytest.mark.parametrize(
    "args,kwargs,frame_rate,int_framerate",
    [
        [["24000/1000", "00:00:00:00"], {}, "24", 24],
        [["24000/1001", "00:00:00;00"], {}, "23.98", 24],
        [["30000/1000", "00:00:00:00"], {}, "30", 30],
        [["30000/1001", "00:00:00;00"], {}, "29.97", 30],
        [["60000/1000", "00:00:00:00"], {}, "60", 60],
        [["60000/1001", "00:00:00;00"], {}, "59.94", 60],
        [[(60000, 1001), "00:00:00;00"], {}, "59.94", 60],
        [["72000/1000", "00:00:00:00"], {}, "72", 72],
        [[(72000, 1000), "00:00:00:00"], {}, "72", 72],
        [["96000/1000", "00:00:00:00"], {}, "96", 96],
        [[(96000, 1000), "00:00:00:00"], {}, "96", 96],
        [["100000/1000", "00:00:00:00"], {}, "100", 100],
        [[(100000, 1000), "00:00:00:00"], {}, "100", 100],
        [["120000/1000", "00:00:00:00"], {}, "120", 120],
        [["120000/1001", "00:00:00;00"], {}, "119.88", 120],
        [[(120000, 1000), "00:00:00:00"], {}, "120", 120],
        [[(120000, 1001), "00:00:00;00"], {}, "119.88", 120],
    ],
)
def test_rational_framerate_conversion(args, kwargs, frame_rate, int_framerate):
    """Fractional framerate conversion."""
    tc = Timecode(*args, **kwargs)
    assert abs(float(frame_rate) - tc.framerate) < 5e-3
    assert int_framerate == tc._int_framerate


def test_rational_frame_delimiter_1():
    tc = Timecode("24000/1000", frames=1)
    assert ";" not in tc.__str__()


def test_rational_frame_delimiter_2():
    tc = Timecode("24000/1001", frames=1)
    assert ";" not in tc.__str__()


def test_rational_frame_delimiter_3():
    tc = Timecode("30000/1001", frames=1)
    assert ";" in tc.__str__()


def test_ms_vs_fraction_frames_1():
    tc1 = Timecode("ms", "00:00:00.040")
    assert tc1.ms_frame
    assert not tc1.fraction_frame


def test_ms_vs_fraction_frames_2():
    tc2 = Timecode(24, "00:00:00.042")
    assert tc2.fraction_frame
    assert not tc2.ms_frame


def test_ms_vs_fraction_frames_3():
    tc1 = Timecode("ms", "00:00:00.040")
    tc2 = Timecode(24, "00:00:00.042")
    assert tc1 != tc2


def test_ms_vs_fraction_frames_4():
    tc1 = Timecode("ms", "00:00:00.040")
    tc2 = Timecode(24, "00:00:00.042")
    assert tc1.frame_number == 40
    assert tc2.frame_number == 1


def test_toggle_fractional_frame_1():
    tc = Timecode(24, 421729315)
    assert tc.__str__() == "19:23:14:23"


def test_toggle_fractional_frame_2():
    tc = Timecode(24, 421729315)
    tc.set_fractional(True)
    assert tc.__str__() == "19:23:14.958"


def test_toggle_fractional_frame_3():
    tc = Timecode(24, 421729315)
    tc.set_fractional(False)
    assert tc.__str__() == "19:23:14:23"


def test_timestamp_realtime_1():
    frames = 12345
    ts = frames * 1 / 24
    realtime = float(Timecode(24, frames=frames).to_realtime())
    assert abs(realtime - ts) < 1e-09


def test_timestamp_realtime_2():
    tc = Timecode(50, start_seconds=1 / 50)
    assert str(tc.to_realtime()) == "00:00:00.020"


def test_timestamp_realtime_3():
    # SMPTE 12-1 §5.2.2:
    # - "When DF compensation is applied to NTSC TC, the deviation after one hour is approximately –3.6 ms"
    tc = Timecode(29.97, "00:59:59;29")
    assert str(tc.to_realtime()) == str((Timecode(1000, "00:59:59.999") - int(round(3.6))).to_realtime())

    # - "[...] The deviation accumulated over a 24-hour period is approximately –2.6 frames (–86 ms)"
    tc = Timecode(59.94, "23:59:59;59")
    assert str(tc.to_realtime()) == str((Timecode(1000, "23:59:59.999") - 86).to_realtime())


def test_timestamp_realtime_4():
    # SMPTE 12-1 §5.2.2
    # - "Monotonically counting at int_framerate will yield a deviation of approx. +3.6 s in one hour of elapsed time."
    tc = Timecode(59.94, "00:59:59:59", force_non_drop_frame=True)
    assert str(tc.to_realtime()) == str((Timecode(1000, "00:59:59.999") + 3600).to_realtime())


def test_timestamp_systemtime_1():
    """
    TC with integer framerate always have system time equal to elapsed time.
    """
    tc50 = Timecode(50, "00:59:59:49")
    tc24 = Timecode(24, "00:59:59:23")
    tcms = Timecode(1000, "00:59:59.999")
    assert str(tc50.to_systemtime()) == "01:00:00.000"
    assert str(tc24.to_systemtime()) == "01:00:00.000"
    assert str(tcms.to_systemtime()) == "01:00:00.000"


def test_timestamp_systemtime_2():
    """
    TC with NTSC framerate always have system time different to realtime.
    """
    tc = Timecode(23.98, "00:59:59:23")
    assert str(tc.to_systemtime()) == "01:00:00.000"
    assert tc.to_systemtime() != tc.to_realtime()


def test_timestamp_systemtime_3():
    """
    TC with DF NTSC framerate have system time roughly equal to real time.
    with a -3.6 ms drift per hour (SMPTE 12-1 §5.2.2).
    """
    tc = Timecode(29.97, "23:59:59;29")
    assert str(tc.to_systemtime()) == "24:00:00.000"
    # Check if we have the expected drift at 24h
    assert abs(float(tc.to_systemtime()) - float(tc.to_realtime()) - 24 * 3600e-6) < 1e-6


def test_add_const_dropframe_flag():
    tc1 = Timecode(29.97, "00:00:00:00", force_non_drop_frame=True)
    assert (tc1 + 1).drop_frame is False


def test_add_tc_dropframe_flag():
    tc1 = Timecode(29.97, "00:00:00:00", force_non_drop_frame=True)
    tc2 = Timecode(29.97, "00:00:00;00")

    # Left operand drop_frame flag is preserved
    assert (tc1 + tc2).drop_frame is False
    assert (tc2 + tc1).drop_frame is True


def test_ge_overload():
    tc1 = Timecode(24, "00:00:00:00")
    tc2 = Timecode(24, "00:00:00:00")
    tc3 = Timecode(24, "00:00:00:01")
    tc4 = Timecode(24, "00:00:01.100")
    tc5 = Timecode(24, "00:00:01.200")

    assert tc1 == tc2
    assert tc1 >= tc2
    assert tc3 >= tc2
    assert (tc2 >= tc3) is False
    assert tc4 <= tc5


def test_gt_overload_a():
    tc1 = Timecode(24, "00:00:00:00")
    tc2 = Timecode(24, "00:00:00:00")
    tc3 = Timecode(24, "00:00:00:01")
    tc4 = Timecode(24, "00:00:01.100")
    tc5 = Timecode(24, "00:00:01.200")

    assert not (tc1 > tc2)
    assert not (tc2 > tc2)
    assert tc3 > tc2
    assert tc5 > tc4


def test_le_overload():
    tc1 = Timecode(24, "00:00:00:00")
    tc2 = Timecode(24, "00:00:00:00")
    tc3 = Timecode(24, "00:00:00:01")
    tc4 = Timecode(24, "00:00:01.100")
    tc5 = Timecode(24, "00:00:01.200")

    assert tc1 == tc2
    assert tc1 <= tc2
    assert tc2 <= tc3
    assert not (tc2 >= tc3)
    assert tc5 >= tc4
    assert tc5 > tc4


def test_lt_overload():
    tc1 = Timecode(24, "00:00:00:00")
    tc2 = Timecode(24, "00:00:00:00")
    tc3 = Timecode(24, "00:00:00:01")
    tc4 = Timecode(24, "00:00:01.100")
    tc5 = Timecode(24, "00:00:01.200")

    assert not (tc1 < tc2)
    assert not (tc2 < tc2)
    assert tc2 < tc3
    assert tc4 < tc5


def test_parse_timecode_with_int():
    """parse_timecode method with int input."""
    result = Timecode.parse_timecode(16663)
    assert result == (0, 0, 41, 17)  # issue #16


def test_frames_argument_is_not_an_int():
    """TypeError is raised if the frames argument is not an integer."""
    with pytest.raises(TypeError) as cm:
        Timecode("30", frames=0.1223)

    assert (
        "Timecode.frames should be a positive integer bigger than zero, not a float"
        == str(cm.value)
    )


def test_frames_argument_is_zero():
    """ValueError is raised if the frames argument is given as 0."""
    with pytest.raises(ValueError) as cm:
        Timecode("30", frames=0)

    assert (
        "Timecode.frames should be a positive integer bigger than zero, not 0"
        == str(cm.value)
    )


def test_bug_report_30():
    """bug report 30

    The claim on the bug report was to get ``00:34:45:09`` from a Timecode with 23.976
    as the frame rate (supplied with Python 3's Fraction library) and 50000 as the total
    number of frames. The support for Fraction instances were missing, and it has been
    added. But the claim for the resultant Timecode was wrong, the resultant Timecode
    should have been ``00:34:43:07`` and that has been confirmed by DaVinci Resolve.
    """
    from fractions import Fraction

    framerate = Fraction(24000, 1001)  # 23.976023976023978
    frame_idx = 50000

    tc1 = Timecode(framerate, frames=frame_idx)
    assert "00:34:43:07" == tc1.__str__()


def test_bug_report_31_part1():
    """bug report 31
    https://github.com/eoyilmaz/timecode/issues/31
    """
    timecode1 = "01:00:10:00"
    timecode2 = "01:00:10:00"
    a = Timecode("25", timecode1)
    b = Timecode("25", timecode2)

    with pytest.raises(ValueError) as cm:
        _ = a - b

    assert (
        str(cm.value)
        == "Timecode.frames should be a positive integer bigger than zero, not 0"
    )


def test_bug_report_31_part2():
    """bug report 31
    https://github.com/eoyilmaz/timecode/issues/31
    """
    timecode1 = "01:00:08:00"
    timecode2 = "01:00:10:00"
    timecode3 = "01:01:00:00"
    a = Timecode("25", timecode1)
    b = Timecode("25", timecode2)
    offset = a - b
    _ = Timecode("25", timecode3) + offset


def test_bug_report_32():
    """bug report 32
    https://github.com/eoyilmaz/timecode/issues/32
    """
    framerate = "30000/1001"
    seconds = 500
    tc1 = Timecode(framerate, start_seconds=seconds)
    assert abs(tc1.float - seconds) < 1e-09


def test_set_timecode_method():
    """set_timecode method is working properly."""
    tc1 = Timecode("24")
    assert tc1.frames == 1
    assert tc1 == "00:00:00:00"

    tc2 = Timecode("29.97", frames=1000)
    assert tc2.frames == 1000

    tc1.set_timecode(tc2.__str__())  # this is interpreted as 24
    assert tc1.frames == 802

    tc1.set_timecode(tc2)  # this should be interpreted as 29.97 and 1000 frames
    assert tc1.frames == 1000


def test_iter_method():
    """__iter__ method"""
    tc = Timecode("24", "01:00:00:00")
    for a in tc:
        assert a == tc


def test_back_method_returns_a_timecode_instance():
    """back method returns a Timecode instance."""
    tc = Timecode("24", "01:00:00:00")
    assert isinstance(tc.back(), Timecode)


def test_back_method_returns_the_instance_itself():
    """back method returns the Timecode instance itself."""
    tc = Timecode("24", "01:00:00:00")
    assert tc.back() is tc


def test_back_method_reduces_frames_by_one():
    """back method reduces the ``Timecode.frames`` by one."""
    tc = Timecode("24", "01:00:00:00")
    frames = tc.frames
    assert tc.back().frames == (frames - 1)


def test_mult_frames_method_is_working_properly():
    """mult_frames method is working properly."""
    tc = Timecode("24")
    tc.mult_frames(10)
    assert tc.frames == 10
    assert tc.__str__() == "00:00:00:09"


def test_div_frames_method_is_working_properly():
    """div_frames method is working properly."""
    tc = Timecode("24", "00:00:00:09")
    assert tc.frames == 10
    tc.div_frames(10)
    assert tc.frames == 1
    assert tc.__str__() == "00:00:00:00"


def test_eq_method_with_integers():
    """Comparing the Timecode with integers are working properly."""
    tc = Timecode("24", "00:00:10:00")
    assert tc == 241


def test_ge_method_with_strings():
    """__ge__ method with strings."""
    tc = Timecode("24", "00:00:10:00")
    assert tc >= "00:00:09:00"
    assert tc >= "00:00:10:00"


def test_ge_method_with_integers():
    """__ge__ method with integers."""
    tc = Timecode("24", "00:00:10:00")
    assert tc >= 230
    assert tc >= 241


def test_gt_method_with_strings():
    """__gt__ method with strings."""
    tc = Timecode("24", "00:00:10:00")
    assert tc > "00:00:09:00"


def test_gt_method_with_integers():
    """__gt__ method with integers."""
    tc = Timecode("24", "00:00:10:00")
    assert tc > 230


def test_le_method_with_strings():
    """__le__ method with strings."""
    tc = Timecode("24", "00:00:10:00")
    assert tc <= "00:00:11:00"
    assert tc <= "00:00:10:00"


def test_le_method_with_integers():
    """__le__ method with integers."""
    tc = Timecode("24", "00:00:10:00")
    assert tc <= 250
    assert tc <= 241


def test_lt_method_with_strings():
    """__lt__ method with strings."""
    tc = Timecode("24", "00:00:10:00")
    assert tc < "00:00:11:00"


def test_lt_method_with_integers():
    """__lt__ method with integers."""
    tc = Timecode("24", "00:00:10:00")
    assert tc < 250


def test_fraction_lib_from_python3_raises_import_error_for_python2():
    """ImportError is raised and the error is handled gracefully under Python 2 if
    importing the Fraction library which is introduced in Python 3.

    This is purely done for increasing the code coverage to 100% under Python 3.
    """
    try:
        import mock
    except ImportError:
        from unittest import mock
    import sys

    with mock.patch.dict(sys.modules, {"fractions": None}):
        # the coverage should be now 100%
        _ = Timecode("24")


def test_rollover_for_23_98():
    """bug report #33."""
    tc = Timecode("23.98", "23:58:47:00")
    assert 2071849 == tc.frames
    tc.add_frames(24)
    assert 2071873 == tc.frames
    assert "23:58:48:00" == tc.__str__()


@pytest.mark.parametrize(
    "framerate",
    ["23.976", "23.98", "24", "25", "29.97", "30", "50", "59.94", "60", "ms"],
)
def test_float_representation_roundtrip(framerate):
    """Test float representation of Timecode."""
    mismatched = 0
    # Close enough to max frame across our supported framerates.
    num_frames = Timecode(framerate, "24:00:00;00").frame_number
    max_samples = 50_000

    if num_frames <= max_samples:
        frames_to_test = range(1, num_frames)
    else:
        # Not the most efficient sample allocation, but our range is pretty small.
        random.seed(42)  # Fixed seed for repeatability
        frames_to_test = sorted(random.sample(range(1, num_frames), max_samples))

    for i in frames_to_test:
        tc = Timecode(framerate, frames=i)
        from_float = Timecode(framerate, start_seconds=tc.float)
        if tc != from_float:
            mismatched += 1

    tested = len(frames_to_test)
    assert mismatched == 0, (
        f"{mismatched}/{tested} ({mismatched / tested * 100:.1f}%) incorrect "
        f"(sampled {tested} of {num_frames} total frames)"
    )


@pytest.mark.parametrize(
    "args,kwargs,str_repr",
    [
        [["29.97"], {"frames": 2589408}, "23:59:59;29"],
        [["29.97"], {"frames": 2589409}, "00:00:00;00"],
        [["29.97"], {"frames": 2589409, "force_non_drop_frame": True}, "23:58:33:18"],
        [["29.97"], {"frames": 2592001, "force_non_drop_frame": True}, "00:00:00:00"],
        [["59.94"], {"frames": 5178816}, "23:59:59;59"],
        [["59.94"], {"frames": 5178817}, "00:00:00;00"],
        [["59.94"], {"frames": 5184000, "force_non_drop_frame": True}, "23:59:59:59"],
        [["59.94"], {"frames": 5184001, "force_non_drop_frame": True}, "00:00:00:00"],
        [["72"], {"frames": 6220800}, "23:59:59:71"],
        [["72"], {"frames": 6220801}, "00:00:00:00"],
        [["89.91"], {"frames": 7768224}, "23:59:59;89"],
        [["89.91"], {"frames": 7768225}, "00:00:00;00"],
        [["96"], {"frames": 8294400}, "23:59:59:95"],
        [["96"], {"frames": 8294401}, "00:00:00:00"],
        [["100"], {"frames": 8640000}, "23:59:59:99"],
        [["100"], {"frames": 8640001}, "00:00:00:00"],
        [["120"], {"frames": 10368000}, "23:59:59:119"],
        [["120"], {"frames": 10368001}, "00:00:00:00"],
        [["119.88"], {"frames": 10357632}, "23:59:59;119"],
        [["119.88"], {"frames": 10357633}, "00:00:00;00"],
    ],
)
def test_rollover(args, kwargs, str_repr):
    tc = Timecode(*args, **kwargs)
    assert str_repr == tc.__str__()


@pytest.mark.parametrize(
    "framerate,int_framerate,is_drop,one_minute_frames,expected_tc",
    [
        # Non-drop NTSC rates (multiples of 24000/1001)
        ["47.952", 48, False, 2881, "00:01:00:00"],  # 2 * 23.976 fps - HFR broadcast
        ["71.928", 72, False, 4321, "00:01:00:00"],  # 3 * 23.976 fps
        ["95.904", 96, False, 5761, "00:01:00:00"],  # 4 * 23.976 fps
        # Drop frame NTSC rate (multiple of 30000/1001)
        # For drop frame, test at 10-minute mark where frames aren't skipped
        ["89.91", 90, True, 53947, "00:10:00;00"],  # 3 * 29.97 fps - with drop frame
    ],
)
def test_generalized_ntsc_rates(
    framerate, int_framerate, is_drop, one_minute_frames, expected_tc
):
    """Test generalized NTSC detection for HFR rates.

    Tests automatic NTSC detection for rates based on multiples of 24000/1001 or 30000/1001.
    Drop frame should only apply to multiples of 30000/1001 (i.e., int_framerate % 30 == 0).
    """
    # Test basic creation and NTSC detection
    separator = ";" if is_drop else ":"
    tc = Timecode(framerate, f"00:00:00{separator}00")
    assert tc._is_ntsc_rate is True
    assert tc._int_framerate == int_framerate
    assert tc.drop_frame is is_drop
    assert abs(tc.framerate - float(framerate)) < 5e-3

    # Test frame counting - one second should be int_framerate + 1
    tc2 = Timecode(framerate, f"00:00:01{separator}00")
    assert tc2.frames == int_framerate + 1

    # Test frame count displays correctly
    tc3 = Timecode(framerate, frames=one_minute_frames)
    assert str(tc3) == expected_tc


@pytest.mark.parametrize(
    "rational_str,int_framerate,is_drop",
    [
        ["48000/1001", 48, False],  # 47.952 fps
        ["72000/1001", 72, False],  # 71.928 fps
        ["90000/1001", 90, True],  # 89.91 fps - drop frame
        ["96000/1001", 96, False],  # 95.904 fps
    ],
)
def test_generalized_ntsc_rational_formats(rational_str, int_framerate, is_drop):
    """Test that rational format fractions work for new NTSC rates."""
    separator = ";" if is_drop else ":"
    tc = Timecode(rational_str, f"00:00:00{separator}00")
    assert tc._is_ntsc_rate is True
    assert tc._int_framerate == int_framerate
    assert tc.drop_frame is is_drop
    
def test_repr_parse():
    #force NDF to verify there is no mangling even with a DF framerate
    tc = Timecode('30000/1001', '12:34:56:21', force_non_drop_frame=True)
    tc_eval = eval(repr(tc))

    assert tc.frames == tc_eval.frames
    assert tc.framerate == tc_eval.framerate

def test_reference_time():
    framerate = Fraction(120000, 1001)
    #start_seconds is in the system timebase, so use int_fps
    tc1 = Timecode(framerate, start_seconds=1/120)
    tc2 = Timecode(framerate, start_seconds=0, reference_time_on_display=True)
    assert tc1 == tc2

def test_reference_time_frame_offset():
    framerate = Fraction(120000, 1001)
    #start_seconds is in the system timebase, so use int_fps
    tc1 = Timecode(framerate, start_seconds=600)
    tc2 = Timecode(framerate, start_seconds=600, reference_time_on_display=True)
    assert (tc1 + 1) == tc2

def test_reference_real_system_time_value():
    framerate = Fraction(48000, 1001)
    tc = Timecode(framerate, frames=1, reference_time_on_display=True)
    assert tc.frames == 1
    assert tc._is_ntsc_rate is True # needed for this test
    
    # Time reference on system starting to draw the first frame.
    # only time where both are equal.
    assert float(tc.to_realtime()) == 0.0
    assert float(tc.to_systemtime()) == 0.0
    
    tc.reference_time_on_display = False
    # No longer true, NTSC is slower than wall-clock
    assert 0 < tc.to_systemtime() < tc.to_realtime()
