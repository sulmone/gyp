#!/usr/bin/python

import copy
import gyp.input
import optparse
import os.path
import re
import shlex
import sys

# Default debug modes for GYP
debug = {}

# List of "official" debug modes, but you can use anything you like.
DEBUG_GENERAL = 'general'
DEBUG_VARIABLES = 'variables'

def DebugOutput(mode, message):
  if mode in gyp.debug.keys():
    print "%s: %s" % (mode.upper(), message)

def FindBuildFiles():
  extension = '.gyp'
  files = os.listdir(os.getcwd())
  build_files = []
  for file in files:
    if file[-len(extension):] == extension:
      build_files.append(file)
  return build_files


def Load(build_files, format, default_variables={},
         includes=[], depth='.', params={}):
  """
  Loads one or more specified build files.
  default_variables and includes will be copied before use.
  Returns the generator for the specified format and the
  data returned by loading the specified build files.
  """
  default_variables = copy.copy(default_variables)

  # Default variables provided by this program and its modules should be
  # named WITH_CAPITAL_LETTERS to provide a distinct "best practice" namespace,
  # avoiding collisions with user and automatic variables.
  default_variables['GENERATOR'] = format

  generator_name = 'gyp.generator.' + format
  # These parameters are passed in order (as opposed to by key)
  # because ActivePython cannot handle key parameters to __import__.
  generator = __import__(generator_name, globals(), locals(), generator_name)
  default_variables.update(generator.generator_default_variables)

  # Give the generator the opportunity to set additional variables based on
  # the params it will receive in the output phase.
  if getattr(generator, 'CalculateVariables', None):
    generator.CalculateVariables(default_variables, params)

  # Fetch the generator specific info that gets fed to input, we use getattr
  # so we can default things and the generators only have to provide what
  # they need.
  generator_input_info = {
    'generator_wants_absolute_build_file_paths':
        getattr(generator, 'generator_wants_absolute_build_file_paths', False),
    'generator_handles_variants':
        getattr(generator, 'generator_handles_variants', False),
    'non_configuration_keys':
        getattr(generator, 'generator_additional_non_configuration_keys', []),
    'path_sections':
        getattr(generator, 'generator_additional_path_sections', []),
    'extra_sources_for_rules':
        getattr(generator, 'generator_extra_sources_for_rules', []),
  }

  # Process the input specific to this generator.
  result = gyp.input.Load(build_files, default_variables, includes[:],
                          depth, generator_input_info)
  return [generator] + result

def NameValueListToDict(name_value_list):
  """
  Takes an array of strings of the form 'NAME=VALUE' and creates a dictionary
  of the pairs.  If a string is simply NAME, then the value in the dictionary
  is set to True.  If VALUE can be converted to an integer, it is.
  """
  result = { }
  for item in name_value_list:
    tokens = item.split('=', 1)
    if len(tokens) == 2:
      # If we can make it an int, use that, otherwise, use the string.
      try:
        token_value = int(tokens[1])
      except ValueError:
        token_value = tokens[1]
      # Set the variable to the supplied value.
      result[tokens[0]] = token_value
    else:
      # No value supplied, treat it as a boolean and set it.
      result[tokens[0]] = True
  return result

def ShlexEnv(env_name):
  flags = os.environ.get(env_name, [])
  if flags:
    flags = shlex.split(flags)
  return flags

def RegenerateAppendFlag(flag, values, predicate, env_name, options):
  """Regenerate a list of command line flags, for an option of action='append'.

  The |env_name|, if given, is checked in the environment and used to generate
  an initial list of options, then the options that were specified on the
  command line (given in |values|) are appended.  This matches the handling of
  environment variables and command line flags where command line flags override
  the environment, while not requiring the environment to be set when the flags
  are used again.
  """
  flags = []
  if options.use_environment and env_name:
    for flag_value in ShlexEnv(env_name):
      flags.append(flag + predicate(flag_value))
  if values:
    for flag_value in values:
      flags.append(flag + predicate(flag_value))
  return flags

def RegenerateFlags(options):
  """Given a parsed options object, and taking the environment variables into
  account, returns a list of flags that should regenerate an equivalent options
  object (even in the absence of the environment variables.)

  Any path options will be normalized relative to depth.

  The format flag is not included, as it is assumed the calling generator will
  set that as appropriate.
  """
  def FixPath(path):
    path = gyp.common.FixIfRelativePath(path, options.depth)
    if not path:
      return os.path.curdir
    return path

  def Noop(value):
    return value

  # We always want to ignore the environment when regenerating, to avoid
  # duplicate or changed flags in the environment at the time of regeneration.
  flags = ['--ignore-environment']
  for name, metadata in options._regeneration_metadata.iteritems():
    opt = metadata['opt']
    value = getattr(options, name)
    value_predicate = metadata['type'] == 'path' and FixPath or Noop
    action = metadata['action']
    env_name = metadata['env_name']
    if action == 'append':
      flags.extend(RegenerateAppendFlag(opt, value, value_predicate,
                                        env_name, options))
    elif action in ('store', None):  # None is a synonym for 'store'.
      if value:
        flags.append(opt + value_predicate(value))
      elif options.use_environment and env_name and os.environ.get(env_name):
        flags.append(opt + value_predicate(os.environ.get(env_name)))
    else:
      print >>sys.stderr, ("regeneration unimplemented for action", action,
                           "flag", opt)

  return flags

