#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Credit Card Statement Analyzer
Extracts and analyzes data from password-protected PDF credit card statements
"""

import PyPDF2
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import sys

def extract_pdf_text(pdf_path, password):
    """Extract text from password-protected PDF with improved error handling"""
    try:
        with open(pdf_path, 'rb') as file:
            # Try different PDF readers
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    print("PDF is encrypted, attempting to decrypt...")
                    try:
                        # Try to decrypt with the password
                        result = pdf_reader.decrypt(password)
                        print(f"Decryption result: {result}")
                        if result == 0:
                            print("Failed to decrypt PDF with provided password")
                            return None
                    except Exception as decrypt_error:
                        print(f"Decryption error: {decrypt_error}")
                        return None
                
                # Extract text from all pages
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += f"--- Page {page_num + 1} ---\n"
                        text += page_text + "\n\n"
                        print(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                    except Exception as page_error:
                        print(f"Error extracting text from page {page_num + 1}: {page_error}")
                        continue
                
                return text
                
            except Exception as reader_error:
                print(f"PyPDF2 error: {reader_error}")
                
                # Try alternative approach with different parameters
                try:
                    print("Trying alternative PDF reading approach...")
                    file.seek(0)  # Reset file pointer
                    pdf_reader = PyPDF2.PdfReader(file, strict=False)
                    
                    if pdf_reader.is_encrypted:
                        pdf_reader.decrypt(password)
                    
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    return text
                    
                except Exception as alt_error:
                    print(f"Alternative approach failed: {alt_error}")
                    return None
                    
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def debug_pdf_content(pdf_path, password):
    """Debug PDF content to understand structure"""
    try:
        import pdfplumber
        print("Trying with pdfplumber...")
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"PDF opened successfully with pdfplumber. Pages: {len(pdf.pages)}")
            
            text = ""
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {page_num + 1} ---\n"
                    text += page_text + "\n\n"
                    print(f"Page {page_num + 1}: {len(page_text)} characters")
            
            return text
            
    except ImportError:
        print("pdfplumber not available, installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
        
        # Try again after installation
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path, password=password) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            print(f"pdfplumber also failed: {e}")
            return None
            
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return None

def parse_transactions(text):
    """Parse transactions from extracted text with enhanced patterns"""
    transactions = []
    
    # Print first 2000 characters for debugging
    print("First 2000 characters of extracted text:")
    print("=" * 50)
    print(text[:2000])
    print("=" * 50)
    
    # Enhanced patterns for Taiwanese bank statements
    patterns = [
        # Pattern for MM/DD format with Chinese description
        r'(\d{2}/\d{2})\s+([\u4e00-\u9fff\w\s\-\*\.]+?)\s+([\d,]+\.?\d*)',
        # Pattern for YYYY/MM/DD format
        r'(\d{4}/\d{2}/\d{2})\s+([\u4e00-\u9fff\w\s\-\*\.]+?)\s+([\d,]+\.?\d*)',
        # Pattern with transaction codes
        r'(\d{2}/\d{2})\s+(\d+)\s+([\u4e00-\u9fff\w\s\-\*\.]+?)\s+([\d,]+\.?\d*)',
        # Pattern for transactions with negative amounts
        r'(\d{2}/\d{2})\s+([\u4e00-\u9fff\w\s\-\*\.]+?)\s+\-?([\d,]+\.?\d*)',
        # Generic pattern for any transaction-like data
        r'(\d{1,2}/\d{1,2})\s+(.+?)\s+([\d,]+\.?\d*)',
        # Pattern with extra spaces
        r'(\d{2}/\d{2})\s{2,}([\u4e00-\u9fff\w\s\-\*\.]+?)\s{2,}([\d,]+\.?\d*)',
    ]
    
    for pattern_num, pattern in enumerate(patterns, 1):
        print(f"Trying pattern {pattern_num}: {pattern}")
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        print(f"Found {len(matches)} matches with pattern {pattern_num}")
        
        for match in matches:
            try:
                if len(match) >= 3:
                    date_str = match[0]
                    description = match[-2].strip()  # Second to last element
                    amount_str = match[-1].strip()   # Last element
                    
                    # Clean up amount string
                    amount_str = re.sub(r'[^\d,.]', '', amount_str)
                    if amount_str:
                        amount = float(amount_str.replace(',', ''))
                        
                        transaction = {
                            'date': date_str,
                            'description': description,
                            'amount': amount
                        }
                        transactions.append(transaction)
                        print(f"Added transaction: {date_str} | {description[:30]}... | {amount}")
                        
            except (ValueError, IndexError) as e:
                print(f"Error parsing match {match}: {e}")
                continue
    
    # Remove duplicates
    unique_transactions = []
    seen = set()
    for t in transactions:
        key = (t['date'], t['description'], t['amount'])
        if key not in seen:
            seen.add(key)
            unique_transactions.append(t)
    
    print(f"Total unique transactions found: {len(unique_transactions)}")
    return unique_transactions

def categorize_transactions(transactions):
    """Categorize transactions based on description"""
    categories = {
        'Food & Dining': ['餐廳', '食', '飲', '麥當勞', '星巴克', '便利商店', '超市', '7-11', '全家', '美食', '餐', '飯', '咖啡'],
        'Transportation': ['捷運', '公車', '計程車', '加油', '停車', 'UBER', '油站', '交通', '高鐵', '台鐵', '客運'],
        'Shopping': ['百貨', '購物', '服飾', '電器', '網購', '商城', 'AMAZON', '買', '購', '商店', '市場'],
        'Entertainment': ['電影', '遊戲', '娛樂', 'KTV', '健身', '運動', '書店', '音樂'],
        'Bills & Utilities': ['電費', '水費', '瓦斯', '電信', '保險', '銀行', '費用', '帳單', '繳費'],
        'Healthcare': ['醫院', '診所', '藥局', '健康', '醫療', '牙科', '眼科'],
        'Education': ['學校', '補習', '書店', '文具', '教育', '學費'],
        'Travel': ['飯店', '機票', '旅遊', '住宿', '旅行', 'HOTEL'],
        'Cash/ATM': ['提款', 'ATM', '現金', '轉帳', '匯款'],
        'Other': []
    }
    
    for transaction in transactions:
        description = transaction['description']
        categorized = False
        
        for category, keywords in categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description:
                    transaction['category'] = category
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            transaction['category'] = 'Other'
    
    return transactions

def analyze_spending(transactions):
    """Analyze spending patterns"""
    df = pd.DataFrame(transactions)
    
    if df.empty:
        print("No transactions found to analyze")
        return None, None
    
    print(f"Analyzing {len(df)} transactions...")
    
    # Convert amount to absolute value for spending analysis
    df['amount_abs'] = df['amount'].abs()
    
    # Basic statistics
    total_spending = df['amount_abs'].sum()
    avg_transaction = df['amount_abs'].mean()
    num_transactions = len(df)
    
    # Category analysis
    category_spending = df.groupby('category')['amount_abs'].sum().sort_values(ascending=False)
    
    # Create analysis report
    analysis = {
        'total_spending': total_spending,
        'average_transaction': avg_transaction,
        'number_of_transactions': num_transactions,
        'category_breakdown': category_spending.to_dict(),
        'top_transactions': df.nlargest(5, 'amount_abs')[['description', 'amount', 'category']].to_dict('records'),
        'transactions_by_category': df.groupby('category').size().to_dict()
    }
    
    return analysis, df

def create_visualizations(df, analysis):
    """Create spending visualization charts"""
    try:
        plt.style.use('default')  # Use default style instead of seaborn
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Category spending pie chart
        category_data = pd.Series(analysis['category_breakdown'])
        axes[0, 0].pie(category_data.values, labels=category_data.index, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Spending by Category')
        
        # Category spending bar chart
        category_data.plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Spending Amount by Category')
        axes[0, 1].set_xlabel('Category')
        axes[0, 1].set_ylabel('Amount (NT$)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Transaction amount distribution
        axes[1, 0].hist(df['amount_abs'], bins=20, edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('Transaction Amount Distribution')
        axes[1, 0].set_xlabel('Amount (NT$)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Transaction count by category
        cat_counts = pd.Series(analysis['transactions_by_category'])
        cat_counts.plot(kind='bar', ax=axes[1, 1])
        axes[1, 1].set_title('Number of Transactions by Category')
        axes[1, 1].set_xlabel('Category')
        axes[1, 1].set_ylabel('Number of Transactions')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('credit_card_analysis.png', dpi=300, bbox_inches='tight')
        print("Visualization saved as 'credit_card_analysis.png'")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")

def generate_report(analysis):
    """Generate a comprehensive analysis report"""
    report = f"""
