import setuptools
from pip._internal.req import parse_requirements


# Parse the requirements file
install_reqs = [str(ir.requirement)
                for ir in parse_requirements('requirements.txt', session='hack')]


# Read the contents of the README file
with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='zalando_de_scraper',
    version='0.1.2',
    description='A python package to scrape data from `zalando.de` website',
    long_description=long_description,
    author='Ilias Balah',
    author_email='ibalah45@gmail.com',
    url='https://github.com/ebalah/zalando_de_project',
    packages=setuptools.find_packages(),
    install_requires=install_reqs,
    classifiers=[
        'Intended Audience :: Upwork Client',
        'Programming Language :: Python :: 3.10'
    ],
    entry_points={
        'console_scripts': [
            'sc_script=zalando_de.main:scrape'
        ]
    },
    python_requires='>=3.6, <4',
    include_package_data=True,
)