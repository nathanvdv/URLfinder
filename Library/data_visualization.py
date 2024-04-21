import matplotlib.pyplot as plt
import seaborn as sns

def visualize_missing_data(df):
    """Generate a heatmap showing missing data in the DataFrame."""
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title('Heatmap of Missing Data')
    plt.show()

def visualize_municipalities(df):
    """Bar plot of the top 10 municipalities by number of entities."""
    municipality_counts = df['Municipality'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=municipality_counts, y=municipality_counts.index)
    plt.xlabel('Number of Entities')
    plt.ylabel('Municipality')
    plt.title('Top 10 Municipalities by Number of Entities')
    plt.show()

def visualize_nace_codes(df, top_n=20):
    """Bar plot of the top N NACE codes by frequency."""
    nace_counts = df['ActivityNACE'].value_counts().head(top_n)
    plt.figure(figsize=(20, 6))
    sns.barplot(x=nace_counts.index, y=nace_counts, color='skyblue')
    plt.xlabel('NACE Code')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} NACE Codes by Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualize_url_duplicates(df):
    """Identify and plot the frequency of duplicated URLs."""
    duplicate_counts = df['URL'].value_counts()
    duplicates_only = duplicate_counts[duplicate_counts > 1]
    if duplicates_only.empty:
        print("No duplicate URLs found.")
        return
    plt.figure(figsize=(10, 6))
    sns.barplot(x=duplicates_only.index, y=duplicates_only, palette='viridis')
    plt.xlabel('URL')
    plt.ylabel('Count')
    plt.title('Frequency of Duplicate URLs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
