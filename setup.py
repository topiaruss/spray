from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='spray',
      version=version,
      description="A python subsystem for turning web-site or database events into",
      long_description="""\
messaging or social actions""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='event-processing social-networks',
      author='Russ Ferriday',
      author_email='russf@topia.com',
      url='sponsorcraft.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
