"""
Top-level module for gene_map.
Here, we simply publish the GeneMapper class
"""

from .main import main
from .gene_mapper import GeneMapper

__all__ = ['main', 'GeneMapper']
