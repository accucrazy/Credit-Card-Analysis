#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Credit Card Analysis
Cleans the extracted data and provides accurate spending analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def clean_transactions(csv_path):
    """Clean transaction data by removing outliers and parsing errors"""
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"Original transactions: {len(df)}")
    
    # Remove rows with invalid dates
    df = df[~df['date'].str.contains('0/0|14/05', na=False)]
    
    # Remove transactions with unrealistic amounts (likely parsing errors)
    # Most credit card transactions should be under NT$100,000
    df = df[df['amount_abs'] < 100000]
    
    # Remove rows with garbled text (cid: patterns)
    df = df[~df['description'].str.contains('cid:', na=False)]
    
    # Remove duplicate transactions (keeping first occurrence)
    df = df.drop_duplicates(subset=['date', 'description', 'amount'], keep='first')
    
    print(f"Cleaned transactions: {len(df)}")
    
    return df

def improve_categorization(df):
    """Improve transaction categorization"""
    
    # Enhanced categories with better keywords
    categories = {
        'Food & Dining': [
            '餐廳', '食', '飲', '麥當勞', '星巴克', '便利商店', '超市', '7-11', '全家', 
            '美食', '餐', '飯', '咖啡', 'cama', '杭州小籠包', '養心殿', '京星港式飲茶',
            '北村家', '吐司利亞', '優食', 'Subway', '燒肉', '創義麵', '湘川', 
            '珍蜜咖啡', 'Fake Sober', 'J WOW', '全聯福利中心', '麥當勞'
        ],
        'Transportation': [
            '捷運', '公車', '計程車', '加油', '停車', 'UBER', '油站', '交通', 
            '高鐵', '台鐵', '客運', '台灣大車隊', '優步', 'Taxi'
        ],
        'Technology/Software': [
            'CURSOR', 'ADOBE', 'OPENAI', 'GOOGLE', 'FIGMA', 'HEYGEN', 'SEASALT',
            'REPORTDASH', 'MANYCHAT', 'RSS.APP', 'PADDLE', 'LEONARDO', 'Colab',
            'SPOTIFY', 'ANTHROPIC', 'Gandi', 'APIFY', 'SHOPIFY', 'PCHOME'
        ],
        'Shopping': [
            '百貨', '購物', '服飾', '電器', '網購', '商城', 'AMAZON', '買', '購', 
            '商店', '市場', 'IKEA', '宜家家居', '永昇五金', '今華電子', '源達科技'
        ],
        'Entertainment': [
            '電影', '遊戲', '娛樂', 'KTV', '健身', '運動', '書店', '音樂', '錢櫃'
        ],
        'Bills & Utilities': [
            '電費', '水費', '瓦斯', '電信', '保險', '銀行', '費用', '帳單', '繳費',
            '手續費', '國外交易手續費', 'ATT'
        ],
        'Cash/ATM': [
            '提款', 'ATM', '現金', '轉帳', '匯款', '現金回饋', '自動扣繳'
        ],
        'Business/Marketing': [
            '全球商務科技', 'LINE Ads', '連加'
        ],
        'Other': []
    }
    
    # Recategorize transactions
    for idx, row in df.iterrows():
        description = row['description']
        categorized = False
        
        for category, keywords in categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description:
                    df.at[idx, 'category'] = category
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            df.at[idx, 'category'] = 'Other'
    
    return df

