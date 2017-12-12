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
    data = resp.text

    df = pd.read_table(io.StringIO(data))
    if df.empty:
        print('No mappings found, invalid ID types?')

    return df

@click.command()
@click.option(
    'input_list', '--input', '-i', multiple=True, required=True,
    help='ID to convert.')
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
    df = query(input_list, source_id_type, target_id_type)

    if output is None:
        df.to_csv(sys.stdout, index=False)
    else:
        df.to_csv(output, index=False)

if __name__ == '__main__':
    main()
