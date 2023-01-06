from setuptools import setup, find_packages

setup(
    name='ludwig',
    install_requires=[
        'pluggy>=1.0,<2.0',
        'python-rtmidi>=1.4.9,<1.5.0',
        'pydantic>=1.10.4,<1.11.0',
    ],
    entry_points={'console_scripts': ['ludwig=ludwig.main:main']},
    packages=find_packages(),
)
