# Credit Card Statement PDF Analyzer
**The Pocket Company by Accucrazy**

---

## 📊 **Enterprise SaaS Spending Analysis Tool**

This comprehensive tool extracts and analyzes transaction data from password-protected PDF credit card statements, with a specialized focus on **SaaS service spending analysis** for modern tech companies.

## ✨ **Key Features**

### 🔐 **PDF Processing**
- **PDF Text Extraction**: Decrypts and extracts text from password-protected PDF files
- **Smart Transaction Parsing**: Automatically identifies and parses transaction data
- **Multi-format Support**: Handles various bank statement formats

### 📈 **Advanced Analytics**
- **Smart Categorization**: Categorizes transactions into spending categories (Food, Transportation, Shopping, SaaS, etc.)
- **SaaS-Focused Analysis**: Specialized analysis for enterprise software subscriptions
- **Comprehensive Insights**: Provides detailed spending statistics and optimization recommendations
- **Visual Reports**: Creates professional charts and graphs for spending patterns

### 🎯 **SaaS Specialization**
- **AI/ML Tools Tracking**: Monitors spending on Cursor, OpenAI, Anthropic, etc.
- **Subscription Type Analysis**: Differentiates between usage-based vs monthly subscriptions
- **Cost Optimization**: Provides specific recommendations for SaaS spending optimization
- **Duplicate Detection**: Removes duplicate transactions for accurate analysis

### 💾 **Export Options**
- **Multiple Formats**: Saves analysis results in CSV, PNG, TXT formats
- **Professional Reports**: Generated with company branding
- **Clean Data**: Deduplicated and categorized transaction data

## 🛠 **Requirements**

- Python 3.7 or higher
- Required packages (install using `pip install -r requirements.txt`)

## 📦 **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/credit-card-analyzer.git
   cd credit-card-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your PDF file**: Place your PDF file in the project directory

## 🚀 **Usage**

### **Basic Analysis**
```bash
python extract_pdf_data.py
```

### **SaaS-Focused Analysis**
```bash
python saas_analysis.py
```

### **Clean Data Analysis**
```bash
python clean_analysis.py
```

### **Custom Configuration**
Edit the script parameters:
```python
pdf_path = "your_pdf_file.pdf"
password = "your_password"  # Use environment variable in production
```

## 📁 **Output Files**

### **Comprehensive Analysis**
- `saas_spending_analysis.png` - SaaS-focused visualization charts
- `saas_analysis_report.txt` - Detailed SaaS spending report
- `saas_transactions.csv` - Clean SaaS transaction data

### **General Analysis**
- `credit_card_analysis.png` - General spending visualization
- `credit_card_analysis_report.txt` - Complete spending analysis
- `clean_transactions.csv` - Processed transaction data

## 🏷 **Spending Categories**

### **SaaS Categories**
- **AI/ML Tools**: Cursor, OpenAI, Anthropic, Leonardo AI, HeyGen
- **Design Tools**: Figma, Adobe Creative Suite
- **Development Tools**: ReportDash, GitHub, hosting services
- **Cloud Services**: Google Cloud, AWS, Colab
- **Marketing Tools**: ManyChat, analytics platforms

### **General Categories**
- **Food & Dining**: Restaurants, convenience stores, supermarkets
- **Transportation**: Public transport, ride-sharing, fuel
- **Entertainment**: Movies, games, recreation
- **Shopping**: Retail, electronics, household items
- **Bills & Utilities**: Utilities, insurance, banking fees

## ⚙ **Customization**

### **Adding SaaS Services**
```python
saas_keywords = {
    'Your Category': ['SERVICE_NAME', 'KEYWORD'],
    # Add new categories here
}
```

### **Transaction Pattern Matching**
```python
patterns = [
    r'(\d{2}/\d{2})\s+(.+?)\s+([\d,]+\.?\d*)',
    # Add custom patterns for your bank format
]
```

## 📊 **Sample Analysis Report**

```
================================================
企業 SaaS 服務支出分析報告
第一銀行信用卡帳單 - 2025年5月
The Pocket Company by Accucrazy
================================================

總體概況：
- SaaS 總支出：NT$ 30,476.00
- 使用服務數量：12 個
- 總交易次數：25 筆
- 平均每筆交易：NT$ 1,219.04

前5大 SaaS 服務支出：
1. ReportDash Analytics: NT$ 9,744.00 (32.0%)
2. Cursor AI IDE: NT$ 5,591.00 (18.3%)
3. Figma Design: NT$ 4,357.00 (14.3%)
4. HeyGen Video AI: NT$ 3,331.00 (10.9%)
5. OpenAI (ChatGPT/API): NT$ 2,934.00 (9.6%)
```

## 🔒 **Security & Privacy**

### **Data Protection**
- All processing is done locally
- No data sent to external servers
- Sensitive files excluded from version control

### **Best Practices**
- Use environment variables for passwords
- Delete sensitive files after analysis
- Review `.gitignore` before committing

## 🚫 **Files NOT to Upload to GitHub**

```
# Sensitive files - DO NOT COMMIT
*.pdf                    # Bank statements
*transactions.csv        # Real transaction data
*_report.txt            # Reports with real data
*.png                   # Charts with real data (sample charts OK)
```

## ⚠ **Troubleshooting**

### **Common Issues**
1. **PDF Password Error**: Verify password or use environment variable
2. **No Transactions Found**: Check PDF format compatibility
3. **Encoding Issues**: Ensure UTF-8 system encoding
4. **Font Display**: Install Chinese fonts for proper chart rendering

### **Getting Help**
1. Check extracted text patterns in debug mode
2. Verify regex patterns match your bank format
3. Ensure all dependencies are installed

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add sample data (NOT real financial data)
4. Submit a pull request

## 📄 **License**

This tool is provided for educational and personal use. Ensure compliance with your financial institution's terms of service.

## 🔗 **Company Information**

**The Pocket Company by Accucrazy**
- Specialized in enterprise SaaS spending optimization
- AI-driven financial analysis tools
- Modern tech company cost management solutions

---

⚠️ **Important**: This tool processes sensitive financial data. Always follow data protection best practices and never commit real financial information to version control. 