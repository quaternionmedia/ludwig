from setuptools import setup, find_packages

setup(
    name='ludwig',
    install_requires='pluggy>=0.3,<1.0',
    entry_points={'console_scripts': ['ludwig=ludwig.main:main']},
    packages=find_packages(),
)
