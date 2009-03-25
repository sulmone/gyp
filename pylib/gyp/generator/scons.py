#!/usr/bin/python


import gyp
import gyp.common
# TODO(sgk):  create a separate "project module" for SCons?
#import gyp.SCons as SCons
import os
import pprint
import re


generator_default_variables = {
    'EXECUTABLE_PREFIX': '',
    'EXECUTABLE_SUFFIX': '',
    'INTERMEDIATE_DIR': '$OBJ_DIR/$COMPONENT_NAME/$TARGET_NAME/intermediate',
    'SHARED_INTERMEDIATE_DIR': '$OBJ_DIR/global_intermediate',
    'OS': 'linux',
    'PRODUCT_DIR': '$DESTINATION_ROOT',
    'RULE_INPUT_ROOT': '${SOURCE.filebase}',
    'RULE_INPUT_EXT': '${SOURCE.suffix}',
    'RULE_INPUT_NAME': '${SOURCE.file}',
    'RULE_INPUT_PATH': '${SOURCE}',
}


header = """\
# This file is generated; do not edit.
"""


def WriteList(fp, list, prefix='',
                        separator=',\n    ',
                        preamble=None,
                        postamble=None):
  fp.write(preamble or '')
  fp.write((separator or ' ').join([prefix + l for l in list]))
  fp.write(postamble or '')


def full_product_name(spec, prefix='', suffix=''):
  name = spec.get('product_name') or spec['target_name']
  name = prefix + name + suffix
  product_dir = spec.get('product_dir')
  if product_dir:
    name = os.path.join(product_dir, name)
  return name


def _SCons_null_writer(fp, spec):
  pass

def _SCons_writer(fp, spec, builder):
  fp.write('\n_outputs = %s\n' % builder)
  fp.write('target_files.extend(_outputs)\n')

def _SCons_program_writer(fp, spec):
  name = full_product_name(spec)
  builder = 'env.ChromeProgram(\'%s\', input_files)' % name
  return _SCons_writer(fp, spec, builder)

def _SCons_static_library_writer(fp, spec):
  name = full_product_name(spec)
  builder = 'env.ChromeStaticLibrary(\'%s\', input_files)' % name
  return _SCons_writer(fp, spec, builder)

def _SCons_shared_library_writer(fp, spec):
  name = full_product_name(spec)
  builder = 'env.ChromeSharedLibrary(\'%s\', input_files)' % name
  return _SCons_writer(fp, spec, builder)

def _SCons_loadable_module_writer(fp, spec):
  name = full_product_name(spec)
  builder = 'env.ChromeLoadableModule(\'%s\', input_files)' % name
  return _SCons_writer(fp, spec, builder)

SConsTypeWriter = {
  None : _SCons_null_writer,
  'none' : _SCons_null_writer,
  'executable' : _SCons_program_writer,
  'static_library' : _SCons_static_library_writer,
  'shared_library' : _SCons_shared_library_writer,
  'loadable_module' : _SCons_loadable_module_writer,
}

_command_template = """
if GetOption('verbose'):
  _action = Action([%(action)s])
else:
  _action = Action([%(action)s], %(message)s)
_outputs = env.Command(
  %(outputs)s,
  %(inputs)s,
  _action
)
"""

_rule_template = """
%(name)s_additional_inputs = %(inputs)s
%(name)s_outputs = %(outputs)s
def %(name)s_emitter(target, source, env):
  return (%(name)s_outputs, source + %(name)s_additional_inputs)
if GetOption('verbose'):
  %(name)s_action = Action([%(action)s])
else:
  %(name)s_action = Action([%(action)s], %(message)s)
env['BUILDERS']['%(name)s'] = Builder(action=%(name)s_action, emitter=%(name)s_emitter)
%(name)s_files = [f for f in input_files if str(f).endswith('.%(extension)s')]
for %(name)s_file in %(name)s_files:
  _outputs = env.%(name)s(%(name)s_file)
"""

