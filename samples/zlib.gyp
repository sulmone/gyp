{
  'targets': [
    {
      'name': 'zlib',
      'type': 'static_library',
      'sources': [
        'adler32.c',
        'compress.c',
        'crc32.c',
        'crc32.h',
        'deflate.c',
        'deflate.h',
        'gzio.c',
        'infback.c',
        'inffast.c',
        'inffast.h',
        'inffixed.h',
        'inflate.c',
        'inflate.h',
        'inftrees.c',
        'inftrees.h',
        'mozzconf.h',
        'trees.c',
        'trees.h',
        'uncompr.c',
        'zconf.h',
        'zlib.h',
        'zutil.c',
        'zutil.h',
      ],
      'vs_props': [ '../../build/external_code.vsprops' ],
      'dependent_settings': {
        'include_dirs': [
          '.',
        ],
      },
    },
  ],
}
