#!/usr/bin/env python3
"""
Scopus Abstract Retrieval Script

This script retrieves full abstracts for academic papers from Scopus using their EIDs.
It processes a CSV file containing paper metadata and enriches it with full abstracts,
saving both individual text files and an updated CSV.

Author: Adriano Reimer
Created: Oct 21, 2023
"""

import os
import logging
from typing import Optional
from pathlib import Path
import pandas as pd
from pybliometrics.scopus import AbstractRetrieval

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('abstract_retrieval.log'),
        logging.StreamHandler()
    ]
)

class AbstractProcessor:
    """Handles the retrieval and processing of Scopus abstracts."""
    
    INVALID_CHARS = str.maketrans({
        char: '_' for char in '/\\:*?"<>|;+{}[]()@'
    })
    
    def __init__(self, input_file: str, output_dir: str):
        """
        Initialize the AbstractProcessor.
        
        Args:
            input_file: Path to input CSV file
            output_dir: Directory for output files
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _sanitize_filename(self, text: str, max_length: int = 100) -> str:
        """
        Create a safe filename from text.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum length for the filename
            
        Returns:
            Sanitized filename string
        """
        if not isinstance(text, str):
            return ""
        return text[:max_length].translate(self.INVALID_CHARS)
    
    def _get_abstract(self, eid: str) -> Optional[str]:
        """
        Retrieve abstract for a given EID.
        
        Args:
            eid: Scopus EID
            
        Returns:
            Abstract text if available, None otherwise
        """
        try:
            abstract = AbstractRetrieval(eid)
            return abstract.description
        except Exception as e:
            logging.warning(f"Failed to retrieve abstract for EID {eid}: {str(e)}")
            return None
            
    def process_abstracts(self):
        """Process all abstracts from the input file."""
        try:
            df = pd.read_csv(self.input_file)
            logging.info(f"Successfully loaded {len(df)} records from {self.input_file}")
        except Exception as e:
            logging.error(f"Failed to read input file: {str(e)}")
            return
            
        # Add column for full abstracts
        df['full_abstract'] = ''
        
        for index, row in df.iterrows():
            eid = str(row.get('eid', ''))
            title = str(row.get('title', ''))
            
            if not eid:
                logging.warning(f"Missing EID at row {index}")
                continue
                
            abstract = self._get_abstract(eid) or "No abstract available"
            
            # Save individual text file
            filename = f"{eid}_{self._sanitize_filename(title)}.txt"
            filepath = self.output_dir / filename
            
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Title: {title}\n\nAbstract:\n{abstract}")
                logging.info(f"Saved abstract for EID {eid}")
            except Exception as e:
                logging.error(f"Failed to save file for EID {eid}: {str(e)}")
                
            # Update dataframe
            df.loc[index, 'full_abstract'] = abstract
            
        # Save updated CSV
        output_csv = self.output_dir / f"enriched_{self.input_file.name}"
        df.to_csv(output_csv, index=False)
        logging.info(f"Saved enriched CSV to {output_csv}")

def main():
    """Main execution function."""
    # Configuration
    INPUT_FILE = "busca_scopus_TITLE-ABS-KEY_deep brain stimulation_Accumbens_Mice.csv"
    OUTPUT_DIR = "abstracts_output"
    
    # Create processor and run
    processor = AbstractProcessor(INPUT_FILE, OUTPUT_DIR)
    processor.process_abstracts()

if __name__ == "__main__":
    main()
