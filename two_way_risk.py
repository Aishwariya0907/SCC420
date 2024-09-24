import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats

# Function to analyze how Type influences inherent_total_risk (One-Way ANOVA)
def analyze_type_anova(data):
    # Remove 'Unknown' 
    filtered_data = data[data['Type'] != 'Unknown']

    # Filter out groups with less than 2 samples
    filtered_data = filtered_data.groupby('Type').filter(lambda x: len(x) > 1)

    # Descriptive Statistics for each Type
    descriptive_stats = filtered_data.groupby('Type')['inherent_total_risk'].describe()
    print("\nDescriptive Statistics for each Type of group(risk score):")
    print(descriptive_stats)

    # Distribution Plot for inherent_total_risk by Type
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Type', y='inherent_total_risk', data=filtered_data)
    plt.title('Distribution of inherent_total_risk by Type')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Perform one-way ANOVA
    anova_res = stats.f_oneway(
        *[filtered_data.loc[filtered_data['Type'] == group, 'inherent_total_risk'] for group in filtered_data['Type'].unique()]
    )

    # Print ANOVA result
    print(f"\nANOVA Result for Type (risk): F-statistic = {anova_res.statistic}, p-value = {anova_res.pvalue}")

    if anova_res.pvalue < 0.05:
        print("\nThe ANOVA result is significant for Type.")

        # Perform Tukey's HSD test
        tukey_result = pairwise_tukeyhsd(endog=filtered_data['inherent_total_risk'],
                                                  groups=filtered_data['Type'],
                                                  alpha=0.05)

        # Extract Tukey HSD results into a DataFrame
        tukey_df = pd.DataFrame(data=tukey_result.summary().data[1:], 
                                                 columns=tukey_result.summary().data[0])

        print("\nTukey HSD Results Table for Type (risk):")
        print(tukey_df)

    else:
        print("\nThe ANOVA result for Type is not significant. No further post-hoc analysis is required.")

# Function to analyze how OriginCountry influences inherent_total_risk 
def analyze_origin_anova(data):
    # Remove 'Unknown' 
    filtered_data = data[data['OriginCountry'] != 'Unknown']

    # Filter out groups with less than 2 samples
    filtered_data = filtered_data.groupby('OriginCountry').filter(lambda x: len(x) > 1)

    # Descriptive Statistics for each OriginCountry
    descriptive_stats_filtered = filtered_data.groupby('OriginCountry')['inherent_total_risk'].describe()
    print("\nDescriptive Statistics for each OriginCountry (risk score):")
    print(descriptive_stats_filtered)

    # Distribution Plot for inherent_total_risk by OriginCountry
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='OriginCountry', y='inherent_total_risk', data=filtered_data)
    plt.title('Distribution of inherent_total_risk by OriginCountry')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Perform one-way ANOVA
    anova_result_filtered = stats.f_oneway(
        *[filtered_data.loc[filtered_data['OriginCountry'] == group, 'inherent_total_risk'] for group in filtered_data['OriginCountry'].unique()]
    )

    # Print ANOVA result 
    print(f"\nANOVA Result for OriginCountry: F-statistic = {anova_result_filtered.statistic}, p-value = {anova_result_filtered.pvalue}")

    if anova_result_filtered.pvalue < 0.05:
        print("\nThe ANOVA result is significant for OriginCountry.")

        # Perform Tukey's HSD test
        tukey_result_filtered = pairwise_tukeyhsd(endog=filtered_data['inherent_total_risk'],
                                                  groups=filtered_data['OriginCountry'],
                                                  alpha=0.05)

        # Extract Tukey HSD results into a DataFrame
        tukey_summary_filtered_df = pd.DataFrame(data=tukey_result_filtered.summary().data[1:], 
                                                 columns=tukey_result_filtered.summary().data[0])

        print("\nTukey HSD Results Table for OriginCountry (after filtering):")
        print(tukey_summary_filtered_df)

    else:
        print("\nThe ANOVA result for OriginCountry is not significant. No further post-hoc analysis is required.")
    
    true_count = tukey_summary_filtered_df['reject'].sum()
    total_comparisons = len(tukey_summary_filtered_df)

    # Print the total number of comparisons and how many were significant
    print(f"\nTotal number of comparisons: {total_comparisons}")
    print(f"Number of significant comparisons (True): {true_count}")

# Function to perform two-way ANOVA 
def analyze_type_origin_twoway_anova(data):
    # Remove 'Unknown' 
    filtered_data = data[(data['Type'] != 'Unknown') & (data['OriginCountry'] != 'Unknown')]

    # Ensure both Type and OriginCountry are treated as strings
    filtered_data['Type'] = filtered_data['Type'].astype(str)
    filtered_data['OriginCountry'] = filtered_data['OriginCountry'].astype(str)

    # Create a combined factor for Type and OriginCountry interaction
    filtered_data['Type_Origin_Interaction'] = filtered_data['Type'] + ' + ' + filtered_data['OriginCountry']

    # Two-Way ANOVA
    model = ols('inherent_total_risk ~ C(Type) + C(OriginCountry) + C(Type):C(OriginCountry)', data=filtered_data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    # Print the two-way ANOVA table
    print("\nTwo-Way ANOVA Table for risk score (Type + OriginCountry):")
    print(anova_table)

    # Check if the interaction effect is significant
    if anova_table.loc['C(Type):C(OriginCountry)', 'PR(>F)'] < 0.05:
        print("\nThe interaction effect between Type and OriginCountry is significant.")
    else:
        print("\nThe interaction effect between Type and OriginCountry is not significant.")

    # Perform Tukey HSD test on the combined Type_Origin interaction
    tukey_result_interaction = pairwise_tukeyhsd(endog=filtered_data['inherent_total_risk'],
                                                 groups=filtered_data['Type_Origin_Interaction'],
                                                 alpha=0.05)

    # Print Tukey HSD results for the interaction between Type and OriginCountry
    print("\nTukey HSD Results for the interaction between Type and OriginCountry:")
    tukey_summary_interaction_df = pd.DataFrame(data=tukey_result_interaction.summary().data[1:], 
                                                columns=tukey_result_interaction.summary().data[0])
    print(tukey_summary_interaction_df)

    # Count the number of significant comparisons
    true_count_interaction = tukey_summary_interaction_df['reject'].sum()
    total_comparisons_interaction = len(tukey_summary_interaction_df)

    # Print the total number of comparisons and how many were significant
    print(f"\nTotal number of comparisons for the interaction: {total_comparisons_interaction}")
    print(f"Number of significant comparisons (True) for the interaction: {true_count_interaction}")


# Load data
file_path = 'mitre_attack_analysis1.xlsx'  
data = pd.read_excel(file_path)

mitre_groups_df = pd.read_excel(file_path, sheet_name='MITRE ATT&CK Groups')
risk_table_df = pd.read_excel(file_path, sheet_name='Risk Table')

# Merge the two datasets 
merged_data = pd.merge(mitre_groups_df[['Group', 'Type', 'OriginCountry']], risk_table_df[['Group', 'inherent_total_risk']], on='Group')

# Ensure that 'inherent_total_risk' is numeric and delete missing values
merged_data['inherent_total_risk'] = pd.to_numeric(merged_data['inherent_total_risk'], errors='coerce')
merged_data = merged_data.dropna(subset=['inherent_total_risk'])

# Perform one-way ANOVA for Type
analyze_type_anova(merged_data)

# Perform one-way ANOVA for OriginCountry
analyze_origin_anova(merged_data)

# Perform two-way ANOVA on Type and OriginCountry 
analyze_type_origin_twoway_anova(merged_data)