class RegeneratableOptionParser(optparse.OptionParser):
  def __init__(self):
    self.__regeneratable_options = {}
    optparse.OptionParser.__init__(self)

  def add_option(self, *args, **kw):
    """Add an option to the parser.

    This accepts the same arguments as OptionParser.add_option, plus the
    following:
      regenerate: can be set to False to prevent this option from being included
                  in regeneration.
      env_name: name of environment variable that additional values for this
                option come from.
      type: adds type='path', to tell the regenerator that the values of
            this option need to be made relative to options.depth
    """
    env_name = kw.pop('env_name', None),
    if 'dest' in kw and kw.pop('regenerate', True):
      dest = kw['dest']

      # The path type is needed for regenerating, for optparse we can just treat
      # it as a string.
      type = kw.get('type')
      if type == 'path':
        kw['type'] = 'string'

      if args[0].startswith('--'):
        opt = args[0] + '='
      else:
        opt = args[0]
      self.__regeneratable_options[dest] = {
          'action': kw.get('action'),
          'type': type,
          'env_name': env_name,
          'opt': opt,
        }

    optparse.OptionParser.add_option(self, *args, **kw)

  def parse_args(self, *args):
    values, args = optparse.OptionParser.parse_args(self, *args)
    values._regeneration_metadata = self.__regeneratable_options
    return values, args

