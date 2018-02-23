from setuptools import setup, find_packages


setup(
    name='gene_map',
    version='0.4.2',

    description='Map gene ids using UniProt.',

    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',

    url='https://github.com/kpj/gene_map',

    author='kpj',
    author_email='kpjkpjkpjkpjkpjkpj@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],

    keywords='uniprot genes mapping',
    packages=find_packages(exclude=['tests']),

    install_requires=['click', 'pandas'],

    entry_points={
        'console_scripts': [
            'gene_map=gene_map:main',
        ],
    }
)
