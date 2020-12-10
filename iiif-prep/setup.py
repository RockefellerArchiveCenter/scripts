from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
]w

setup(
    name='iiif-pipeline',
    version='0.1',
    description="Prepare files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/RockefellerArchiveCenter/scripts/iiif-prep',
    author='Rockefeller Archive Center',
    author_email='archive@rockarch.org',
    license='MIT',
    packages=find_packages(),
    install_requires=requirements,
    tests_require=['pytest', 'vcrpy'],
    zip_safe=False)