def main(args):
  my_name = os.path.basename(sys.argv[0])

  parser = RegeneratableOptionParser()
  usage = 'usage: %s [options ...] [build_file ...]'
  parser.set_usage(usage.replace('%s', '%prog'))
  parser.add_option('-D', dest='defines', action='append', metavar='VAR=VAL',
                    env_name='GYP_DEFINES',
                    help='sets variable VAR to value VAL')
  parser.add_option('-f', '--format', dest='formats', action='append',
                    env_name='GYP_GENERATORS', regenerate=False,
                    help='output formats to generate')
  parser.add_option('--msvs-version', dest='msvs_version',
                    regenerate=False,
                    help='Deprecated; use -G msvs_version=MSVS_VERSION instead')
  parser.add_option('-I', '--include', dest='includes', action='append',
                    metavar='INCLUDE', type='path',
                    help='files to include in all loaded .gyp files')
  parser.add_option('--depth', dest='depth', metavar='PATH', type='path',
                    help='set DEPTH gyp variable to a relative path to PATH')
  parser.add_option('-d', '--debug', dest='debug', metavar='DEBUGMODE',
                    action='append', default=[], help='turn on a debugging '
                    'mode for debugging GYP.  Supported modes are "variables" '
                    'and "general"')
  parser.add_option('-S', '--suffix', dest='suffix', default='',
                    help='suffix to add to generated files')
  parser.add_option('-G', dest='generator_flags', action='append', default=[],
                    metavar='FLAG=VAL', env_name='GYP_GENERATOR_FLAGS',
                    help='sets generator flag FLAG to VAL')
  parser.add_option('--generator-output', dest='generator_output',
                    action='store', default=None, metavar='DIR', type='path',
                    env_name='GYP_GENERATOR_OUTPUT',
                    help='puts generated build files under DIR')
  parser.add_option('--ignore-environment', dest='use_environment',
                    action='store_false', default=True, regenerate=False,
                    help='do not read options from environment variables')

  # We read a few things from ~/.gyp, so set up a var for that.
  home_vars = ['HOME']
  if sys.platform in ('cygwin', 'win32'):
    home_vars.append('USERPROFILE')
  home = None
  for home_var in home_vars:
    home = os.getenv(home_var)
    if home != None:
      break
  home_dot_gyp = None
  if home != None:
    home_dot_gyp = os.path.join(home, '.gyp')
    if not os.path.exists(home_dot_gyp):
      home_dot_gyp = None

  # TODO(thomasvl): add support for ~/.gyp/defaults

  (options, build_files_arg) = parser.parse_args(args)
  build_files = build_files_arg

  if not options.formats:
    # If no format was given on the command line, then check the env variable.
    generate_formats = []
    if options.use_environment:
      generate_formats = os.environ.get('GYP_GENERATORS', [])
    if generate_formats:
      generate_formats = re.split('[\s,]', generate_formats)
    if generate_formats:
      options.formats = generate_formats
    else:
      # Nothing in the variable, default based on platform.
      options.formats = [ {'darwin':   'xcode',
                           'win32':    'msvs',
                           'cygwin':   'msvs',
                           'freebsd7': 'make',
                           'freebsd8': 'make',
                           'linux2':   'scons',}[sys.platform] ]

  if not options.generator_output and options.use_environment:
    g_o = os.environ.get('GYP_GENERATOR_OUTPUT')
    if g_o:
      options.generator_output = g_o

  for mode in options.debug:
    gyp.debug[mode] = 1

  # Do an extra check to avoid work when we're not debugging.
  if DEBUG_GENERAL in gyp.debug.keys():
    DebugOutput(DEBUG_GENERAL, 'running with these options:')
    for (option, value) in options.__dict__.items():
      if option[0] == '_':
        continue
      if isinstance(value, basestring):
        DebugOutput(DEBUG_GENERAL, "  %s: '%s'" % (option, value))
      else:
        DebugOutput(DEBUG_GENERAL, "  %s: %s" % (option, str(value)))

  if not build_files:
    build_files = FindBuildFiles()
  if not build_files:
    print >>sys.stderr, (usage + '\n\n%s: error: no build_file') % \
                        (my_name, my_name)
    return 1

  # TODO(mark): Chromium-specific hack!
  # For Chromium, the gyp "depth" variable should always be a relative path
  # to Chromium's top-level "src" directory.  If no depth variable was set
  # on the command line, try to find a "src" directory by looking at the
  # absolute path to each build file's directory.  The first "src" component
  # found will be treated as though it were the path used for --depth.
  if not options.depth:
    for build_file in build_files:
      build_file_dir = os.path.abspath(os.path.dirname(build_file))
      build_file_dir_components = build_file_dir.split(os.path.sep)
      components_len = len(build_file_dir_components)
      for index in xrange(components_len - 1, -1, -1):
        if build_file_dir_components[index] == 'src':
          options.depth = os.path.sep.join(build_file_dir_components)
          break
        del build_file_dir_components[index]

      # If the inner loop found something, break without advancing to another
      # build file.
      if options.depth:
        break

    if not options.depth:
      raise Exception, \
            'Could not automatically locate src directory.  This is a ' + \
            'temporary Chromium feature that will be removed.  Use ' + \
            '--depth as a workaround.'

  # -D on the command line sets variable defaults - D isn't just for define,
  # it's for default.  Perhaps there should be a way to force (-F?) a
  # variable's value so that it can't be overridden by anything else.
  cmdline_default_variables = {}
  defines = []
  if options.use_environment:
    defines += ShlexEnv('GYP_DEFINES')
  if options.defines:
    defines += options.defines
  cmdline_default_variables = NameValueListToDict(defines)
  if DEBUG_GENERAL in gyp.debug.keys():
    DebugOutput(DEBUG_GENERAL,
                "cmdline_default_variables: %s" % cmdline_default_variables)

  # Set up includes.
  includes = []

  # If ~/.gyp/include.gypi exists, it'll be forcibly included into every
  # .gyp file that's loaded, before anything else is included.
  if home_dot_gyp != None:
    default_include = os.path.join(home_dot_gyp, 'include.gypi')
    if os.path.exists(default_include):
      includes.append(default_include)

  # Command-line --include files come after the default include.
  if options.includes:
    includes.extend(options.includes)

  # Generator flags should be prefixed with the target generator since they
  # are global across all generator runs.
  gen_flags = []
  if options.use_environment:
    gen_flags += ShlexEnv('GYP_GENERATOR_FLAGS')
  if options.generator_flags:
    gen_flags += options.generator_flags
  generator_flags = NameValueListToDict(gen_flags)
  if DEBUG_GENERAL in gyp.debug.keys():
    DebugOutput(DEBUG_GENERAL, "generator_flags: %s" % generator_flags)

  # TODO: Remove this and the option after we've gotten folks to move to the
  # generator flag.
  if options.msvs_version:
    print >>sys.stderr, \
      'DEPRECATED: Use generator flag (-G msvs_version=' + \
      options.msvs_version + ') instead of --msvs-version=' + \
      options.msvs_version
    generator_flags['msvs_version'] = options.msvs_version

  # Generate all requested formats (use a set in case we got one format request
  # twice)
  for format in set(options.formats):
    params = {'options': options,
              'build_files': build_files,
              'generator_flags': generator_flags,
              'cwd': os.getcwd(),
              'build_files_arg': build_files_arg,
              'gyp_binary': sys.argv[0]}

    # Start with the default variables from the command line.
    [generator, flat_list, targets, data] = Load(build_files, format,
                                                 cmdline_default_variables,
                                                 includes, options.depth,
                                                 params)

    # TODO(mark): Pass |data| for now because the generator needs a list of
    # build files that came in.  In the future, maybe it should just accept
    # a list, and not the whole data dict.
    # NOTE: flat_list is the flattened dependency graph specifying the order
    # that targets may be built.  Build systems that operate serially or that
    # need to have dependencies defined before dependents reference them should
    # generate targets in the order specified in flat_list.
    generator.GenerateOutput(flat_list, targets, data, params)

  # Done
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
