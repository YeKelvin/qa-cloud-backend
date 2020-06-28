import pathlib

from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='test-platform-server',
    version='0.1',
    description='',
    long_description=README,
    long_description_content_type="text/markdown",
    url='',
    license='',
    author='Kaiwen.Ye',
    author_email='',
    packages=find_packages(exclude=('test',)),
    include_package_data=True,
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "requests",
    ],
    extras_require={
        'test': []
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
