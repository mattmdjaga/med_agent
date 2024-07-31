# Llama Agentic System with Gene Pathway Analysis

## Setup

### 1. Get the Repository and Submodules

Clone the repository and its submodules:

```bash
git clone --recurse-submodules https://github.com/mattmdjaga/med_agent
```

### 2. Setup the Environment

Create and activate a virtual environment:

```bash
cd med_agent/llama-agentic-system
# Create and activate a virtual environment
ENV=agentic_env
conda create -n $ENV python=3.10
conda activate $ENV

# Install the package
pip install -r requirements.txt
```

### 3. Data

Unzip the KEGG data in the med_agent folder:

```bash
unzip KEGG_data.zip
```

Place the "Gene Association File (GAF)" file in the `med_agent` folder, not in the `llama-agentic-system` folder.
You can run this to uncompressed the GAF file:

```bash
gunzip goa_human.gaf.gz
```

### 4. Create the Database

Run the pre-processing script to create the SQLite database:

```bash
python pre_process.py
```

### 5. Setup Llama Agentic System

There's a README with setup instructions here [llama-agentic-system](https://github.com/meta-llama/llama-agentic-system) but below are the main instructions that should be enough.

```bash
cd llama-agentic-system
pip install -e .
```

Download the models:

```bash
# Download the 8B model, this can be run on a single GPU
llama download meta-llama/Meta-Llama-3.1-8B-Instruct

# Download safety models
llama download meta-llama/Prompt-Guard-86M --ignore-patterns original
llama download meta-llama/Llama-Guard-3-8B --ignore-patterns original
```

Configure the inference server:

```bash
llama inference configure
```

You might need to add `/original` to the paths of the models in the config file. Configure the agentic system:

```bash
llama agentic_system configure
```

### 6. Run the System

Start the inference server:

```bash
llama inference start
# You might need to add the flag --disable-ipv6 (I had to)
llama inference start --disable-ipv6
```

Run the chat interface with custom tools:

```bash
PYTHONPATH=. mesop app/chat_with_custom_tools.py
```

This should give you a chat interface where you can ask questions.

## System Architecture

The system is designed to provide an LLM-powered agent capable of generating hypotheses about gene involvement in specific diseases. The system integrates data from KEGG pathways and Gene Ontology (GO) associations, stores it in an SQLite database, and uses custom tools to query this data.

### Components

1. **Data Pre-processing**:
   - **KGML Parsing**: Parses KEGG pathway files to extract gene-pathway relationships and associated diseases.
   - **GAF Parsing**: Parses Gene Ontology Association Files to extract gene-GO term associations.
   - **Database Insertion**: Inserts parsed data into an SQLite database.

2. **Llama Agentic System**:
   - **Custom Tools**: Provides tools for querying the database to retrieve diseases associated with genes, GO terms associated with genes, and perform downstream analysis on gene interactions.
   - **Inference Server**: Runs the language model to process queries.
   - **Chat Interface**: Provides an interface to interact with the system and query the database using natural language.

### Data Flow

1. **Data Ingestion**:
   - KEGG pathway data (KGML files) and Gene Ontology data (GAF file) are ingested.
   - The `parse_kgml` function parses KGML files to extract gene-pathway relationships.
   - The `parse_gaf` function parses the GAF file to extract gene-GO term associations.

2. **Database Creation**:
   - The parsed data is stored in an SQLite database using functions `insert_genes`, `insert_pathways`, and `insert_gene_go_associations`.

3. **Query Processing**:
   - Custom tools are used to query the database and retrieve relevant information.
   - Tools can be found in **"med_agent/llama-agentic-system/llama_agentic_system/tools/genes.py"**
   - Tools `GeneDiseaseAssociationTool`, `GeneGoTermsTool`, and `DownstreamAnalysisTool` are implemented to handle specific queries.

4. **Hypothesis Generation**:
   - The agent processes user queries using the custom tools and can be asked to make hypotheses in follow up.
   - Downstream analysis is performed to predict gene interactions and their possible effects on disease pathways.

### Custom Tools

1. **GeneDiseaseAssociationTool**:
   - Retrieves diseases associated with a given gene from the database.

2. **GeneGoTermsTool**:
   - Retrieves GO terms associated with a given gene from the database.

3. **DownstreamAnalysisTool**:
   - Performs downstream analysis on gene interactions to predict their effects on disease pathways.

### Example Query

An example query to the system might be:

"get the go terms associated with NUDT4B"
"get diseases associated with hsa:10213"
"do downstream analvsis on hsa:5594"

The system will use the `GeneDiseaseAssociationTool` to retrieve and provide this information.

### Operation

To operate the system, follow these steps:

1. Start the inference server using `llama inference start`.
2. Run the chat interface with custom tools using `PYTHONPATH=. mesop app/chat_with_custom_tools.py`.
3. Interact with the chat interface and ask questions to generate hypotheses based on the integrated data.
