from distutils.core import setup

setup(
  name = 'pycheesi',         # How you named your package folder (MyLib)
  packages = ['pycheesi'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'The class ic game of Parcheesi, in Python!',   # Give a short description about your library
  author = 'John Wendeborn',                   # Type in your name
  author_email = 'jwendeborn@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/wendeborn8/pycheesi',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/wendeborn8/pycheesi.git',    # I explain this later on
  keywords = ['game', 'parcheesi', 'pygame', 'board', 'ludo', 'parchisi', 'pycheesi'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'pygame',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Anyone',      # Define that your audience are developers
    'Topic :: Entertainment :: Board Game',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)