====================================
CREDIT CARD SPENDING ANALYSIS REPORT
====================================

SUMMARY STATISTICS:
- Total Spending: NT$ {analysis['total_spending']:,.2f}
- Number of Transactions: {analysis['number_of_transactions']}
- Average Transaction Amount: NT$ {analysis['average_transaction']:,.2f}

SPENDING BY CATEGORY:
"""
    
    for category, amount in analysis['category_breakdown'].items():
        percentage = (amount / analysis['total_spending']) * 100
        count = analysis['transactions_by_category'].get(category, 0)
        report += f"- {category}: NT$ {amount:,.2f} ({percentage:.1f}%) - {count} transactions\n"
    
    report += f"""
TOP 5 TRANSACTIONS:
"""
    
    for i, transaction in enumerate(analysis['top_transactions'], 1):
        report += f"{i}. {transaction['description']}: NT$ {transaction['amount']:,.2f} ({transaction['category']})\n"
    
    report += f"""

INSIGHTS & RECOMMENDATIONS:
- Largest spending category: {max(analysis['category_breakdown'], key=analysis['category_breakdown'].get)}
- Most frequent transaction category: {max(analysis['transactions_by_category'], key=analysis['transactions_by_category'].get)}
- Consider setting budgets for high-spending categories
- Review recurring transactions for potential savings
- Monitor transaction patterns for unusual activity

