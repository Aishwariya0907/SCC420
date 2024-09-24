import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns

# Load the Excel file
file_path = 'mitre_attack_analysis1.xlsx'  # Replace with the path to your Excel file

# Load the 'MITRE ATT&CK Groups' sheet from the Excel file
mitre_groups_df = pd.read_excel(file_path, sheet_name='MITRE ATT&CK Groups')

# 1. Basic bar graph: Number of groups per each type
plt.figure(num=1,figsize=(10, 6))
data = mitre_groups_df['Type'].value_counts()
palette1 = sns.color_palette('pastel', n_colors=len(data))
data.plot(kind='barh', color=palette1)
plt.title('Number of Groups per Each Type')
plt.ylabel('Type of Group')
plt.xlabel('Number of Groups')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
plt.close()




#grph 2
# Reorder the 'capability' categories to be: High, Medium, Low
mitre_groups_df['capability'] = pd.Categorical(mitre_groups_df['capability'], 
                                               categories=['high capability', 'medium capability', 'low capability'], 
                                               ordered=True)

# Group by 'capability' and 'Type' to count the number of groups for each capability level
capability_groups = mitre_groups_df.groupby(['capability', 'Type']).size().unstack(fill_value=0)

# Plot with aesthetic colors and adjust the figure size to fit the legend
plt.figure(num=2,figsize=(8, 5))  # Adjust figure size
aesthetic_colors = ['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd']  # Soft, pastel-like colors
capability_groups.plot(kind='bar', stacked=True, figsize=(8, 5), color=aesthetic_colors)
plt.title('Distribution of Groups by Capability and Type')
plt.xlabel('Capability Level (High, Medium, Low)')
plt.ylabel('Number of Groups')
plt.xticks(rotation=0)

# Place the legend completely outside the plot area on the right
plt.legend(title='Group Type', loc='center left', bbox_to_anchor=(1, 0.5))

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()


#graph3 
# Plot Histogram and KDE for the 'capability_score' column
plt.figure(figsize=(10, 6))

# Plot histogram with density normalization
plt.hist(mitre_groups_df['capability_score'], bins=20, alpha=0.6, color='b', density=True, label='Histogram')

# Plot the Kernel Density Estimate (KDE) line
mitre_groups_df['capability_score'].plot(kind='kde', color='r', label='KDE')

# Add titles and labels
plt.title('Histogram and KDE of Capability Score')
plt.xlabel('Capability Score')
plt.ylabel('Density')

# Show the legend
plt.legend()

# Display the plot
plt.show()


#graph 4 -5  dist

# Generate a range of x values for plotting the fitted distributions
x = np.linspace(min(mitre_groups_df['capability_score']), max(mitre_groups_df['capability_score']), 1000)

# Calculate the fitted Gamma PDF
shape_gamma, loc_gamma, scale_gamma = stats.gamma.fit(mitre_groups_df['capability_score'])
gamma_pdf = stats.gamma.pdf(x, shape_gamma, loc=loc_gamma, scale=scale_gamma)

# Calculate the fitted Weibull PDF
shape_weibull, loc_weibull, scale_weibull = stats.weibull_min.fit(mitre_groups_df['capability_score'])
weibull_pdf = stats.weibull_min.pdf(x, shape_weibull, loc=loc_weibull, scale=scale_weibull)

# Plot the histogram and both fitted distributions
plt.figure(figsize=(10, 6))

# Plot histogram with density normalization
plt.hist(mitre_groups_df['capability_score'], bins=20, alpha=0.6, color='b', density=True, label='Histogram')

# Plot Gamma PDF
plt.plot(x, gamma_pdf, 'r-', lw=2, label='Gamma Fit')

# Plot Weibull PDF
plt.plot(x, weibull_pdf, 'g-', lw=2, label='Weibull Fit')

# Add titles and labels
plt.title('Histogram of Capability Score with Gamma and Weibull Fits')
plt.xlabel('Capability Score')
plt.ylabel('Density')

# Show the legend
plt.legend()

# Display the plot
plt.show()

#graph 6 - pre vs post comparison

# Pre-normalized capability score
mitre_groups_df['pre_normalized_capability_score'] = np.sqrt(
    mitre_groups_df['totalTechniques']**2 +
    mitre_groups_df['totalTactics']**2 +
    mitre_groups_df['totalSoftware']**2
)

# Plot histograms for pre-normalized and normalized capability scores
plt.figure(figsize=(12, 6))

# Histogram for pre-normalized capability score
plt.subplot(1, 2, 1)
plt.hist(mitre_groups_df['pre_normalized_capability_score'], bins=20, alpha=0.7, color='blue', density=True, label='Pre-Normalized')
plt.title('Pre-Normalized Capability Score')
plt.xlabel('Capability Score')
plt.ylabel('Density')

# Histogram for normalized capability score
plt.subplot(1, 2, 2)
plt.hist(mitre_groups_df['capability_score'], bins=20, alpha=0.7, color='green', density=True, label='Normalized')
plt.title('Normalized Capability Score')
plt.xlabel('Capability Score')
plt.ylabel('Density')

# Display the plots
plt.tight_layout()
plt.show()


# Box Plot (without different colors for each type)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Type', y='capability_score', data=mitre_groups_df, color='skyblue')
plt.title('Box Plot of Capability Score by Group Type')
plt.xlabel('Group Type')
plt.ylabel('Capability Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Violin Plot (without different colors for each type)
plt.figure(figsize=(10, 6))
sns.violinplot(x='Type', y='capability_score', data=mitre_groups_df, color='skyblue')
plt.title('Violin Plot of Capability Score by Group Type')
plt.xlabel('Group Type')
plt.ylabel('Capability Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# correleation matrix
# Select the relevant columns for the correlation matrix
correlation_columns = ['totalTactics', 'totalTechniques', 'totalSoftware', 'total_CVE', 'capability_score']

# Calculate the correlation matrix
correlation_matrix = mitre_groups_df[correlation_columns].corr()

# Visualize the correlation matrix using a heatmap
plt.figure(figsize=(10, 6))

# Plot the heatmap with annotations for the correlation values
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f")

# Add a title
plt.title('Correlation Matrix of Tactics, Techniques, Software, CVEs, and Capability Score')

# Display the heatmap
plt.tight_layout()
plt.show()

#comaprison graph

mitre_groups_df = pd.read_excel(file_path, sheet_name='MITRE ATT&CK Groups')
risk_table_df = pd.read_excel(file_path, sheet_name='Risk Table')

# Merge the 'capability' and 'Type' columns from 'mitre_groups_df' into the 'risk_table_df' based on 'Group'
merged_df = pd.merge(risk_table_df, mitre_groups_df[['Group', 'capability', 'Type']], on='Group', how='left')

# Group the data by 'overall_risk_rank', 'capability', and 'Type' to get the counts
grouped_data = merged_df.groupby(['overall_risk_rank', 'capability', 'Type']).size().unstack(fill_value=0)

# Plot the horizontal stacked bar graph
plt.figure(figsize=(12, 6))

grouped_data.plot(kind='barh', stacked=True, color=['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd'], ax=plt.gca())
plt.title('Combined Influence of Group Types and Capability Levels on Risks')
plt.ylabel('Risk Level')
plt.xlabel('Number of Groups')

# Move the legend to the right side and avoid overlap
plt.legend(title='Group Type', bbox_to_anchor=(1.05, 1), loc='upper left')

# Display the plot
plt.tight_layout()
plt.show()