escape_quotes_re = re.compile('^([^=]*=)"([^"]*)"$')
def escape_quotes(s):
    return escape_quotes_re.sub('\\1\\"\\2\\"', s)

def GenerateConfig(fp, spec, config, indent=''):
  """
  Generates SCons dictionary items for a gyp configuration.

  This provides the main translation between the (lower-case) gyp settings
  keywords and the (upper-case) SCons construction variables.
  """
  var_mapping = {
      'asflags' : 'ASFLAGS',
      'cflags' : 'CCFLAGS',
      'defines' : 'CPPDEFINES',
      'include_dirs' : 'CPPPATH',
      'linkflags' : 'LINKFLAGS',
  }
  postamble='\n%s],\n' % indent
  for gyp_var, scons_var in var_mapping.iteritems():
      value = config.get(gyp_var)
      if value:
        if gyp_var in ('defines',):
          value = [escape_quotes(v) for v in value]
        WriteList(fp,
                  map(repr, value),
                  prefix=indent,
                  preamble='%s%s = [\n    ' % (indent, scons_var),
                  postamble=postamble)

  libraries = spec.get('libraries')
  if libraries:
    WriteList(fp,
                map(repr, libraries),
                prefix=indent,
                preamble='%sLIBS = [\n    ' % indent,
                postamble=postamble)


