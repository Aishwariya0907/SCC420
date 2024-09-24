
# Automated Cyber Risk Assessment with Threat Data-Driven Graph-Based Model

## Overview

This project provides an **Automated Cyber Risk Assessment** by leveraging a **Threat Data-Driven Graph-Based Model** built on the MITRE ATT&CK framework, using **Neo4j** for graph-based data representation. The project includes integrating various datasets such as CVEs, MITRE ATT&CK TTPs, and other related threat intelligence data, followed by detailed analysis using Python scripts for statistical insights and visualizations.

The core workflow starts with populating the Neo4j database, followed by data retrieval, analysis, and visualization using Python. The result is a comprehensive understanding of vulnerabilities and their relationships to adversarial techniques and threat actors.

## Project Structure

```
|-- mitre.py                     # Script to load MITRE ATT&CK and CVE data into Neo4j
|-- combined.py                  # Data extraction from Neo4j and exporting to Excel
|-- mitre_attack_analysis1.xlsx   # Excel file containing exported MITRE ATT&CK data
|-- analysis_final.py            # Visualization and statistical analysis
|-- two_way_capability.py         # Two-way analysis of group capabilities
|-- two_way_risk.py               # Two-way risk analysis
|-- README.md                    # This file
```

## Prerequisites

Make sure you have the following dependencies installed:

- Python 3.x
- Neo4j Database
- Pandas (`pip install pandas`)
- Matplotlib (`pip install matplotlib`)
- Seaborn (`pip install seaborn`)
- Neo4j Python Driver (`pip install neo4j`)
- Flask (`pip install Flask`)
- `ontolocy` Python library for importing MITRE ATT&CK data

## Project Workflow

### Step 1: Populating Neo4j Database with MITRE ATT&CK and CVE Data

**Script: `mitre.py`**

The `mitre.py` script connects to a Neo4j database and populates it with data from the MITRE ATT&CK framework and CVE databases using the **ontolocy** library.

- The **MITRE ATT&CK framework** is imported using the **`MitreAttackParser`** component of `ontolocy`, which transforms STIX data into Neo4j's graph-based structure.
- **CVE to TTP mappings** are imported using pre-mapped data provided by the Center for Threat-Informed Defense.
- Environment variables are used to securely manage Neo4j connection credentials.
- CVEs are enriched with CVSS, CIA Impact, and EPSS data from external sources to provide more detailed vulnerability insights.

#### Cypher Query to Load CSV Data into Neo4j

To load the **CVE to TTP mappings** CSV file into Neo4j, use the following Cypher query:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///cve-10.21.2021_attack-9.0-enterprise.csv' AS row
WITH row.capability_id AS id
RETURN id, count(*) AS idCount
ORDER BY idCount DESC
LIMIT 10;
```

- This query loads the data from the specified CSV file.
- The `WITH` clause is used to process the `capability_id` from the file.
- It counts the number of occurrences of each `capability_id` and orders them by frequency.

You can use this query as part of the process to integrate your CSV data into Neo4j and begin analyzing relationships between CVEs and capabilities.

```bash
python mitre.py
```

This step ensures that all data sources are structured as graph nodes and relationships within Neo4j, establishing connections between CVEs, TTPs, and other relevant threat data. 

### Step 2: Retrieving Data from Neo4j and Exporting to Excel

**Script: `combined.py`**

Once the data is loaded into Neo4j, `combined.py` extracts relevant data for further analysis and exports it into an Excel file (`mitre_attack_analysis1.xlsx`). 

- It queries the Neo4j database to extract details such as:
  - Group and technique relationships.
  - Vulnerabilities and their corresponding attack techniques.
  - The mapping of CVEs to TTPs and their associated risk scores.

```bash
python combined.py
```

This step ensures that data is accessible in a structured format (Excel) for further analysis and visualization.

### Step 3: Analyzing Data with Visualization and Statistical Analysis

#### 3.1 Two-Way Capability Analysis

**Script: `two_way_capability.py`**

This script analyzes group capabilities based on the extracted data. It visualizes the relationship between threat groups, their tactics, techniques, and capabilities.

```bash
python two_way_capability.py
```

- The script generates visualizations such as:
  - Distribution of groups by capability.
  - Comparison of capabilities between different threat actor groups.
  
#### 3.2 Two-Way Risk Analysis

**Script: `two_way_risk.py`**

This script focuses on risk analysis, identifying patterns between threat groups and the risk levels associated with specific techniques and vulnerabilities.

```bash
python two_way_risk.py
```

- Visualizations include:
  - Risk scores associated with specific CVEs and techniques.
  - Comparative risk analysis for different types of threat actors.

#### 3.3 Final Statistical Analysis and Visualizations

**Script: `analysis_final.py`**

This script performs a detailed statistical analysis of the MITRE ATT&CK data and generates a comprehensive set of visualizations. It reads from the exported Excel file (`mitre_attack_analysis1.xlsx`) and provides insights into vulnerabilities, attack techniques, and threat actor behaviors.

```bash
python analysis_final.py
```

- Key visualizations include:
  - **Number of Groups per Each Type**
  - **Distribution of Groups by Capability and Type**
  - **Correlation Matrix of Tactics, Techniques, Software, CVEs, and Capability Score**
  - **Combined Influence of Group Types and Capability Levels on Risks**

These visualizations help in understanding relationships between various components of the dataset, offering valuable insights for risk assessment.

## Graph Titles

Here are some key graphs generated by the project:

- **Number of Groups per Each Type**
- **Distribution of Groups by Capability and Type**
- **Correlation Matrix of Tactics, Techniques, Software, CVEs, and Capability Score**
- **Combined Influence of Group Types and Capability Levels on Risks**

## Conclusion

This project provides a robust framework for **automated cyber risk assessment** using a graph-based model. By combining Neo4j’s powerful graph database with data-driven analysis, this model allows for the effective representation and understanding of threat intelligence data. The two-way capability and risk analyses offer valuable insights into threat actor behaviors and vulnerability exploitation patterns.

With Neo4j as the backbone, this system is designed for scalability and future-proofing, ensuring that as new vulnerabilities and adversarial techniques emerge, they can be seamlessly integrated into the existing framework. The accompanying visualizations offer actionable insights, supporting decision-making in threat defense and mitigation strategies.

---
#   S C C 4 2 0 
 
 #   S C C 4 2 0 
 
 
