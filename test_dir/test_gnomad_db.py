from gnomad_db.database import gnomAD_DB
import pandas as pd
import numpy as np
import pytest
import yaml

@pytest.fixture
def database():
    with open("script_config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
       
    database_location = config['database_location']
    
    return gnomAD_DB(database_location)

def test_get_maf_from_df(database):
    
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
    
    observed = database.get_maf_from_df(dummy_var_df, "*")
    
    assert expected.equals(observed)
    
    expected = pd.DataFrame({'AF': {0: np.NaN, 1: 0.000243902}})
    
    observed = database.get_maf_from_df(dummy_var_df, "AF")
    
    assert expected.equals(observed)

 
  

def test_get_maf_from_str(database):
    
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
    
    observed = database.get_maf_from_str(dummy_str, "*")
    
    assert expected.equals(observed)
   
    expected = 0.000243902
    
    observed = database.get_maf_from_str(dummy_str, "AF")
    
    assert round(expected, 5) == round(observed, 5) 

    
    
    
def test_insert_variants(database):
    
    dummy_var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=database.columns, index_col=False)
    dummy_var_df = dummy_var_df.replace(".", np.NaN)
    
    database.insert_variants(dummy_var_df)
    
    observed = database.get_maf_from_df(dummy_var_df, "*")
    
    assert dummy_var_df[["pos", "ref", "alt"]].equals(observed[["pos", "ref", "alt"]])


def test_query_variants_x320_000_columns(database):
    
    dummy_var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=database.columns, index_col=False)
    dummy_var_df = dummy_var_df.replace(".", np.NaN)
    
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    dummy_var_df = pd.concat([dummy_var_df, dummy_var_df])
    
    observed = database.get_maf_from_df(dummy_var_df, "AF")
    
    assert len(observed) == len(dummy_var_df)


