
from nibetaseries.cli.run import get_parser


def test_get_parser():
    try:
        get_parser().parse_args(['-h'])
    except SystemExit:
        print('success')
