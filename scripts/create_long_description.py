#!/usr/bin/env python

import re
import io
from os.path import join, abspath


def read(*names, **kwargs):
    return io.open(
        join(abspath(*names)),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


long_description = '%s\n%s' % (
    re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub(
        '',
        re.sub(r":ref:`(.*)`", r"\1", read('README.rst'))),
    re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    )

ld_rst = 'long_description.rst'
with open(ld_rst, 'w') as out_file:
    out_file.write(long_description)
