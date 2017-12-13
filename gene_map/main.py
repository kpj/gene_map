import os
import sys

from typing import List, Optional

import click

from .gene_mapper import SUPPORTED_ORGANISMS, GeneMapper


@click.command(help='Map gene ids between various formats.')
@click.option(
    'input_list', '--input', '-i', multiple=True, required=True,
    help='If it exists, treated as file with whitespace-separated gene ids. Otherwise treated as a gene id itself.')
@click.option(
    'source_id_type', '--from', required=True,
    help='Source ID type.')
@click.option(
    'target_id_type', '--to', required=True,
    help='Target ID type.')
@click.option(
    '--output', '-o', default=None, type=click.File('w'),
    help='CSV-file to save result to.')
@click.option(
    '--organism', default='HUMAN_9606', type=click.Choice(SUPPORTED_ORGANISMS),
    help='Organism to convert IDs in.')
@click.option(
    '--cache-dir', default='/tmp', type=click.Path(exists=True, file_okay=False),
    help='Folder to store ID-databases in.')
def main(
    input_list: List[str],
    source_id_type: str, target_id_type: str,
    output: Optional[str], organism: str,
    cache_dir: str
) -> None:
    # parse input
    actual_input = []
    for inp in input_list:
        if os.path.exists(inp):
            with open(inp) as fd:
                actual_input.extend(fd.read().split())
        else:
            actual_input.append(inp)

    # do query
    gm = GeneMapper(organism, cache_dir=cache_dir)
    df = gm.query(actual_input, source_id_type, target_id_type)

    # save result
    if output is None:
        df.to_csv(sys.stdout, index=False)
    else:
        df.to_csv(output, index=False)

if __name__ == '__main__':
    main()
