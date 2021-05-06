import sqlite3
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

class gnomAD_DB:
    
    def __init__(self, genodb_path):

        self.db_file = os.path.join(genodb_path, 'gnomad_db.sqlite3')
        
        self.columns = ["chrom", "pos", "ref", "alt", "AF", "AF_afr", "AF_eas", "AF_fin", "AF_nfe", "AF_asj", "AF_oth", "AF_popmax"]
        
        if not os.path.exists(self.db_file):
            if not os.path.exists(genodb_path):
                os.mkdir(genodb_path)
            self.create_table()
    
    
    
    def open_dbconn(self):
        return sqlite3.connect(self.db_file)
    
    
    def create_table(self):
        sql_create = """
        CREATE TABLE gnomad_db (
            chrom TEXT,
            pos INTEGER,
            ref TEXT,
            alt TEXT,
            AF REAL,
            AF_afr REAL,
            AF_eas REAL,
            AF_fin REAL,
            AF_nfe REAL,
            AF_asj REAL,
            AF_oth REAL,
            AF_popmax REAL,
            PRIMARY KEY (chrom, pos, ref, alt));
        """
        
        sql_index = """
        CREATE INDEX gnomad_db_chrom_pos_index 
        ON gnomad_db(chrom, pos);
        """
        
        with self.open_dbconn() as conn:
            c = conn.cursor()
            c.executescript(sql_create)
            c.executescript(sql_index)    
    
    def insert_variants(self, var_df: pd.DataFrame):
        assert np.array_equal(
            var_df.columns, 
            np.array(
                self.columns
            )
        ), "Columns are missing. The dataframe should contain: " + ", ".join(self.columns)
        
        
        
        
        ## sort and process var_df
        var_df = var_df.reindex(self.columns, axis=1)
        var_df = self._sanitize_variants(var_df)
        
        var_df = var_df[var_df.apply(lambda x: 
                                     len(x.ref) == (x.ref.count("A") + x.ref.count("T") + x.ref.count("C") + x.ref.count("G"))
                                     and
                                     len(x.alt) == (x.alt.count("A") + x.alt.count("T") + x.alt.count("C") + x.alt.count("G"))
                                                    ,axis=1)]
        
        rows = [self._pack_var_args(var) for _, var in var_df.iterrows()]
        
        sql_input = f"""
                    BEGIN TRANSACTION;
                    INSERT OR REPLACE INTO gnomad_db({", ".join(self.columns)})
                    VALUES 
                    {",".join(rows)};
                    COMMIT;
                    """
        with self.open_dbconn() as conn:
            c = conn.cursor()
            c.executescript(sql_input)
    
    
    def _sanitize_variants(self, var_df: pd.DataFrame) -> pd.DataFrame:
        var_df["chrom"] = var_df.chrom.apply(lambda x: x.replace("chr", ""))
        return var_df
    
    def _pack_var_args(self, var: pd.Series, variant_keys_only=False) -> str:
        if variant_keys_only:
            return f"('{var.chrom}', {var.pos}, '{var.ref}', '{var.alt}')"
        else:
            return f"('{var.chrom}', {var.pos}, '{var.ref}', '{var.alt}', {var.AF}, \
        {var.AF_afr}, {var.AF_eas}, {var.AF_fin}, {var.AF_nfe}, {var.AF_asj}, {var.AF_oth}, {var.AF_popmax})"
    
    
    def get_maf(self, var: pd.Series, score_id: str) -> float:
        
        sql_request = f"""
        SELECT {score_id} from gnomad_db
        WHERE chrom = '{var.chrom}' AND pos = {var.pos} AND ref = '{var.ref}' AND alt = '{var.alt}';
        """
        
        with self.open_dbconn() as conn:
            res = pd.read_sql_query(sql_request, conn).values
            assert len(res) <= 1
            return  res.flatten()
    
    def get_maf_from_df(self, var_df: pd.DataFrame, score_id: str) -> pd.Series:
        # TODO: Doesn't work when all variants are missing!
        # TODO: join between local table and sql table! speed-up
        var_df = self._sanitize_variants(var_df)
        res = var_df.progress_apply(lambda x: self.get_maf(x, score_id), axis=1)
        
        columns = self.columns if "*" in score_id else score_id.replace(" ", "").split(",")
        
        return pd.DataFrame(list(res), columns=columns)
    
    
    def get_maf_from_str(self, var, score_id) -> float:
        # variant in form chrom:pos:ref>alt
        
        var = var.split(":")
        chrom = var[0].replace("chr", "")
        pos = var[1]
        ref = var[2].split(">")[0]
        alt = var[2].split(">")[1]
        
        var = pd.Series([chrom, pos, ref, alt], index=["chrom", "pos", "ref", "alt"])
        
        columns = self.columns if "*" in score_id else score_id.replace(" ", "").split(",")
        res = pd.Series(self.get_maf(var, score_id), index=columns)
        
        return res
            