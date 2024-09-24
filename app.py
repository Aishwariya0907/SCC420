import pandas as pd
from flask import Flask, render_template

# Function to load the Excel data
def load_data():
    file_path = 'mitre_attack_analysis1.xlsx'
    data = pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dictionary of DataFrames
    return data

# Function to generate the threat profile for a specific group
def generate_threat_profile(group_name, data):
    # Extract group information from the 'MITRE ATT&CK Groups' sheet
    group_info = data['MITRE ATT&CK Groups'][data['MITRE ATT&CK Groups']['Group'] == group_name].iloc[0]
    
    # Extract the information for the group from the 'Risk Table' sheet
    risk_info = data['Risk Table'][data['Risk Table']['Group'] == group_name]
    
    # Merge the risk info with the 'Impact Table' on the CVE column to get the relevant CVEs
    impact_info = data['Impact Table'].merge(
        risk_info[['CVE', 'overall_risk_rank', 'inherent_total_risk', 'Relevancy']],
        on='CVE', how='inner'  # Only include CVEs that are associated with the group
    )
    
    # Filter out CVEs that are associated with the group 
    associated_cves = impact_info if not impact_info.empty else pd.DataFrame()

    # Structure the profile with the group's details and associated CVEs
    profile = {
        "group_name": group_info['Group'],
        "type": group_info['Type'],
        "origin_country": group_info['OriginCountry'],
        "overall_rank": group_info['overall_rank'],
        "capability_score": group_info['capability_score'],
        "total_techniques": group_info['totalTechniques'],
        "total_tactics": group_info['totalTactics'],
        "total_software": group_info['totalSoftware'],
        "total_CVE": group_info['total_CVE'],  # Include total CVEs from the group
        "cves": associated_cves.to_dict('records') if not associated_cves.empty else []  # Convert CVEs to list of dictionaries
    }
    
    return profile

# Flask application
app = Flask(__name__)

# Load the data when the application starts
data = load_data()

# Home route to display the list of groups
@app.route('/')
def index():
    # Get a list of groups and their details from 'MITRE ATT&CK Groups' sheet
    groups = [(row['Group'], row['overall_rank'], row['Type'], row['OriginCountry']) for _, row in data['MITRE ATT&CK Groups'].iterrows()]
    return render_template('index.html', groups=groups)

# Profile route to display a detailed profile for a specific group
@app.route('/profile/<group_name>')
def profile(group_name):
    # Generate the threat profile for the given group name
    profile = generate_threat_profile(group_name, data)
    return render_template('profile.html', profile=profile)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
