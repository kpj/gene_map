import os

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

import gene_map


@pytest.fixture
def gene_mapper(tmpdir):
    df = pd.DataFrame([
        ('A_ID', 'type01', 'foo'),
        ('A_ID', 'type02', 'bar'),
        ('B_ID', 'type01', 'baz'),
        ('B_ID-1', 'type02', 'qux'),
    ])
    df.to_csv(
        os.path.join(tmpdir, 'HUMAN_9606_idmapping.dat.gz'),
        sep='\t', compression='gzip')

    gm = gene_map.GeneMapper(cache_dir=tmpdir)
    return gm

def test_from_uniprot(gene_mapper):
    id_list = ['A_ID', 'B_ID']
    id_map = gene_mapper.query(
        id_list, source_id_type='ACC', target_id_type='type01')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['A_ID', 'B_ID'],
        'ID_to': ['foo', 'baz']
    }))

def test_to_uniprot(gene_mapper):
    id_list = ['bar', 'qux']
    id_map = gene_mapper.query(
        id_list, source_id_type='type02', target_id_type='ACC')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['bar', 'qux'],
        'ID_to': ['A_ID', 'B_ID']
    }))

def test_via_uniprot(gene_mapper):
    id_list = ['foo', 'baz']
    id_map = gene_mapper.query(
        id_list, source_id_type='type01', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['baz', 'foo'],
        'ID_to': ['qux', 'bar']
    }))

def test_invalid_id(gene_mapper):
    id_list = ['foo', 'INVALID']
    id_map = gene_mapper.query(
        id_list, source_id_type='type01', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['foo'],
        'ID_to': ['bar']
    }))