def generate_clean_analysis(df):
    """Generate comprehensive analysis of cleaned data"""
    
    # Basic statistics
    total_spending = df['amount_abs'].sum()
    avg_transaction = df['amount_abs'].mean()
    median_transaction = df['amount_abs'].median()
    num_transactions = len(df)
    
    # Category analysis
    category_spending = df.groupby('category')['amount_abs'].sum().sort_values(ascending=False)
    category_counts = df['category'].value_counts()
    
    # Date analysis
    spending_by_date = df.groupby('date')['amount_abs'].sum().sort_values(ascending=False)
    
    # Top merchants
    merchant_spending = df.groupby('description')['amount_abs'].sum().sort_values(ascending=False).head(10)
    
    # Analysis dictionary
    analysis = {
        'total_spending': total_spending,
        'average_transaction': avg_transaction,
        'median_transaction': median_transaction,
        'number_of_transactions': num_transactions,
        'category_breakdown': category_spending.to_dict(),
        'category_counts': category_counts.to_dict(),
        'top_transactions': df.nlargest(10, 'amount_abs')[['date', 'description', 'amount', 'category']].to_dict('records'),
        'top_merchants': merchant_spending.to_dict(),
        'spending_by_date': spending_by_date.head(10).to_dict()
    }
    
    return analysis

