"""
NHANES ETL Pipeline.

Loads, harmonizes, and prepares NHANES 1999-2002 data for phenotypic age modeling.
"""

from .nhanes_etl import run_nhanes_etl

__all__ = ["run_nhanes_etl"]
