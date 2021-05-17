import sqlite3
import os
import numpy as np
import pandas as pd
import multiprocessing
from joblib import Parallel, delayed


class gnomAD_DB:
    
    def __init__(self, genodb_path, parallel=True):
        
        self.cpu_count = int(multiprocessing.cpu_count())
        self.parallel = parallel

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
        
        with self.open_dbconn() as conn:
            c = conn.cursor()
            c.executescript(sql_create)
    
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
        
        rows = [tuple(x) for x in var_df.to_numpy()]
        
        sql_input = f"""
                    INSERT OR REPLACE INTO gnomad_db({", ".join(self.columns)})
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """
        with self.open_dbconn() as conn:
            c = conn.cursor()
            c.executemany(sql_input, rows)
    
    
    def _sanitize_variants(self, var_df: pd.DataFrame) -> pd.DataFrame:
        var_df = var_df.replace(".", np.NaN)
        var_df["chrom"] = var_df["chrom"].astype(str)
        var_df["chrom"] = var_df.chrom.apply(lambda x: x.replace("chr", ""))
        return var_df
    
    def _pack_var_args(self, var: pd.Series) -> str:
        return (var.chrom, var.pos, var.ref, var.alt)
    
    def _get_maf_from_df(self, var_df: pd.DataFrame, query: str="AF") -> pd.Series:
        
        var_df = self._sanitize_variants(var_df)
        
        rows = [self._pack_var_args(var) for _, var in var_df.iterrows()]
        
        
        
        query = self._query_columns(query, prefix="tt")
        
        sql_create_temp_table = f"""
        CREATE TEMPORARY TABLE temp_table(
            chrom TEXT,
            pos INTEGER,
            ref TEXT,
            alt TEXT
            );
        """
        
        sql_insert = """
        INSERT INTO temp_table (chrom, pos, ref, alt)
        VALUES (?,?,?,?);
        """
        
        sql_query = f"""
        SELECT {query} FROM temp_table as tt
        LEFT JOIN gnomad_db AS gdb 
        ON tt.chrom = gdb.chrom AND tt.pos = gdb.pos AND tt.ref = gdb.ref AND tt.alt = gdb.alt;
        """
        
        with self.open_dbconn() as conn:
            c = conn.cursor()
            c.executescript(sql_create_temp_table)
            c.executemany(sql_insert, rows)
            return pd.read_sql_query(sql_query, conn)
        
    
    
    def get_maf_from_df(self, var_df: pd.DataFrame, query: str="AF") -> pd.Series:
        if var_df.empty:
            return var_df
        
        if self.parallel and len(var_df) > 100 * self.cpu_count:
            out = np.array_split(var_df, self.cpu_count)
            assert len(out) == self.cpu_count
            out = Parallel(self.cpu_count)(delayed(self._get_maf_from_df)(df, query) for df in out)
            out = pd.concat(out)
            out.set_index(var_df.index, inplace=True)
            assert len(var_df) == len(out)
        else:
            out = self._get_maf_from_df(var_df, query)
        
        return out
        
        
    
    def _query_columns(self, query: str, prefix: str=None) -> str:
        if prefix is None:
            query = ", ".join(self.columns) if query == '*' else query
        else:
            query = f"{prefix}.chrom, {prefix}.pos, {prefix}.ref, {prefix}.alt, " + ", ".join(self.columns[4:]) if query == '*' else query
        return query
    
    def _pack_from_str(self, var: str) -> str:
        var = var.split(":")
        chrom = var[0].replace("chr", "")
        pos = int(var[1])
        ref = var[2].split(">")[0]
        alt = var[2].split(">")[1]
        return chrom, pos, ref, alt
        
    
    def query_direct(self, sql_query: str):
         with self.open_dbconn() as conn:
            c = conn.cursor()
            return pd.read_sql_query(sql_query, conn)
    
    def get_mafs_for_interval(self, chrom: str, interval_start: int, interval_end: int, query: str="AF") -> pd.DataFrame:
                
        query = self._query_columns(query)
        
        sql_query = f"""
        SELECT {query} FROM gnomad_db
        WHERE chrom = '{chrom}' AND pos BETWEEN {interval_start} AND {interval_end}
        """
        
        return self.query_direct(sql_query)
        
    
    
    def get_maf_from_str(self, var: str, query: str="AF") -> float:
        # variant in form chrom:pos:ref>alt
        
        chrom, pos, ref, alt = self._pack_from_str(var)
        
        query = self._query_columns(query)
        
        sql_query = f"""
        SELECT {query} FROM gnomad_db
        where chrom = '{chrom}' AND pos = {pos} AND ref = '{ref}' AND alt = '{alt}';
        """
        
        return self.query_direct(sql_query).squeeze()