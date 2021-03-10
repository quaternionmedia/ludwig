from setuptools import setup, find_packages

setup(
    name='sandfly',
    install_requires='pluggy>=0.3,<1.0',
    entry_points={'console_scripts': ['sandfly=sandfly.main:main']},
    packages=find_packages(),
)
