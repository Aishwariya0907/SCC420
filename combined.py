from neo4j import GraphDatabase
import pandas as pd
import numpy as np
import subprocess

# Defining connection details
uri = "bolt://localhost:7687"
user = "test_user"
password = "test_password"

# Create a Neo4j driver instance
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_mitreattack_groups_and_counts():
    query = """
    MATCH (group:MitreAttackGroup)
    MATCH (group)-[:MITRE_ATTACK_GROUP_USES_TECHNIQUE]->(technique:MitreAttackTechnique)
    OPTIONAL MATCH (tactic:MitreAttackTactic)-[:MITRE_TACTIC_INCLUDES_TECHNIQUE]->(technique)
    OPTIONAL MATCH (group)-[:MITRE_ATTACK_GROUP_USES_SOFTWARE]->(software:MitreAttackSoftware)
    OPTIONAL MATCH (technique)<-[:MAPS_TO]-(cve:CVE)
    WITH group, 
         COUNT(DISTINCT technique) AS totalTechniques, 
         COUNT(DISTINCT tactic) AS totalTactics, 
         COUNT(DISTINCT software) AS totalSoftware,
         COLLECT(DISTINCT cve.cve_id) AS CVEs,
         COUNT(DISTINCT cve) AS total_CVE
    RETURN group.name AS Group, 
           group.type AS Type, 
           group.origin_country AS OriginCountry, 
           totalTechniques, 
           totalTactics, 
           totalSoftware,
           CVEs,
           total_CVE
    ORDER BY totalTechniques DESC
    """
    records, summary, keys = driver.execute_query(
        query,
        database_="neo4j",
    )

    # Extract records into a list of dictionaries
    data = [record.data() for record in records]

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)
    
    return df, summary

def get_cve_impact():
    query = """
    MATCH (cve:CVE)
    RETURN DISTINCT cve.cve_id AS CVE, 
                    cve.confidentialityImpact AS ConfidentialityImpact, 
                    cve.integrityImpact AS IntegrityImpact, 
                    cve.availabilityImpact AS AvailabilityImpact,
                    cve.epss_score AS EPSSScore
    """
    records, summary, keys = driver.execute_query(
        query,
        database_="neo4j",
    )

    
    data = [record.data() for record in records]
    df = pd.DataFrame(data)
    return df, summary

def get_risk_table():
    query = """
    MATCH (group:MitreAttackGroup)-[:MITRE_ATTACK_GROUP_USES_TECHNIQUE]->(technique:MitreAttackTechnique)<-[:MAPS_TO]-(cve:CVE)
    RETURN group.name AS Group, cve.cve_id AS CVE, cve.epss_score AS EPSSScore, cve.capability_description AS Relevancy
    """
    records, summary, keys = driver.execute_query(
        query,
        database_="neo4j",
    )

    
    data = [record.data() for record in records]
    df = pd.DataFrame(data)
    return df, summary

def get_confidentiality_impact_table():
    query = """
    MATCH (group:MitreAttackGroup)-[:MITRE_ATTACK_GROUP_USES_TECHNIQUE]->(technique:MitreAttackTechnique)<-[:MAPS_TO]-(cve:CVE)
    RETURN group.name AS Group, 
           cve.cve_id AS CVE, 
           cve.confidentialityImpact AS ConfidentialityImpact
    ORDER BY Group, CVE
    """
    records, summary, keys = driver.execute_query(
        query,
        database_="neo4j",
    )

    
    data = [record.data() for record in records]
    df = pd.DataFrame(data)
    return df, summary


