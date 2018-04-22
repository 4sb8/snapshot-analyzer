from setuptools import setup

setup(
    name="snapshotanalyzer-3000",
    version="0.1",
    author="None of your business ;)",
    description="Tool to create AWS EC2 snapshots",
    license="GPLv3+",
    packages=["shotty"],
    url="https://github.com/4sb8/snapshot-analyzer",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''',
)
