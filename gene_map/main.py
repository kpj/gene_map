import os
import sys
import urllib

from typing import List, Optional

import click
import pandas as pd


class GeneMapper:
    def __init__(self, data_fname: str = '/tmp/uniprot.dat.gz') -> None:
        self._ensure_data(data_fname)
        self.df = pd.read_table(
            data_fname,
            header=None, names=['UniProtKB-AC','ID_type','ID'])

        self.default_id_type = 'ACC'  # UniProtKB-AC

    def _ensure_data(self, fname: str) -> str:
        """ Check that UniProt mapping data exists and download of not
        """
        _url = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz'
        if not os.path.exists(fname):
            print('Caching', fname)
            urllib.request.urlretrieve(_url, fname)
        return fname

    def get_id_types(self) -> List[str]:
        """ Return list of all possible ID formats
        """
        return ['ACC'] + list(sorted(self.df['ID_type'].unique().tolist()))

    def query(
        self,
        id_list: List[str],
        source_id_type: str, target_id_type: str
    ) -> pd.DataFrame:
        """ Wrapper for all ID conversions
        """
        # sanity checks
        valid_id_formats = self.get_id_types()
        for id_format in [source_id_type, target_id_type]:
            if id_format not in valid_id_formats:
                print(
                    f'Invalid ID format "{id_format}".\n'
                    f'Available are: {valid_id_formats}'
                    , file=sys.stderr)
                sys.exit(-1)

        if source_id_type == target_id_type:
            print('Source ID is target ID, aborting...')
            sys.exit(-1)

        # do query
        if source_id_type == self.default_id_type:
            return self._convert_from(
                id_list, target_id_type)
        elif target_id_type == self.default_id_type:
            return self._convert_to(
                id_list, source_id_type)
        else:
            return self._convert_inbetween(
                id_list, source_id_type, target_id_type)

    def _convert_from(
        self, id_list: List[str], target_id_type: str
    ) -> pd.DataFrame:
        """ Convert from UniProtKB-AC to any other ID format
        """
        df_res = self.df[
            (self.df['UniProtKB-AC'].isin(id_list))
            & (self.df['ID_type']==target_id_type)
        ].reset_index(drop=True)

        df_res = df_res[['UniProtKB-AC','ID']].copy()
        df_res.rename(columns={
            'UniProtKB-AC': 'ID_from',
            'ID': 'ID_to'
        }, inplace=True)

        return df_res

    def _convert_to(
        self, id_list: List[str], source_id_type: str
    ) -> pd.DataFrame:
        """ Convert from any ID format to UniProtKB-AC
        """
        df_res = self.df[
            (self.df['ID'].isin(id_list))
            & (self.df['ID_type']==source_id_type)
        ].reset_index(drop=True)

        df_res = df_res[['ID', 'UniProtKB-AC']].copy()
        df_res.rename(columns={
            'UniProtKB-AC': 'ID_to',
            'ID': 'ID_from'
        }, inplace=True)

        return df_res

    def _convert_inbetween(
        self,
        id_list: List[str],
        source_id_type: str, target_id_type: str
    ) -> pd.DataFrame:
        """ Convert between any two formats
        """
        # try naive mapping way: ID_from -> ACC -> ID_to
        id_acc = self._convert_to(
            id_list, source_id_type)
        id_target = self._convert_from(
            id_acc['ID_to'].tolist(), target_id_type)

        df_res = id_acc.merge(
            id_target, left_on='ID_to', right_on='ID_from',
            how='left', suffixes=('_from','_to'))

        df_res = df_res[['ID_from_from','ID_to_to']].copy()
        df_res.rename(columns={
            'ID_from_from': 'ID_from',
            'ID_to_to': 'ID_to'
        }, inplace=True)

        return df_res

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
    gm = GeneMapper()
    df = gm.query(actual_input, source_id_type, target_id_type)

    # save result
    if output is None:
        df.to_csv(sys.stdout, index=False)
    else:
        df.to_csv(output, index=False)

if __name__ == '__main__':
    main()
