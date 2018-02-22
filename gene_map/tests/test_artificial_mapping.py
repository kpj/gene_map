import os

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from ..gene_mapper import GeneMapper


@pytest.fixture
def gm(tmpdir):
    df = pd.DataFrame([
        ('A_ID', 'type01', 'foo'),
        ('A_ID', 'type02', 'bar'),
        ('A_ID', 'type03', 'fubar'),
        ('B_ID', 'type01', 'baz'),
        ('B_ID-1', 'type02', 'qux'),
        ('A_ID', 'weirdtype', 13),
        ('A_ID', 'weirdtype', '42')
    ])
    df.to_csv(
        os.path.join(tmpdir, 'HUMAN_9606_idmapping.dat.gz'),
        sep='\t', compression='gzip')

    gm = GeneMapper(cache_dir=tmpdir)
    return gm

def test_from_uniprot(gm):
    id_list = ['A_ID', 'B_ID']
    id_map = gm.query(
        id_list, source_id_type='ACC', target_id_type='type01')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['A_ID', 'B_ID'],
        'ID_to': ['foo', 'baz']
    }))

def test_to_uniprot(gm):
    id_list = ['bar', 'qux']
    id_map = gm.query(
        id_list, source_id_type='type02', target_id_type='ACC')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['bar', 'qux'],
        'ID_to': ['A_ID', 'B_ID']
    }))

def test_via_uniprot(gm):
    id_list = ['foo', 'baz']
    id_map = gm.query(
        id_list, source_id_type='type01', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['baz', 'foo'],
        'ID_to': ['qux', 'bar']
    }))

def test_invalid_id(gm):
    id_list = ['foo', 'INVALID']
    id_map = gm.query(
        id_list, source_id_type='type01', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['foo'],
        'ID_to': ['bar']
    }))

def test_none_sourceid(gm):
    id_list = ['foo', 'qux', 'fubar']
    id_map = gm.query(
        id_list, source_id_type='auto', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['foo', 'fubar', 'qux'],
        'ID_to': ['bar', 'bar', 'qux']
    }))

@pytest.mark.parametrize('test_argument', [
    'foo',
    set(['foo', 'INVALID']),
    ('foo', 'INVALID'),
])
def test_argument_types(gm, test_argument):
    id_map = gm.query(
        test_argument, source_id_type='type01', target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': ['foo'],
        'ID_to': ['bar']
    }))

@pytest.mark.parametrize('test_argument', ['13', 13, '42', 42])
def test_nonstring_input(gm, test_argument):
    id_map = gm.query(
        test_argument,
        source_id_type='weirdtype',
        target_id_type='type02')
    assert_frame_equal(id_map, pd.DataFrame({
        'ID_from': [str(test_argument)],
        'ID_to': ['bar']
    }))