def GenerateSConscript(output_filename, spec, build_file):
  """
  Generates a SConscript file for a specific target.

  This generates a SConscript file suitable for building any or all of
  the target's configurations.

  A SConscript file may be called multiple times to generate targets for
  multiple configurations.  Consequently, it needs to be ready to build
  the target for any requested configuration, and therefore contains
  information about the settings for all configurations (generated into
  the SConscript file at gyp configuration time) as well as logic for
  selecting (at SCons build time) the specific configuration being built.

  The general outline of a generated SConscript file is:
 
    --  Header

    --  Import 'env'.  This contains a $CONFIG_NAME construction
        variable that specifies what configuration to build
        (e.g. Debug, Release).

    --  Configurations.  This is a dictionary with settings for
        the different configurations (Debug, Release) under which this
        target can be built.  The values in the dictionary are themselves
        dictionaries specifying what construction variables should added
        to the local copy of the imported construction environment
        (Append), should be removed (FilterOut), and should outright
        replace the imported values (Replace).

    --  Clone the imported construction environment and update
        with the proper configuration settings.

    --  Initialize the lists of the targets' input files and prerequisites.

    --  Target-specific actions and rules.  These come after the
        input file and prerequisite initializations because the
        outputs of the actions and rules may affect the input file
        list (process_outputs_as_sources) and get added to the list of
        prerequisites (so that they're guaranteed to be executed before
        building the target).

    --  Call the Builder for the target itself.

    --  Arrange for any copies to be made into installation directories.

    --  Set up the gyp_target_{name} Alias (phony Node) for the target
        as the primary handle for building all of the target's pieces.

    --  Use env.Require() to make sure the prerequisites (explicitly
        specified, but also including the actions and rules) are built
        before the target itself.

    --  Return the gyp_target_{name} Alias to the calling SConstruct
        file so it can be added to the list of default targets.
  """
  gyp_dir = os.path.split(output_filename)[0]
  if not gyp_dir:
      gyp_dir = '.'
  gyp_dir = os.path.abspath(gyp_dir)
  component_name = os.path.splitext(os.path.basename(build_file))[0]
  target_name = spec['target_name']

  fp = open(output_filename, 'w')
  fp.write(header)

  fp.write('\nImport("env")\n')

  #
  fp.write('\n')
  fp.write('configurations = {\n')
  for config_name, config in spec['configurations'].iteritems():
    fp.write('    \'%s\' : {\n' % config_name)

    fp.write('        \'Append\' : dict(\n')
    GenerateConfig(fp, spec, config, ' '*12)
    fp.write('        ),\n')

    fp.write('        \'FilterOut\' : dict(\n' )
    for key, var in config.get('scons_remove', {}).iteritems():
      fp.write('             %s = %s,\n' % (key, repr(var)))
    fp.write('        ),\n')

    fp.write('        \'Replace\' : dict(\n' )
    scons_settings = config.get('scons_settings', {})
    for key in sorted(scons_settings.keys()):
      val = pprint.pformat(scons_settings[key])
      fp.write('             %s = %s,\n' % (key, val))
    if 'c++' in spec.get('link_languages', []):
      fp.write('             %s = %s,\n' % ('LINK', repr('$CXX')))
    fp.write('        ),\n')

    fp.write('    },\n')
  fp.write('}\n')

  #
  fp.write('\n')
  fp.write('env = env.Clone(COMPONENT_NAME=%s,\n' % repr(component_name))
  fp.write('                TARGET_NAME=%s)\n' % repr(target_name))
  fp.write('\n')
  fp.write('config = configurations[env[\'CONFIG_NAME\']]\n')
  fp.write('env.Append(**config[\'Append\'])\n')
  fp.write('env.FilterOut(**config[\'FilterOut\'])\n')
  fp.write('env.Replace(**config[\'Replace\'])\n')

  #
  sources = spec.get('sources')
  if sources:
    pre = '\ninput_files = ChromeFileList([\n    '
    WriteList(fp, map(repr, sources), preamble=pre, postamble=',\n])\n')
  else:
    fp.write('\ninput_files = []\n')

  fp.write('\n')
  fp.write('target_files = []\n')
  prerequisites = spec.get('scons_prerequisites', [])
  fp.write('prerequisites = %s\n' % pprint.pformat(prerequisites))

  actions = spec.get('actions', [])
  for action in actions:
    a = ['cd', gyp_dir, '&&'] + action['action']
    message = action.get('message')
    if message:
        message = repr(message)
    fp.write(_command_template % {
                 'inputs' : pprint.pformat(action.get('inputs', [])),
                 'outputs' : pprint.pformat(action.get('outputs', [])),
                 'action' : pprint.pformat(a),
                 'message' : message,
             })
    if action.get('process_outputs_as_sources'):
      fp.write('input_files.extend(_outputs)\n')
    fp.write('prerequisites.extend(_outputs)\n')

  rules = spec.get('rules', [])
  for rule in rules:
    name = rule['rule_name']
    a = ['cd', gyp_dir, '&&'] + rule['action']
    message = rule.get('message')
    if message:
        message = repr(message)
    fp.write(_rule_template % {
                 'inputs' : pprint.pformat(rule.get('inputs', [])),
                 'outputs' : pprint.pformat(rule.get('outputs', [])),
                 'action' : pprint.pformat(a),
                 'extension' : rule['extension'],
                 'name' : name,
                 'message' : message,
             })
    if rule.get('process_outputs_as_sources'):
      fp.write('  input_files.Replace(%s_file, _outputs)\n' % name)
    fp.write('prerequisites.extend(_outputs)\n')

  SConsTypeWriter[spec.get('type')](fp, spec)

  copies = spec.get('copies', [])
  for copy in copies:
    destdir = copy['destination']
    files = copy['files']
    fmt = '\n_outputs = env.Install(%s,\n    %s\n)\n'
    fp.write(fmt % (repr(destdir), pprint.pformat(files)))
    fp.write('prerequisites.extend(_outputs)\n')

  fmt = "\ngyp_target = env.Alias('gyp_target_%s', target_files)\n"
  fp.write(fmt % target_name)
  dependencies = spec.get('scons_dependencies', [])
  if dependencies:
    WriteList(fp, dependencies, preamble='env.Requires(gyp_target, [\n    ',
                                postamble='\n])\n')
  fp.write('env.Requires(gyp_target, prerequisites)\n')
  fp.write('Return("gyp_target")\n')

  fp.close()


