from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('easy_menu').__version__


setup(
    name='easy-menu',
    version=get_version(),
    description='Super Simple Terminal Command Launcher Generator',
    author='mogproject',
    author_email='mogproj@gmail.com',
    license='Apache 2.0 License',
    url='https://github.com/mogproject/easy-menu',
    install_requires=[
        'pyyaml',
        'six',
    ],
    tests_require=[
        'unittest2',
        'mock',
        'jinja2 == 2.6',  # specify library version to support Python 3.2
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
    entry_points="""
    [console_scripts]
    easy-menu = easy_menu.easy_menu:main
    """,
)
