from setuptools import setup

setup(name='flask-geokit',
      version='0.1.6',
      packages=['flaskext'],
      namespace_packages=['flaskext'],
      author='Alex Toney',
      author_email='toneyalex@gmail.com',
      url='https://github.com/bluemoon/flask-geokit',
      license='BSD',
      description='Geocoding toolkit',
      zip_safe=False,
      long_description='',
      platforms=['any'],
      install_requires=[
          'furl', 
          'geohash', 
          'Flask'
          ],
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
