import os
import io
import sys

from typing import List, Optional

import click
import requests
import pandas as pd


def query(
    id_list: List[str],
    source_id_type: str, target_id_type: str
) -> pd.DataFrame:
    _url = 'http://www.uniprot.org/uploadlists/'

    params = {
        'from': source_id_type,
        'to': target_id_type,
        'format': 'tab',
        'query': ' '.join(id_list)
    }

    resp = requests.get(_url, params=params)
    resp.raise_for_status()
    data = resp.text

    df = pd.read_table(io.StringIO(data))
    if df.empty:
        print('No mappings found, invalid ID types?')

    return df

@click.command()
@click.option(
    'input_list', '--input', '-i', multiple=True, required=True,
    help='If it exists, treated as file with newline-separated gene ids. Otherwise treated as a gene id itself.')
@click.option(
    'source_id_type', '--from', required=True,
    help='Source ID type.')
@click.option(
    'target_id_type', '--to', required=True,
    help='Target ID type.')
@click.option(
    '--output', '-o', default=None,
    help='CSV-file to save result to.')
def main(
    input_list: List[str],
    source_id_type: str, target_id_type: str,
    output: Optional[str]
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
    try:
        df = query(actual_input, source_id_type, target_id_type)
    except requests.exceptions.HTTPError as ex:
        print('[ERROR]' + str(ex)[:100] + '...')
        sys.exit(-1)

    # save result
    if output is None:
        df.to_csv(sys.stdout, index=False)
    else:
        df.to_csv(output, index=False)

if __name__ == '__main__':
    main()