def generate_excel():
    df, summary = get_mitreattack_groups_and_counts()

    # Calculate the maximum values for each column
    max_total_techniques = df['totalTechniques'].max()
    max_total_tactics = df['totalTactics'].max()
    max_total_software = df['totalSoftware'].max()

    # get normalized values
    df['normalized_technique'] = df['totalTechniques'] / max_total_techniques
    df['normalized_tactic'] = df['totalTactics'] / max_total_tactics
    df['normalized_software'] = df['totalSoftware'] / max_total_software

    # Calculate overall capability score
    df['capability_score'] = np.sqrt(
        df['normalized_technique']**2 +
        df['normalized_tactic']**2 +
        df['normalized_software']**2
    )

    # Sort the DataFrame by overall capability_score in descending order
    df = df.sort_values(by='capability_score', ascending=False)

    # Add overall rank column
    df['overall_rank'] = np.arange(1, len(df) + 1)

    # Classify the groups into high, medium, and low capability
    df['capability'] = pd.qcut(df['capability_score'], q=3, labels=['low capability', 'medium capability', 'high capability'])

    # Display the complete DataFrame with all columns
    print("Complete DataFrame with all columns:")
    print(df)

    # Create a separate table for group name, capability, total_CVE, and CVEs
    capability_table = df[['Group', 'capability', 'total_CVE', 'CVEs']]

    # Display the capability table
    print("\nCapability Table:")
    print(capability_table)

    # Executing the function to retrieve CVE impacts
    impact_df, impact_summary = get_cve_impact()

    # Map qualitative impacts to scores
    impact_scores = {
        'COMPLETE': 2,
        'HIGH': 2,
        'PARTIAL': 1,
        'LOW': 1,
        'NONE': 0
    }

    # Apply the mapping to create new columns
    impact_df['confi_score'] = impact_df['ConfidentialityImpact'].map(impact_scores)
    impact_df['intgrity_score'] = impact_df['IntegrityImpact'].map(impact_scores)
    impact_df['availability_score'] = impact_df['AvailabilityImpact'].map(impact_scores)

    # Calculate the maximum values for normalization
    max_confi_score = impact_df['confi_score'].max()
    max_integrity_score = impact_df['intgrity_score'].max()
    max_availability_score = impact_df['availability_score'].max()

    # Calculate normalized scores for confidentiality, integrity, and availability
    impact_df['norm_confi_score'] = impact_df['confi_score'] / max_confi_score
    impact_df['norm_integrity_score'] = impact_df['intgrity_score'] / max_integrity_score
    impact_df['norm_availability_score'] = impact_df['availability_score'] / max_availability_score

    # Calculate total impact 
    impact_df['total_impact'] = impact_df[['confi_score', 'intgrity_score', 'availability_score']].sum(axis=1)

    # Create a probability column 
    impact_df['probability'] = pd.qcut(impact_df['EPSSScore'], q=3, labels=['low probability', 'medium probability', 'high probability'])

    # Sort the DataFrame by EPSSScore in descending order
    impact_df = impact_df.sort_values(by='EPSSScore', ascending=False)

    max_impact_score = impact_df['total_impact'].max()
    impact_df['norm_total_impact'] = impact_df['total_impact'] / max_impact_score

    # Reorder columns to include the normalized scores
    impact_df = impact_df[['CVE', 'ConfidentialityImpact', 'confi_score', 'norm_confi_score', 
                        'IntegrityImpact', 'intgrity_score', 'norm_integrity_score', 
                        'AvailabilityImpact', 'availability_score', 'norm_availability_score', 
                        'total_impact','norm_total_impact', 'probability', 'EPSSScore']]

    # Display the updated Impact Table
    print("\nImpact Table with Normalized Scores:")
    print(impact_df)

    # Execute the function to retrieve Risk Table
    risk_df, risk_summary = get_risk_table()

    # Merge risk_df with df to add overall_norm_score and overall_rank
    risk_df = risk_df.merge(df[['Group', 'capability_score', 'overall_rank']], on='Group', how='left')

    # Merge norm_total_impact from impact_df to risk_df
    risk_df = risk_df.merge(impact_df[['CVE', 'norm_total_impact']], on='CVE', how='left')

    # Drop duplicate rows
    risk_df = risk_df.drop_duplicates()

    # Reorder columns to match the specified order
    risk_df = risk_df[['overall_rank','Group','capability_score','norm_total_impact','CVE','Relevancy','EPSSScore']]
    risk_df = risk_df.sort_values(by='EPSSScore', ascending=False)

    max_capability_score = risk_df['capability_score'].max()
    risk_df['norm_capability_score'] = risk_df ['capability_score'] / max_capability_score

    risk_df['inherent_total_risk'] = np.sqrt(
        risk_df['norm_total_impact']**2 +
        risk_df['EPSSScore']**2 +
        risk_df['norm_capability_score']**2
    )

    risk_df['overall_risk_rank'] = pd.qcut(risk_df['inherent_total_risk'], q=3, labels=['Low Risk', 'Medium Risk', 'High Risk'])


    # Display the Risk Table
    print("\nRisk Table:")
    print(risk_df)

    # Confidentiality Impact Table
    confidentiality_df, confidentiality_summary = get_confidentiality_impact_table()
    confidentiality_df = confidentiality_df.merge(df[['Group', 'capability_score']], on='Group', how='left')
    confidentiality_df = confidentiality_df.merge(impact_df[['CVE', 'norm_confi_score','EPSSScore']], on='CVE', how='left')
    max_capability_score = confidentiality_df['capability_score'].max()
    confidentiality_df['norm_capability_score'] = confidentiality_df ['capability_score'] / max_capability_score

    confidentiality_df['inherent_confidentiality_risk'] = np.sqrt(
        confidentiality_df['norm_confi_score']**2 +
        confidentiality_df['EPSSScore']**2 +
        confidentiality_df['norm_capability_score']**2
    )
    confidentiality_df['Conf_rank'] = pd.qcut(confidentiality_df['inherent_confidentiality_risk'], q=3, labels=['Low risk', 'Medium risk', 'High risk'])

    print("\nConfidentiality Impact Table with Capability Score and EPSSScore:")
    print(confidentiality_df)

    # Integrity Impact Table
    integrity_df = impact_df[['CVE', 'IntegrityImpact', 'norm_integrity_score', 'EPSSScore']]

    # Merge to bring in 'Group' from df based on 'CVE'
    integrity_df = integrity_df.merge(risk_df[['Group', 'CVE']], on='CVE', how='left')

    # Merge to bring in 'capability_score' from df
    integrity_df = integrity_df.merge(df[['Group', 'capability_score']], on='Group', how='left')

    max_capability_score = integrity_df['capability_score'].max()
    integrity_df['norm_capability_score'] = integrity_df ['capability_score'] / max_capability_score

    # Calculate inherent integrity risk and rank
    integrity_df['inherent_integrity_risk'] = np.sqrt(
        integrity_df['norm_integrity_score']**2 +
        integrity_df['EPSSScore']**2 +
        integrity_df['norm_capability_score']**2
    )
    integrity_df['Integrity_rank'] = pd.qcut(integrity_df['inherent_integrity_risk'], q=3, labels=['Low risk', 'Medium risk', 'High risk'])

    print("\nIntegrity Impact Table:")
    print(integrity_df)

    # Availability Impact Table
    availability_df = impact_df[['CVE', 'AvailabilityImpact', 'norm_availability_score', 'EPSSScore']]

    # Merge to bring in 'Group' from df based on 'CVE'
    availability_df = availability_df.merge(risk_df[['Group', 'CVE']], on='CVE', how='left')

    # Merge to bring in 'capability_score' from df
    availability_df = availability_df.merge(df[['Group', 'capability_score']], on='Group', how='left')

    max_capability_score = availability_df['capability_score'].max()
    availability_df['norm_capability_score'] = availability_df ['capability_score'] / max_capability_score

    # Calculate inherent availability risk and rank
    availability_df['inherent_availability_risk'] = np.sqrt(
        availability_df['norm_availability_score']**2 +
        availability_df['EPSSScore']**2 +
        availability_df['norm_capability_score']**2
    )
    availability_df['Availability_rank'] = pd.qcut(availability_df['inherent_availability_risk'], q=3, labels=['Low Risk', 'Medium Risk', 'High risk'])

    print("\nAvailability Impact Table:")
    print(availability_df)

    # Export all tables to an Excel file with separate sheets
    with pd.ExcelWriter('mitre_attack_analysis1.xlsx') as writer:
        df.to_excel(writer, sheet_name='MITRE ATT&CK Groups', index=False)
        capability_table.to_excel(writer, sheet_name='Capability Table', index=False)
        impact_df.to_excel(writer, sheet_name='Impact Table', index=False)
        risk_df.to_excel(writer, sheet_name='Risk Table', index=False)
        confidentiality_df.to_excel(writer, sheet_name='Confidentiality Impact Table', index=False)
        integrity_df.to_excel(writer, sheet_name='Integrity Impact Table', index=False)
        availability_df.to_excel(writer, sheet_name='Availability Impact Table', index=False)

    print("Data successfully exported to mitre_attack_analysis1.xlsx")



def run_flask_app():
    subprocess.run(["python", "app.py"])

if __name__ == '__main__':
    # Generate the Excel file
    generate_excel()
    
    # Close the neo4j driver connection
    driver.close()
    
    # Run the Flask app
    run_flask_app()