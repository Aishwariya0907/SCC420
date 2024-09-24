from ontolocy import init_ontolocy
from ontolocy.tools import MitreAttackParser
import os

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv('C:/Users/AishwariyaVenkatesan/OneDrive/Documents/MainFolder/Metrea/ontology/test.env')

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"NEO4J_URI: {NEO4J_URI}")
print(f"NEO4J_USERNAME: {NEO4J_USERNAME}")
print(f"NEO4J_PASSWORD: {NEO4J_PASSWORD}")

# Initialize the connection to Neo4j
init_ontolocy(
    neo4j_uri=NEO4J_URI,
    neo4j_username=NEO4J_USERNAME,
    neo4j_password=NEO4J_PASSWORD
)

parser = MitreAttackParser()

# Parse MITRE ATT&CK data from URL
parser.parse_url('https://github.com/mitre-attack/attack-stix-data/raw/master/enterprise-attack/enterprise-attack.json')
