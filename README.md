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
  -i, --input TEXT   If it exists, treated as file with whitespace-separated
                     gene ids. Otherwise treated as a gene id itself.
                     [required]
  --from TEXT        Source ID type.  [required]
  --to TEXT          Target ID type.  [required]
  -o, --output TEXT  CSV-file to save result to.
  --help             Show this message and exit.
```

## Getting started

Inputs can be either gene ids or files containing whitespace-separated gene ids:

```bash
$ cat mygenes.txt
P63244 P08246
P68871
$ gene_map -i P35222 -i P04637 -i mygenes.txt --from ACC --to Gene_Name
ID_from,ID_to
P35222,CTNNB1
P08246,ELANE
P68871,HBB
P04637,TP53
P63244,RACK1
```
