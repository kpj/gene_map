import os
import sys
import urllib

from typing import List

import pandas as pd


SUPPORTED_ORGANISMS = [
    'ARATH_3702', 'CAEEL_6239', 'CHICK_9031', 'DANRE_7955', 'DICDI_44689',
    'DROME_7227', 'ECOLI_83333', 'HUMAN_9606', 'MOUSE_10090', 'RAT_10116',
    'SCHPO_284812', 'YEAST_559292'
]

class GeneMapper:
    def __init__(
        self, organism: str = 'HUMAN_9606', cache_dir: str = '/tmp', verbose: bool = True
    ) -> None:
        self.verbose = verbose

        # download data
        assert organism in SUPPORTED_ORGANISMS, \
            f'"{organism}" is not in {SUPPORTED_ORGANISMS}'
        fname = f'{organism}_idmapping.dat.gz'
        data_path = os.path.join(cache_dir, fname)
        self._ensure_data(fname, data_path)

        # parse data
        self.df = pd.read_table(
            data_path,
            header=None, names=['UniProtKB-AC','ID_type','ID'])
        self.df['UniProtKB-AC'] = self._normalize_uniprot_isoforms(
            self.df['UniProtKB-AC'])

        self.default_id_type = 'ACC'  # UniProtKB-AC
        self.autodetect_id_type = 'auto'

    def _ensure_data(self, remote_file: str, local_file: str) -> str:
        """ Check that UniProt mapping data exists and download if not
        """
        _url = f'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/{remote_file}'
        if not os.path.exists(local_file):
            if self.verbose:
                print('Caching', local_file)
            urllib.request.urlretrieve(_url, local_file)
        return local_file

    def get_id_types(self) -> List[str]:
        """ Return list of all possible ID formats
        """
        uniprot_id_types = list(sorted(
            self.df['ID_type'].unique().tolist()))
        return [
            self.autodetect_id_type,
            self.default_id_type
        ] + uniprot_id_types

    def query(
        self,
        id_list: List[str],
        source_id_type: str, target_id_type: str
    ) -> pd.DataFrame:
        """ Wrapper for all ID conversions
        """
        # sanity checks
        if target_id_type == self.autodetect_id_type:
            print(
                'Only `source_id_type` can be set to '
                f'{self.autodetect_id_type}, aborting...')
            sys.exit(-1)

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
        source_id_type_orig = source_id_type
        if source_id_type == self.autodetect_id_type:
            # If the source id is not given, convert everything
            # to ACC and follow standard procedure from then on
            acc_ids = set(id_list) & set(self.df['UniProtKB-AC'])

            acc_ids_res = self._convert_to(
                list(set(id_list)-acc_ids), source_id_type)
            acc_ids_new = set(acc_ids_res['ID_to'].tolist())

            # change mapping parameters
            source_id_type = self.default_id_type

            id_list_orig = id_list[:]
            id_list = list(acc_ids | acc_ids_new)

            orig_id_map = pd.concat([
                acc_ids_res,
                pd.DataFrame(
                    [(v, v) for v in acc_ids],
                    columns=['ID_from', 'ID_to'])
            ])

        if source_id_type == self.default_id_type:
            df_res = self._convert_from(
                id_list, target_id_type)
        elif target_id_type == self.default_id_type:
            df_res = self._convert_to(
                id_list, source_id_type)
        else:
            df_res = self._convert_inbetween(
                id_list, source_id_type, target_id_type)

        if source_id_type_orig == self.autodetect_id_type:
            df_tmp = orig_id_map.merge(
                df_res, left_on='ID_to', right_on='ID_from')

            df_res = df_tmp[['ID_from_x', 'ID_to_y']].copy()
            df_res.rename(columns={
                'ID_from_x': 'ID_from',
                'ID_to_y': 'ID_to'
            }, inplace=True)

        # sanitize query
        df_res.drop_duplicates(inplace=True)
        df_res.sort_values(by='ID_from', inplace=True)
        df_res.reset_index(drop=True, inplace=True)

        return df_res

    def _normalize_uniprot_isoforms(self, ser: pd.Series) -> pd.Series:
        """ Take into account that UniProt isoforms of P50053
            have IDs as follows: P50053-1, P50053-2, ...
            Normalize them so they map to the same ID
        """
        return ser.apply(lambda x: x.split('-')[0])

    def _post_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Clean up given dataframe
        """
        return df.dropna().drop_duplicates()

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

        return self._post_process(df_res)

    def _convert_to(
        self, id_list: List[str], source_id_type: str
    ) -> pd.DataFrame:
        """ Convert from any ID format to UniProtKB-AC
        """
        df_res = self.df[
            (self.df['ID'].isin(id_list)) &
            (
                source_id_type == self.autodetect_id_type or
                self.df['ID_type'] == source_id_type
            )
        ].reset_index(drop=True)

        df_res = df_res[['ID', 'UniProtKB-AC']].copy()
        df_res.rename(columns={
            'UniProtKB-AC': 'ID_to',
            'ID': 'ID_from'
        }, inplace=True)

        return self._post_process(df_res)

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

        return self._post_process(df_res)
