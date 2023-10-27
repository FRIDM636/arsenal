"""Packaging logic for arsenal """

import setuptools

setuptools.setup(
    name='arsenal',
    version='1.1.1',
    url='https://github.com/Orange-Cyberdefense/arsenal',
    license='GPL-3.0',
    author='Guillaume Muh, mayfly',
    author_email='csr-audit.so@orange.com',
    description='Arsenal is just a quick inventory, reminder and launcher for pentest commands. ',
    keywords=[
        'security',
        'pen testing',
        'cli',
        'tools',
        'tmux',
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Security',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
    packages=setuptools.find_packages(),
    install_requires=[
        'libtmux',
        'docutils',
        'pyperclip',
        'pyyaml',
        'pyfzf',
    ],
    include_package_data=True,
    package_data={'': ['cheats/*']},
    scripts=(
        'bin/arsenal-cli',
    )
)