_wrapper_template = """\

__doc__ = '''
Wrapper configuration for building this entire "solution,"
including all the specific targets in various *.scons files.
'''

import sys

# Support PROGRESS= to show progress in different ways.
if sys.platform == 'win32':
  console = 'con'
else:
  console = '/dev/tty'
p = ARGUMENTS.get('PROGRESS')
if p == 'spinner':
  Progress(['/\\r', '|\\r', '\\\\\\r', '-\\r'],
           interval=5,
           file=open(console, 'w'))
elif p == 'name':
  Progress('$TARGET\\r', overwrite=True, file=open(console, 'w'))

# Set the default -j value based on the number of processors.
if sys.platform in ('win32', 'cygwin'):
  cpus = int(os.environ.get('NUMBER_OF_PROCESSORS', 1))
elif sys.platform in ('linux', 'linux2', 'posix'):
  # TODO(evanm): this is Linux-specific, not posix.
  # Parse /proc/cpuinfo for processor count.
  cpus = len([l for l in open('/proc/cpuinfo')
                      if l.startswith('processor\\t')])
else:
  cpus = 1
SetOption('num_jobs', cpus + 1)

# Since we set the -j value by default, suppress SCons warnings about being
# unable to support parallel build on versions of Python with no threading.
default_warnings = ['no-no-parallel-support']
SetOption('warn', default_warnings + GetOption('warn'))

# TODO(sgk):  We'd like to use --conf= to select the configuration to
# build, but SCons already supports a --config option and by the time we
# get here optparse has already decided that --conf is a synonym for
# --config.  So spell out all of --configuration.
AddOption('--configuration', nargs=1, dest='conf_list', default=[],
          action='append', help='Configuration to build.')

#
AddOption('--verbose', dest='verbose', default=False,
          action='store_true', help='Verbose command-line output.')


sconscript_files = %(sconscript_files)s

target_alias_list= []

conf_list = GetOption('conf_list')
if not conf_list:
    conf_list = ['Debug']

srcdir = GetOption('repository')
if srcdir:
  # Deep SCons magick to support --srcdir={chromium_component}:
  # By specifying --srcdir=, a connection has already been set up
  # between our current directory (the build directory) and the
  # component source directory (base/, net/, webkit/, etc.).
  # The Chromium build is really rooted at src/, so we need to
  # repoint the repository connection to that directory.  To
  # do so and have everything just work, we must wipe out the
  # existing connection by hand, including its cached value.
  target_dir = Dir('#')
  target_dir.clear()
  target_dir.repositories = [target_dir.dir]

for conf in conf_list:
  if srcdir:
    destination_root = '$MAIN_DIR'
  else:
    destination_root = '$MAIN_DIR/$CONFIG_NAME'
  env = Environment(
      tools = ['ar', 'as', 'gcc', 'g++', 'gnulink', 'chromium_builders'],
      _GYP='_gyp',
      CHROME_SRC_DIR='$MAIN_DIR/..',
      CONFIG_NAME=conf,
      DESTINATION_ROOT=destination_root,
      MAIN_DIR=Dir('#').abspath,
      OBJ_DIR='$DESTINATION_ROOT/obj',
      TARGET_PLATFORM='LINUX',
  )
  if not GetOption('verbose'):
    env.SetDefault(
        ARCOMSTR='Creating library $TARGET',
        ASCOMSTR='Assembling $TARGET',
        CCCOMSTR='Compiling $TARGET',
        CONCATSOURCECOMSTR='ConcatSource $TARGET',
        CXXCOMSTR='Compiling $TARGET',
        LDMODULECOMSTR='Building loadable module $TARGET',
        LINKCOMSTR='Linking $TARGET',
        MANIFESTCOMSTR='Updating manifest for $TARGET',
        MIDLCOMSTR='Compiling IDL $TARGET',
        PCHCOMSTR='Precompiling $TARGET',
        RANLIBCOMSTR='Indexing $TARGET',
        RCCOMSTR='Compiling resource $TARGET',
        SHCCCOMSTR='Compiling $TARGET',
        SHCXXCOMSTR='Compiling $TARGET',
        SHLINKCOMSTR='Linking $TARGET',
        SHMANIFESTCOMSTR='Updating manifest for $TARGET',
    )
  SConsignFile(env.File('$DESTINATION_ROOT/.sconsign').abspath)

  if not srcdir:
    env.Dir('$OBJ_DIR').addRepository(env.Dir('$CHROME_SRC_DIR'))

  for sconscript in sconscript_files:
    target_alias = env.SConscript('$OBJ_DIR/%(subdir)s/' + sconscript,
                                  exports=['env'])
    if target_alias:
      target_alias_list.extend(target_alias)

Default(Alias('%(name)s', target_alias_list))
"""