SPENDING BREAKDOWN:
"""
    
    for category in sorted(analysis['category_breakdown'].keys()):
        amount = analysis['category_breakdown'][category]
        count = analysis['transactions_by_category'].get(category, 0)
        avg_per_transaction = amount / count if count > 0 else 0
        report += f"- {category}: {count} transactions, avg NT$ {avg_per_transaction:.2f} per transaction\n"
    
    return report

def main():
    """Main function to run the analysis"""
    print("=" * 60)
    print("The Pocket Company by Accucrazy")
    print("Credit Card Statement PDF Analyzer")
    print("=" * 60)
    
    # SECURITY: Use environment variables for sensitive data
    import os
    
    pdf_path = os.getenv('PDF_PATH', 'your_bank_statement.pdf')
    password = os.getenv('PDF_PASSWORD')
    
    # Check if using default values (not secure for production)
    if not password:
        print("⚠️  ERROR: PDF_PASSWORD environment variable not set.")
        print("For security, set the environment variable:")
        print("   Windows: set PDF_PASSWORD=your_actual_password")
        print("   Linux/Mac: export PDF_PASSWORD=your_actual_password")
        print("\nExample usage:")
        print("   set PDF_PASSWORD=12345678")
        print("   python extract_pdf_data.py")
        return
    
    if pdf_path == 'your_bank_statement.pdf':
        print("⚠️  WARNING: Using default PDF path. Set PDF_PATH environment variable.")
        print("   Windows: set PDF_PATH=your_statement.pdf")
        print("   Linux/Mac: export PDF_PATH=your_statement.pdf")
        # Don't return here, use default filename
        pdf_path = "bank_statement.pdf"
    
    print(f"\n📄 PDF Path: {pdf_path}")
    print("🔐 Password: [PROTECTED]")
    print("Starting PDF Credit Card Analysis...")
    
    print("\nAttempting to extract text from PDF...")
    text = extract_pdf_text(pdf_path, password)
    
    if not text:
        print("PyPDF2 failed, trying alternative method...")
        text = debug_pdf_content(pdf_path, password)
    
    if not text:
        print("Failed to extract text from PDF using all available methods")
        print("Please check:")
        print("1. PDF file exists and is readable")
        print("2. Password is correct")
        print("3. PDF is not corrupted")
        return
    
    print(f"\nSuccessfully extracted {len(text)} characters from PDF")
    
    print("\nParsing transactions...")
    transactions = parse_transactions(text)
    
    if not transactions:
        print("No transactions found. The PDF format might not match expected patterns.")
        # Save extracted text for manual review
        with open('extracted_text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Extracted text saved to 'extracted_text.txt' for manual review")
        return
    
    print(f"\nFound {len(transactions)} transactions")
    
    print("Categorizing transactions...")
    transactions = categorize_transactions(transactions)
    
    print("Analyzing spending patterns...")
    analysis, df = analyze_spending(transactions)
    
    if analysis:
        print("Generating visualizations...")
        create_visualizations(df, analysis)
        
        print("Generating report...")
        report = generate_report(analysis)
        print(report)
        
        # Save report to file
        with open('credit_card_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save transactions to CSV
        df.to_csv('transactions.csv', index=False, encoding='utf-8')
        
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE!")
        print("="*50)
        print("Files saved:")
        print("- credit_card_analysis.png (visualization charts)")
        print("- credit_card_analysis_report.txt (detailed report)")
        print("- transactions.csv (transaction data)")
        print("="*50)
    else:
        print("Analysis failed - no valid transactions found")

if __name__ == "__main__":
    main() 