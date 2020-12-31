from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
includefiles = []

build_options = {'packages': [], 'excludes': [], 'include_files':includefiles, 'optimize':2}

base = 'Win32GUI'

executables = [
    Executable('ADC_detector.py', base=base, icon="test.ico")
]

setup(name='HUB voltage & current monitor program',
      version = '1.0.0',
      description = 'HUB voltage & current monitor program.',
      options = {'build_exe': build_options},
      executables = executables)
