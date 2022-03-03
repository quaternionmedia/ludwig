from setuptools import setup, find_packages

setup(
    name='ludwig',
    install_requires=[
        'pluggy>=0.3,<1.0',
        'python-rtmidi>=1.4.9,<1.5.0'
    ],
    entry_points={'console_scripts': ['ludwig=ludwig.main:main']},
    packages=find_packages(),
)
