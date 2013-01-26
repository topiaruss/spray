from setuptools import setup, find_packages

version = '0.2'

setup(name='spray',
      version=version,
      description="A system that performs actions in response to events",
      long_description="""\
messaging or social actions""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: GNU Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
      keywords='event-processing social-networks',
      author='Russ Ferriday',
      author_email='russf@topia.com',
      url='sponsorcraft.com',
      license='NCSA',
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      package_dir={'': 'src'},
      extras_require=dict(
        test=(
            'zope.app.testing',
            'zope.testing',
            'MiniMock',
            'Mock',
            ),
        ),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'boto',
          'gspread>=0.0.13',
          'jinja2',
          'msgpack-python',
          'zope.interface',
      ],
      entry_points="""
        [console_scripts]
        client = spray.client:app
        dryrun = spray.client:dryrun
        sprayd = spray.sprayd:app
      """,
      dependency_links=[
      'http://github.com/Sponsorcraft/gspread/tarball/master#egg=gspread-0.0.13'],
      )
