import xml.etree.ElementTree as ET
import pandas as pd
import sqlite3
from typing import List, Dict, Any


def parse_kgml(file_path: str, disease: str) -> List[Dict[str, Any]]:
    """
    Parses KGML files to extract gene-pathway relationships and associated diseases.

    Args:
        file_path (str): Path to the KGML file.
        disease (str): Name of the disease.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing pathway data.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    pathways = []
    for entry in root.findall("entry"):
        entry_id = entry.get("id")
        entry_name = entry.get("name")
        entry_type = entry.get("type")

        gene_names = entry_name.split(" ")

        for gene_name in gene_names:
            pathways.append(
                {
                    "entry_id": entry_id,
                    "gene_id": gene_name,
                    "entry_type": entry_type,
                    "disease": disease,
                }
            )

    return pathways



def parse_gaf(file_path: str) -> pd.DataFrame:
    """
    Parses GAF files to extract gene-GO term associations.

    Args:
        file_path (str): Path to the GAF file.

    Returns:
        pd.DataFrame: A DataFrame containing gene-GO term associations.
    """
    dtype = {2: str, 4: str}  # DB_Object_Symbol  # GO_ID

    gaf_df = pd.read_csv(
        file_path, sep="\t", comment="!", header=None, dtype=dtype, low_memory=False
    )
    gaf_df.columns = [
        "DB",
        "DB_Object_ID",
        "DB_Object_Symbol",
        "Qualifier",
        "GO_ID",
        "DB:Reference",
        "Evidence_Code",
        "With_or_From",
        "Aspect",
        "DB_Object_Name",
        "DB_Object_Synonym",
        "DB_Object_Type",
        "Taxon",
        "Date",
        "Assigned_By",
        "Annotation_Extension",
        "Gene_Product_Form_ID",
    ]

    gene_go_associations = gaf_df[["DB_Object_Symbol", "GO_ID"]].drop_duplicates()

    return gene_go_associations


def insert_genes(data: List[str], cursor: sqlite3.Cursor) -> None:
    """
    Inserts gene data into the database.

    Args:
        data (List[str]): List of unique gene IDs.
        cursor (sqlite3.Cursor): Database cursor.
    """
    for gene_id in data:
        cursor.execute("INSERT OR IGNORE INTO genes (gene_id) VALUES (?)", (gene_id,))


# Function to insert pathways data into the database
def insert_pathways(data: List[Dict[str, Any]], cursor: sqlite3.Cursor) -> None:
    """
    Inserts pathways data into the database.

    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing pathway data.
        cursor (sqlite3.Cursor): Database cursor.
    """
    for row in data:
        cursor.execute(
            "INSERT INTO pathways (entry_id, gene_id, entry_type, disease) VALUES (?, ?, ?, ?)",
            (row["entry_id"], row["gene_id"], row["entry_type"], row["disease"]),
        )


def insert_gene_go_associations(data: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """
    Inserts gene-GO associations data into the database.

    Args:
        data (pd.DataFrame): DataFrame containing gene-GO associations.
        cursor (sqlite3.Cursor): Database cursor.
    """
    for _, row in data.iterrows():
        cursor.execute(
            "INSERT INTO gene_go_associations (gene_id, go_id) VALUES (?, ?)",
            (row["DB_Object_Symbol"], row["GO_ID"]),
        )


def create_tables(cursor: sqlite3.Cursor) -> None:
    """
    Creates the necessary tables in the SQLite database.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
    """
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS genes (
                        gene_id TEXT PRIMARY KEY
                     )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS pathways (
                        entry_id TEXT,
                        gene_id TEXT,
                        entry_type TEXT,
                        disease TEXT,
                        FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
                     )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS gene_go_associations (
                        gene_id TEXT,
                        go_id TEXT,
                        FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
                     )"""
    )


def main() -> None:
    """
    Main function to parse KGML and GAF files and insert the data into the SQLite database.
    """
    # Create a SQLite database connection
    conn = sqlite3.connect("gene_pathway_db.sqlite")
    c = conn.cursor()

    # Create tables
    create_tables(c)

    # File paths and disease names
    files_and_diseases = [
        ("KEGG_data/KGML/hsa05010.xml", "Alzheimer's disease"),
        ("KEGG_data/KGML/hsa05012.xml", "Parkinson's disease"),
        ("KEGG_data/KGML/hsa04930.xml", "Type II diabetes mellitus"),
        ("KEGG_data/KGML/hsa05210.xml", "Colorectal cancer"),
    ]

    # Collect unique gene IDs
    unique_genes = set()

    # Parse and insert pathways data
    for file_path, disease in files_and_diseases:
        pathways_data = parse_kgml(file_path, disease)
        insert_pathways(pathways_data, c)
        for pathway in pathways_data:
            unique_genes.add(pathway["gene_id"])

    # Insert unique genes
    insert_genes(list(unique_genes), c)

    # Parse and insert gene-GO associations data
    gaf_data = parse_gaf("goa_human.gaf")
    insert_gene_go_associations(gaf_data, c)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
