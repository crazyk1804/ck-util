from distutils.util import convert_path
from setuptools import setup, find_packages

main_ns = {}
path_ver = convert_path('cktools/__init__.py')
with open(path_ver) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='cktools',
    version=main_ns['__version__'],
    packages=find_packages(include=[
        'cktools',
        'cktools.*'
    ]),
)