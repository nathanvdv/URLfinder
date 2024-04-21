import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(df_final_URL):
    # Summary statistics for numerical columns and info
    print(df_final_URL.describe())
    print(df_final_URL.info())

    # Count of non-null values to assess missing data
    print(df_final_URL.count())

    # Frequency of categories in 'Municipality'
    municipality_counts = df_final_URL['Municipality'].value_counts()
    print(municipality_counts.head())  # Top 5 municipalities

    # Visualization: Number of Entities per Municipality (Top 10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=municipality_counts.head(10), y=municipality_counts.head(10).index)
    plt.xlabel('Number of Entities')
    plt.ylabel('Municipality')
    plt.title('Top 10 Municipalities by Number of Entities')
    plt.show()

    # Visualization: Missing Data
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_final_URL.isnull(), cbar=False, cmap='viridis')
    plt.title('Heatmap of Missing Data')
    plt.show()

    # Identifying duplicate entries
    duplicate_counts = df_final_URL['URL'].value_counts()
    duplicates_only = duplicate_counts[duplicate_counts > 1]

    # Print each duplicate entry and its count
    for entry, count in duplicates_only.items():
        print(f"Entry '{entry}' is duplicated {count} times.")

    # Count the total number of duplicates (not just distinct duplicate values)
    total_duplicates = df_final_URL.duplicated(subset='URL', keep=False).sum()
    print(f"\nTotal number of duplicate entries: {total_duplicates}")
