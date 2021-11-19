from gnomad_db.database import gnomAD_DB
import pandas as pd
import numpy as np
import pytest
import yaml

@pytest.fixture
def database():
    with open("script_config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
    
    genome = config["genome"]
    database_location = config['database_location']
    
    database = gnomAD_DB(database_location, genome=genome)
    
    var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=database.columns, index_col=False)
    
    database.insert_variants(var_df)
    
    return database

    

def test_get_info_from_df(database):
    
    dummy_var_df = pd.DataFrame({
                                    "chrom": ["1", "21"], 
                                    "pos": [21, 9825790], 
                                    "ref": ["T", "C"], 
                                    "alt": ["G", "T"]
    })
    
    
    expected = pd.DataFrame({
                                'chrom': {0: '1', 1: '21'},
                                 'pos': {0: 21, 1: 9825790},
                                 'ref': {0: 'T', 1: 'C'},
                                 'alt': {0: 'G', 1: 'T'},
                                 'AF': {0: np.NaN, 1: 0.000243902},
                                 'AF_afr': {0: np.NaN, 1: 0.0},
                                 'AF_eas': {0: np.NaN, 1: 0.0},
                                 'AF_fin': {0: np.NaN, 1: 0.000959693},
                                 'AF_nfe': {0: np.NaN, 1: 0.0},
                                 'AF_asj': {0: np.NaN, 1: 0.0},
                                 'AF_oth': {0: np.NaN, 1: 0.0},
                                 'AF_popmax': {0: None, 1: None}
    })
    
    observed = database.get_info_from_df(dummy_var_df, "*")

    assert expected.equals(observed[expected.columns])
    
    expected = pd.DataFrame({'AF': {0: np.NaN, 1: 0.000243902}})
    
    observed = database.get_info_from_df(dummy_var_df, "AF")
    
    assert expected.equals(observed[expected.columns])

 
  

def test_get_info_from_str(database):
    
    dummy_str = "21:9825790:C>T"
    
    
    expected = pd.Series({
                         'chrom': '21',
                         'pos': 9825790,
                         'ref': 'C',
                         'alt': 'T',
                         'AF': 0.000243902,
                         'AF_afr': 0.0,
                         'AF_eas': 0.0,
                         'AF_fin': 0.000959693,
                         'AF_nfe': 0.0,
                         'AF_asj': 0.0,
                         'AF_oth': 0.0,
                         'AF_popmax': None
    })
    
    observed = database.get_info_from_str(dummy_str, "*")
    
    assert expected.equals(observed[expected.index])
   
    expected = 0.000243902
    
    observed = database.get_info_from_str(dummy_str, "AF")
    
    assert round(expected, 5) == round(observed, 5) 

    
    
    
def test_insert_variants(database):
    
    dummy_var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=database.columns, index_col=False)
    dummy_var_df = dummy_var_df.replace(".", np.NaN)
    
    database.insert_variants(dummy_var_df)
    
    observed = database.get_info_from_df(dummy_var_df, "*")
    
    dummy_var_df["pos"] = dummy_var_df["pos"].astype(int)
    observed["pos"] = observed["pos"].astype(int)
    
    assert len(dummy_var_df) == len(observed)

    assert dummy_var_df[["pos", "ref", "alt"]].equals(observed[["pos", "ref", "alt"]])


def test_query_variants_x320_000_rows(database):
    
    dummy_var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=database.columns, index_col=False)
    dummy_var_df = dummy_var_df.replace(".", np.NaN)
    
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    
    # parallel
    observed = database.get_info_from_df(dummy_var_df, "AF")
    
    expected_af = dummy_var_df.AF.astype(float).values
    observed_af = observed.AF.astype(float).values
        
    assert len(observed) == len(dummy_var_df)

    values = abs(expected_af - observed_af)
    
    assert np.logical_or(values < 0.00001, np.logical_and(np.isnan(expected_af), np.isnan(observed_af))).all()
    
    # single core
    dummy_var_df = dummy_var_df[:10]
    observed = database.get_info_from_df(dummy_var_df, "AF")
    
    expected_af = dummy_var_df.AF.astype(float).values
    observed_af = observed.AF.astype(float).values
        
    assert len(observed) == len(dummy_var_df)
    
    
    values = abs(expected_af - observed_af)
    
    assert np.logical_or(values < 0.00001, np.logical_and(np.isnan(expected_af), np.isnan(observed_af))).all()
    
    

def test_pack_from_str(database):
    
    expected = ('21', 9825790, 'C', 'T')
    
    observed = database._pack_from_str("21:9825790:C>T")
    
    assert expected == observed

#def test_query_columns(database):
#    
#    expected = 'chrom, pos, ref, alt, AF, AF_afr, AF_eas, AF_fin, AF_nfe, AF_asj, AF_oth, AF_popmax'
#    observed = database._query_columns("*")
#    
#    expected = 'tt.chrom, tt.pos, tt.ref, tt.alt, AF, AF_afr, AF_eas, AF_fin, AF_nfe, AF_asj, AF_oth, AF_popmax'
#    observed = database._query_columns("*", prefix="tt")
    
    
    
    


def test_get_interval_from_str(database):
    
    expected = pd.DataFrame({'chrom': {0: '21', 1: '21', 2: '21', 3: '21', 4: '21'},
                             'pos': {0: 9825790, 1: 9825790, 2: 9825790, 3: 9825791, 4: 9825793},
                             'ref': {0: 'C', 1: 'C', 2: 'C', 3: 'T', 4: 'C'},
                             'alt': {0: 'CT', 1: 'G', 2: 'T', 3: 'TGCG', 4: 'T'},
                             'AF': {0: 0.00097561, 1: 0.000731707, 2: 0.000243902, 3: 0.0, 4: 0.000804182},
                             'AF_afr': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                             'AF_eas': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                             'AF_fin': {0: 0.0, 1: 0.0, 2: 0.000959693, 3: 0.0, 4: 0.0},
                             'AF_nfe': {0: 0.00145879, 1: 0.00109409, 2: 0.0, 3: 0.0, 4: 0.00126263},
                             'AF_asj': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                             'AF_oth': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                             'AF_popmax': {0: 0.00145879, 1: 0.00109409, 2: np.NaN, 3: np.NaN, 4: 0.00126263}})
    
    observed = database.get_info_for_interval(chrom=21, interval_start=9825787, interval_end=9825793, query="*")
    
    assert expected.equals(observed[expected.columns])