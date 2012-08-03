from setuptools import setup, find_packages
import sys, os

version = '0.1'

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
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_dir={'': 'src'},
      extras_require=dict(
        test=(
            'zope.app.testing',
            'zope.testing',
            'lazr.smtptest',
            ),
        ),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'gspread',
          'jinja2',
	        'boto',
          'msgpack-python',
      ],
      entry_points="""
        [console_scripts]
        spray = spray.spray:app
      """,
      )
