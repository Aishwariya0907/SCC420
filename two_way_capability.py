import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats

# Function to analyze how Type influences capability_score (One-Way ANOVA)
def analyze_type_anova_capability(data):
    # Remove 'Unknown' 
    filtered_data = data[data['Type'] != 'Unknown']

    # Filter out groups with less than 2 samples
    filtered_data = filtered_data.groupby('Type').filter(lambda x: len(x) > 1)

    # Descriptive Statistics for each Type
    descriptive_stats = filtered_data.groupby('Type')['capability_score'].describe()
    print("\nDescriptive Statistics for each Type of group (capability score):")
    print(descriptive_stats)

    # Distribution Plot for capability_score by Type
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Type', y='capability_score', data=filtered_data,color='skyblue')
    plt.title('Distribution of capability_score by Type')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Perform one-way ANOVA
    anova_res = stats.f_oneway(
        *[filtered_data.loc[filtered_data['Type'] == group, 'capability_score'] for group in filtered_data['Type'].unique()]
    )

    # Print ANOVA result
    print(f"\nANOVA Result for Type (capability score): F-statistic = {anova_res.statistic}, p-value = {anova_res.pvalue}")

    if anova_res.pvalue < 0.05:
        print("\nThe ANOVA result is significant for Type.")

        # Perform Tukey's HSD test
        tukey_result = pairwise_tukeyhsd(endog=filtered_data['capability_score'],
                                         groups=filtered_data['Type'],
                                         alpha=0.05)

        # Extract Tukey HSD results into a DataFrame
        tukey_df = pd.DataFrame(data=tukey_result.summary().data[1:], 
                                                 columns=tukey_result.summary().data[0])

        print("\nTukey HSD Results Table for Type (capability score):")
        print(tukey_df)

    else:
        print("\nThe ANOVA result for Type is not significant. No further post-hoc analysis is required.")

# Function to analyze how OriginCountry influences capability_score 
def analyze_origin_anova_capability(data):
    # Remove 'Unknown' 
    filtered_data = data[data['OriginCountry'] != 'Unknown']

    # Filter out groups with less than 2 samples
    filtered_data = filtered_data.groupby('OriginCountry').filter(lambda x: len(x) > 1)

    # Descriptive Statistics for each OriginCountry
    descriptive_stats_filtered = filtered_data.groupby('OriginCountry')['capability_score'].describe()
    print("\nDescriptive Statistics for each OriginCountry (capability score):")
    print(descriptive_stats_filtered)

    # Distribution Plot for capability_score by OriginCountry
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='OriginCountry', y='capability_score', data=filtered_data,color='skyblue')
    plt.title('Distribution of capability_score by OriginCountry')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Perform one-way ANOVA
    anova_result_filtered = stats.f_oneway(
        *[filtered_data.loc[filtered_data['OriginCountry'] == group, 'capability_score'] for group in filtered_data['OriginCountry'].unique()]
    )

    # Print ANOVA result 
    print(f"\nANOVA Result for OriginCountry (capability score): F-statistic = {anova_result_filtered.statistic}, p-value = {anova_result_filtered.pvalue}")

    if anova_result_filtered.pvalue < 0.05:
        print("\nThe ANOVA result is significant for OriginCountry.")

        # Perform Tukey's HSD test
        tukey_result_filtered = pairwise_tukeyhsd(endog=filtered_data['capability_score'],
                                                  groups=filtered_data['OriginCountry'],
                                                  alpha=0.05)

        # Extract Tukey HSD results into a DataFrame
        tukey_summary_filtered_df = pd.DataFrame(data=tukey_result_filtered.summary().data[1:], 
                                                 columns=tukey_result_filtered.summary().data[0])

        print("\nTukey HSD Results Table for OriginCountry (capability score):")
        print(tukey_summary_filtered_df)

        # Count the number of significant comparisons
        true_count = tukey_summary_filtered_df['reject'].sum()
        total_comparisons = len(tukey_summary_filtered_df)

        # Print the total number of comparisons and how many were significant
        print(f"\nTotal number of comparisons: {total_comparisons}")
        print(f"Number of significant comparisons (True): {true_count}")
    else:
        print("\nThe ANOVA result for OriginCountry is not significant. No further post-hoc analysis is required.")

