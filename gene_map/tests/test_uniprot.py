import pandas as pd
from pandas.testing import assert_frame_equal

from click.testing import CliRunner

import gene_map


def test_cli():
    args = [
        '-i', 'P35222', '-i', 'InvalidID',
        '-i', 'mygenes.txt', '-i', 'P04637',
        '--from', 'ACC', '--to', 'Gene_Name',
        '-o', 'gene_mapping.csv'
    ]

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('mygenes.txt', 'w') as fd:
            fd.write('P63244 P08246\nP68871')

        # run program
        result = runner.invoke(gene_map.main, args)

        # test output
        assert result.exit_code == 0
        assert result.output == 'Mapped 5/6 genes.\n'

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

    gm = gene_map.GeneMapper()
    df = gm.query(
        stringdb_ids,
        source_id_type='STRING',
        target_id_type='GeneID')

    assert_frame_equal(df, pd.DataFrame({
        'ID_from': stringdb_ids,
        'ID_to': ['79007', '90529']
    }))
