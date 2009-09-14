#!/usr/bin/env python

"""
Verifies simple actions when using the default build target.
"""

import sys

import TestGyp

test = TestGyp.TestGyp()

test.run_gyp('actions.gyp', chdir='src')

test.relocate('src', 'relocate/src')

test.build_default('actions.gyp', chdir='relocate/src')

expect = """\
Hello from program.c
Hello from make-prog1.py
Hello from make-prog2.py
"""

if sys.platform in ('darwin',):
  chdir = 'relocate/src/subdir1'
else:
  chdir = 'relocate/src'
test.run_built_executable('program', chdir=chdir, stdout=expect)

test.must_match('relocate/src/subdir2/file.out', "Hello from make-file.py\n")

test.pass_test()
