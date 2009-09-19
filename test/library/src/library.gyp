{
  'variables': {
    'moveable_function%': 0,
  },
  'targets': [
    {
      'target_name': 'program',
      'type': 'executable',
      'dependencies': [
        'lib1',
        'lib2',
      ],
      'sources': [
        'program.c',
      ],
    },
    {
      'target_name': 'lib1',
      'type': '<(library)',
      'sources': [
        'lib1.c',
      ],
      'conditions': [
        ['moveable_function=="lib1"', {
          'sources': [
            'lib1_moveable.c',
          ],
        }],
      ],
    },
    {
      'target_name': 'lib2',
      'type': '<(library)',
      'sources': [
        'lib2.c',
      ],
      'conditions': [
        ['moveable_function=="lib2"', {
          'sources': [
            'lib2_moveable.c',
          ],
        }],
      ],
    },
  ],
  'conditions': [
    ['OS=="linux"', {
      'target_defaults': {
        'cflags': ['-m32'],
        'ldflags': ['-m32'],
      },
    }],
  ],
}