def GenerateSConscriptWrapper(name, output_filename, sconscript_files):
  """
  Generates the "wrapper" SConscript file (analogous to the Visual Studio
  solution) that calls all the individual target SConscript files.
  """
  subdir = os.path.basename(os.path.split(output_filename)[0])
  fp = open(output_filename, 'w')
  fp.write(header)
  fp.write(_wrapper_template % {
               'name' : name,
               'sconscript_files' : pprint.pformat(sconscript_files),
               'subdir' : subdir,
           })
  fp.close()


def TargetFilename(target, build_file=None, output_suffix=''):
  """Returns the .scons file name for the specified target.
  """
  if build_file is None:
    build_file, target = gyp.common.BuildFileAndTarget('', target)[:2]
  output_file = os.path.join(os.path.split(build_file)[0],
                             target + output_suffix + '.scons')
  return output_file


def GenerateOutput(target_list, target_dicts, data, params):
  options = params['options']
  """
  Generates all the output files for the specified targets.
  """
  for build_file, build_file_dict in data.iteritems():
    if not build_file.endswith('.gyp'):
      continue

  for qualified_target in target_list:
    spec = target_dicts[qualified_target]

    if spec['type'] == 'settings':
      continue

    build_file, target = gyp.common.BuildFileAndTarget('', qualified_target)[:2]
    output_file = TargetFilename(target, build_file, options.suffix)

    if not spec.has_key('libraries'):
      spec['libraries'] = []

    # Add dependent static library targets to the 'libraries' value.
    deps = spec.get('dependencies', [])
    spec['scons_dependencies'] = []
    for d in deps:
      td = target_dicts[d]
      target_name = td['target_name']
      spec['scons_dependencies'].append("Alias('gyp_target_%s')" % target_name)
      if td['type'] in ('static_library', 'shared_library'):
        libname = td.get('product_name', target_name)
        spec['libraries'].append(libname)
      if td['type'] == 'loadable_module':
        prereqs = spec.get('scons_prerequisites', [])
        # TODO:  parameterize with <(SHARED_LIBRARY_*) variables?
        name = full_product_name(td, '${SHLIBPREFIX}', '${SHLIBSUFFIX}')
        prereqs.append(name)
        spec['scons_prerequisites'] = prereqs

    GenerateSConscript(output_file, spec, build_file)

  for build_file in sorted(data.keys()):
    path, ext = os.path.splitext(build_file)
    if ext != '.gyp':
      continue
    output_dir, basename = os.path.split(path)
    output_filename  = path + '_main' + options.suffix + '.scons'

    all_targets = gyp.common.AllTargets(target_list, target_dicts, build_file)
    sconscript_files = []
    for t in all_targets:
      if target_dicts[t]['type'] == 'settings':
        continue
      target_filename = TargetFilename(t, output_suffix=options.suffix)
      t = gyp.common.RelativePath(target_filename, output_dir)
      sconscript_files.append(t)
    sconscript_files.sort()

    if sconscript_files:
      GenerateSConscriptWrapper(basename, output_filename, sconscript_files)
