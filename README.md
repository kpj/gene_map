# gene_map

[![PyPI](https://img.shields.io/pypi/v/gene_map.svg?style=flat)](https://pypi.python.org/pypi/gene_map)

Tool for converting between various gene ids.

## Installation

```bash
$ pip install gene_map
```

## Usage

```bash
$ gene_map --help
Usage: gene_map [OPTIONS]

  Map gene ids between various formats.

Options:
  -i, --input TEXT   If it exists, treated as file with newline-separated gene
                     ids. Otherwise treated as a gene id itself.  [required]
  --from TEXT        Source ID type.  [required]
  --to TEXT          Target ID type.  [required]
  -o, --output TEXT  CSV-file to save result to.
  --help             Show this message and exit.
```

## Getting started

Inputs can be either gene ids or files containing whitespace-separated gene ids:

```bash
$ cat mygenes.txt
Q9UM73 P97793
Q17192
$ gene_map -i P13368 -i P20806 -i mygenes.txt --from ACC --to GENENAME
From,To
P13368,sev
P20806,sev
Q9UM73,ALK
P97793,Alk
Q17192,BBXA1
```
