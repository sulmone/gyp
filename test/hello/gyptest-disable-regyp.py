#!/usr/bin/env python

"""
Verifies that Makefiles don't get rebuilt when a source gyp file changes and
the disable_regeneration generator flag is set.
"""

import TestGyp

test = TestGyp.TestGyp()

test.run_gyp('hello.gyp', '-Gauto_regeneration=0')

test.build_all('hello.gyp')

test.run_built_executable('hello', stdout="Hello, world!\n")

# Sleep so that the changed gyp file will have a newer timestamp than the
# previously generated build files.
test.sleep()
test.write('hello.gyp', test.read('hello2.gyp'))

test.build_all('hello.gyp')

# Should still be the old executable, as regeneration was disabled.
test.run_built_executable('hello', stdout="Hello, world!\n")

test.pass_test()
