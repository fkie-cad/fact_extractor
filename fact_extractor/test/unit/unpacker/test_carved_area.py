import pytest

from unpacker.helper.carving import Area, CarvingArea


@pytest.mark.parametrize(
    ('start', 'end', 'expected'),
    [
        # complete area
        (0, 100, []),
        (-1, 101, []),
        (-1, 100, []),
        (0, 101, []),
        # borders
        (0, 99, [Area(99, 100)]),
        (1, 100, [Area(0, 1)]),
        (-1, 99, [Area(99, 100)]),
        (1, 101, [Area(0, 1)]),
        # in between
        (50, 60, [Area(0, 50), Area(60, 100)]),
    ],
)
def test_add_carved_area(start, end, expected):
    carved_area = CarvingArea(100)
    carved_area.add_carved_area(Area(start, end))
    assert carved_area.uncarved_areas == expected


def test_bug():
    area_size = 8258048
    carved_area = CarvingArea(area_size)

    carved_area.add_carved_area(Area(0, 512))

    carved_area.add_carved_area(Area(15440, 15504))
    carved_area.add_carved_area(Area(15504, 48257))

    carved_area.add_carved_area(Area(131584, 132096))
    carved_area.add_carved_area(Area(132096, 1066830))

    carved_area.add_carved_area(Area(1180160, 8258048))

    expected = [Area(512, 15440), Area(48257, 131584), Area(1066830, 1180160)]
    assert len(carved_area.uncarved_areas) == len(expected)

    for area in expected:
        assert area in carved_area.uncarved_areas

    assert str(carved_area) == '(512:15440) (48257:131584) (1066830:1180160)'