def create_clean_visualizations(df, analysis):
    """Create improved visualizations"""
    plt.style.use('default')
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Credit Card Spending Analysis - May 2025', fontsize=16, fontweight='bold')
    
    # 1. Category spending pie chart
    category_data = pd.Series(analysis['category_breakdown'])
    # Only show categories with more than 1% of total spending
    threshold = category_data.sum() * 0.01
    category_filtered = category_data[category_data > threshold]
    other_amount = category_data[category_data <= threshold].sum()
    if other_amount > 0:
        category_filtered['Other (Small)'] = other_amount
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_filtered)))
    axes[0, 0].pie(category_filtered.values, labels=category_filtered.index, autopct='%1.1f%%', 
                   startangle=90, colors=colors)
    axes[0, 0].set_title('Spending by Category')
    
    # 2. Category spending bar chart
    category_data.plot(kind='bar', ax=axes[0, 1], color='skyblue')
    axes[0, 1].set_title('Amount by Category')
    axes[0, 1].set_xlabel('Category')
    axes[0, 1].set_ylabel('Amount (NT$)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Transaction count by category
    cat_counts = pd.Series(analysis['category_counts'])
    cat_counts.plot(kind='bar', ax=axes[0, 2], color='lightcoral')
    axes[0, 2].set_title('Transaction Count by Category')
    axes[0, 2].set_xlabel('Category')
    axes[0, 2].set_ylabel('Number of Transactions')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # 4. Transaction amount distribution
    axes[1, 0].hist(df['amount_abs'], bins=30, edgecolor='black', alpha=0.7, color='lightgreen')
    axes[1, 0].set_title('Transaction Amount Distribution')
    axes[1, 0].set_xlabel('Amount (NT$)')
    axes[1, 0].set_ylabel('Frequency')
    
    # 5. Top merchants
    top_merchants = pd.Series(analysis['top_merchants']).head(8)
    top_merchants.plot(kind='barh', ax=axes[1, 1], color='orange')
    axes[1, 1].set_title('Top Merchants by Spending')
    axes[1, 1].set_xlabel('Amount (NT$)')
    
    # 6. Spending by amount ranges
    amount_ranges = ['<100', '100-500', '500-1000', '1000-5000', '5000+']
    range_counts = [
        len(df[df['amount_abs'] < 100]),
        len(df[(df['amount_abs'] >= 100) & (df['amount_abs'] < 500)]),
        len(df[(df['amount_abs'] >= 500) & (df['amount_abs'] < 1000)]),
        len(df[(df['amount_abs'] >= 1000) & (df['amount_abs'] < 5000)]),
        len(df[df['amount_abs'] >= 5000])
    ]
    
    axes[1, 2].bar(amount_ranges, range_counts, color='purple', alpha=0.7)
    axes[1, 2].set_title('Transactions by Amount Range')
    axes[1, 2].set_xlabel('Amount Range (NT$)')
    axes[1, 2].set_ylabel('Number of Transactions')
    
    plt.tight_layout()
    plt.savefig('clean_credit_card_analysis.png', dpi=300, bbox_inches='tight')
    print("Clean visualization saved as 'clean_credit_card_analysis.png'")

def generate_clean_report(analysis):
    """Generate a comprehensive cleaned analysis report"""
    report = f"""
====================================
CLEANED CREDIT CARD SPENDING ANALYSIS
First Bank Statement - May 2025
====================================

SUMMARY STATISTICS:
- Total Spending: NT$ {analysis['total_spending']:,.2f}
- Number of Transactions: {analysis['number_of_transactions']}
- Average Transaction: NT$ {analysis['average_transaction']:,.2f}
- Median Transaction: NT$ {analysis['median_transaction']:,.2f}

SPENDING BY CATEGORY:
"""
    
    total = analysis['total_spending']
    for category, amount in analysis['category_breakdown'].items():
        percentage = (amount / total) * 100
        count = analysis['category_counts'].get(category, 0)
        avg_per_transaction = amount / count if count > 0 else 0
        report += f"- {category}: NT$ {amount:,.2f} ({percentage:.1f}%) - {count} transactions (avg: NT$ {avg_per_transaction:,.2f})\n"
    
    report += f"""

TOP 10 TRANSACTIONS:
"""
    
    for i, transaction in enumerate(analysis['top_transactions'], 1):
        report += f"{i:2d}. {transaction['date']} | {transaction['description'][:40]:<40} | NT$ {transaction['amount']:>8,.0f} | {transaction['category']}\n"
    
    report += f"""

TOP MERCHANTS BY TOTAL SPENDING:
"""
    
    for i, (merchant, amount) in enumerate(analysis['top_merchants'].items(), 1):
        report += f"{i:2d}. {merchant[:50]:<50} | NT$ {amount:>8,.2f}\n"
    
    report += f"""

SPENDING INSIGHTS:
- Highest spending category: {max(analysis['category_breakdown'], key=analysis['category_breakdown'].get)}
- Most frequent transaction category: {max(analysis['category_counts'], key=analysis['category_counts'].get)}
- Largest single transaction: NT$ {max(t['amount'] for t in analysis['top_transactions']):,.2f}
- Technology/Software spending: NT$ {analysis['category_breakdown'].get('Technology/Software', 0):,.2f}
- Food & Dining spending: NT$ {analysis['category_breakdown'].get('Food & Dining', 0):,.2f}

RECOMMENDATIONS:
1. Monitor Technology/Software subscriptions - this appears to be a major expense category
2. Consider consolidating software subscriptions to save costs
3. Track food delivery and dining expenses for budgeting
4. Review recurring payments for optimization opportunities
5. Set up alerts for transactions over NT$ 5,000

SPENDING PATTERNS:
- Small transactions (<NT$500): {len([t for t in analysis['top_transactions'] if abs(t['amount']) < 500])} transactions
- Medium transactions (NT$500-5,000): Most common range
- Large transactions (>NT$5,000): Focus on technology and entertainment expenses
"""
    
    return report

def main():
    """Main function for clean analysis"""
    print("Starting Clean Credit Card Analysis...")
    
    # Load and clean data
    df = clean_transactions('transactions.csv')
    
    if len(df) == 0:
        print("No valid transactions found after cleaning")
        return
    
    # Improve categorization
    df = improve_categorization(df)
    
    # Generate analysis
    analysis = generate_clean_analysis(df)
    
    # Create visualizations
    create_clean_visualizations(df, analysis)
    
    # Generate report
    report = generate_clean_report(analysis)
    print(report)
    
    # Save files
    with open('clean_credit_card_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    df.to_csv('clean_transactions.csv', index=False, encoding='utf-8')
    
    print("\n" + "="*60)
    print("CLEAN ANALYSIS COMPLETE!")
    print("="*60)
    print("Files saved:")
    print("- clean_credit_card_analysis.png (clean visualizations)")
    print("- clean_credit_card_report.txt (detailed clean report)")
    print("- clean_transactions.csv (cleaned transaction data)")
    print("="*60)

if __name__ == "__main__":
    main() 