# Function to perform two-way ANOVA for capability_score (Type + OriginCountry)
def analyze_type_origin_twoway_anova_capability(data):
    # Remove 'Unknown' 
    filtered_data = data[(data['Type'] != 'Unknown') & (data['OriginCountry'] != 'Unknown')]

    # Ensure both Type and OriginCountry are treated as strings
    filtered_data['Type'] = filtered_data['Type'].astype(str)
    filtered_data['OriginCountry'] = filtered_data['OriginCountry'].astype(str)

    # Create a combined factor for Type and OriginCountry interaction
    filtered_data['Type_Origin_Interaction'] = filtered_data['Type'] + ' + ' + filtered_data['OriginCountry']

    # Two-Way ANOVA
    model = ols('capability_score ~ C(Type) + C(OriginCountry) + C(Type):C(OriginCountry)', data=filtered_data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    # Print the two-way ANOVA table
    print("\nTwo-Way ANOVA Table for capability score (Type + OriginCountry):")
    print(anova_table)

    # Check if the interaction effect is significant
    if anova_table.loc['C(Type):C(OriginCountry)', 'PR(>F)'] < 0.05:
        print("\nThe interaction effect between Type and OriginCountry is significant.")

        # Perform Tukey HSD test on the combined Type_Origin interaction
        tukey_result_interaction = pairwise_tukeyhsd(endog=filtered_data['capability_score'],
                                                     groups=filtered_data['Type_Origin_Interaction'],
                                                     alpha=0.05)

        # Print Tukey HSD results for the interaction between Type and OriginCountry
        print("\nTukey HSD Results for the interaction between Type and OriginCountry (capability score):")
        tukey_summary_interaction_df = pd.DataFrame(data=tukey_result_interaction.summary().data[1:], 
                                                    columns=tukey_result_interaction.summary().data[0])
        print(tukey_summary_interaction_df)

        # Count the number of significant comparisons
        true_count_interaction = tukey_summary_interaction_df['reject'].sum()
        total_comparisons_interaction = len(tukey_summary_interaction_df)

        # Print the total number of comparisons and how many were significant
        print(f"\nTotal number of comparisons for the interaction: {total_comparisons_interaction}")
        print(f"Number of significant comparisons (True) for the interaction: {true_count_interaction}")

    else:
        print("\nThe interaction effect between Type and OriginCountry is not significant. No further post-hoc analysis is required.")

# Load data
file_path = 'mitre_attack_analysis1.xlsx'  
data = pd.read_excel(file_path)

mitre_groups_df = pd.read_excel(file_path, sheet_name='MITRE ATT&CK Groups')
capability_table_df = pd.read_excel(file_path, sheet_name='Capability Table')  # Assuming this is the sheet for capability_score

# Merge the two datasets 
merged_data = pd.merge(mitre_groups_df[['Group', 'Type', 'OriginCountry','capability_score']], 
                       capability_table_df[['Group']], 
                       on='Group')

# Ensure that 'capability_score' is numeric and delete missing values
merged_data['capability_score'] = pd.to_numeric(merged_data['capability_score'], errors='coerce')
merged_data = merged_data.dropna(subset=['capability_score'])

# Perform one-way ANOVA for Type on capability_score
analyze_type_anova_capability(merged_data)

# Perform one-way ANOVA for OriginCountry on capability_score
analyze_origin_anova_capability(merged_data)

# Perform two-way ANOVA on Type and OriginCountry for capability_score
analyze_type_origin_twoway_anova_capability(merged_data)
