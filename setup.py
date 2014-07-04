# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from aldryn_segmentation import __version__

REQUIREMENTS = [
    # 'django-cms>=3.0.3'
    # 'aldryn-country-segment>=0.1.0'
]

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-segmentation',
    version=__version__,
    description='Visitor Segmentation for django CMS',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-segmentation',
    packages=find_packages(),
    package_data={
        "aldryn_segmentation": [
            "locale/*/LC_MESSAGES/*",
            "templates/aldryn_segmentation/*",
        ],
    },
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)
