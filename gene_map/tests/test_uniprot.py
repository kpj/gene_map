import os

import pandas as pd
from pandas.testing import assert_frame_equal

from click.testing import CliRunner

import pytest

from ..main import main
from ..gene_mapper import GeneMapper


def test_cli():
    cache_dir = 'cache'
    args = [
        '-i', 'P35222', '-i', 'InvalidID',
        '-i', 'mygenes.txt', '-i', 'P04637',
        '--from', 'ACC', '--to', 'Gene_Name',
        '-o', 'gene_mapping.csv',
        '--cache-dir', cache_dir
    ]
    cache_fname = f'{cache_dir}/HUMAN_9606_idmapping.dat.gz'

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('mygenes.txt', 'w') as fd:
            fd.write('P63244 P08246\nP68871')
        os.makedirs(cache_dir)

        # run program
        result = runner.invoke(main, args)

        # test output
        assert result.exit_code == 0

        expected_output = f'''Downloading to {cache_fname}
Mapped 5/6 genes.
'''
        assert result.output == expected_output

        df_out = pd.read_csv('gene_mapping.csv')
        assert_frame_equal(df_out, pd.DataFrame({
            'ID_from': [
                'P04637', 'P08246', 'P35222',
                'P63244', 'P68871'],
            'ID_to': [
                'TP53', 'ELANE', 'CTNNB1',
                'RACK1', 'HBB']
        }))

def test_api():
    stringdb_ids = [
        '9606.ENSP00000306407',
        '9606.ENSP00000337461']

    gm = GeneMapper()
    df = gm.query(
        stringdb_ids,
        source_id_type='STRING',
        target_id_type='GeneID')

    assert_frame_equal(df, pd.DataFrame({
        'ID_from': stringdb_ids,
        'ID_to': ['79007', '90529']
    }))

def test_nonhuman_genemapping():
    ecoli_gene = ['ligA']

    gm_hum = GeneMapper(
        organism='HUMAN_9606')
    gm_ecoli = GeneMapper(
        organism='ECOLI_83333')

    df_hum = gm_hum.query(
        ecoli_gene,
        source_id_type='Gene_Name',
        target_id_type='GeneID')
    df_ecoli = gm_ecoli.query(
        ecoli_gene,
        source_id_type='Gene_Name',
        target_id_type='GeneID')

    assert df_hum.empty
    assert_frame_equal(df_ecoli, pd.DataFrame({
        'ID_from': ecoli_gene,
        'ID_to': ['946885']
    }))

def test_invalid_organism():
    with pytest.raises(RuntimeError):
        GeneMapper(organism='INVALID_ORGANISM')
