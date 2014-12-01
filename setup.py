from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='uwosh.intranet.tabs',
      version=version,
      description="tabs implementation for the 'portal' like aspect of the intranet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uwosh', 'uwosh.intranet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.layout',
          'plone.app.z3cform',
          'plone.z3cform',
          'plone.formwidget.contenttree'
      ],
      extras_require = { 'test': [
            'plone.app.testing',
      ]},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
