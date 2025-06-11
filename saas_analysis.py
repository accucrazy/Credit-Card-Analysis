#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企業 SaaS 服務支出分析
專門分析 Cursor、OpenAI 等技術工具的支出
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from collections import defaultdict

def load_and_filter_saas_data(csv_path):
    """載入並篩選 SaaS 相關交易"""
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # SaaS 服務關鍵字
    saas_keywords = {
        'AI/ML Tools': ['CURSOR', 'OPENAI', 'ANTHROPIC', 'LEONARDO', 'HEYGEN'],
        'Design Tools': ['FIGMA', 'ADOBE'],
        'Cloud Services': ['GOOGLE', 'Colab'],
        'Development Tools': ['REPORTDASH', 'Gandi'],
        'Marketing Tools': ['MANYCHAT', 'RSS.APP', 'SEASALT'],
        'Media': ['SPOTIFY', 'PADDLE']
    }
    
    # 篩選 SaaS 相關交易
    saas_transactions = []
    
    for idx, row in df.iterrows():
        description = row['description'].upper()
        for category, keywords in saas_keywords.items():
            found = False
            for keyword in keywords:
                if keyword in description:
                    row_copy = row.copy()
                    row_copy['saas_category'] = category
                    row_copy['saas_service'] = keyword.lower()
                    saas_transactions.append(row_copy)
                    found = True
                    break
            if found:
                break
    
    if not saas_transactions:
        print("未找到 SaaS 相關交易")
        return pd.DataFrame()
    
    saas_df = pd.DataFrame(saas_transactions)
    
    # 去除重複交易 - 基於 description 和 amount 的組合
    print(f"去重前: {len(saas_df)} 筆交易")
    
    # 創建唯一標識符
    saas_df['unique_id'] = saas_df['description'].str.replace('^\d{2}/\d{2} ', '', regex=True) + '_' + saas_df['amount_abs'].astype(str)
    
    # 去除重複，保留第一筆
    saas_df_clean = saas_df.drop_duplicates(subset=['unique_id'], keep='first')
    saas_df_clean = saas_df_clean.drop('unique_id', axis=1)
    
    print(f"去重後: {len(saas_df_clean)} 筆 SaaS 相關交易")
    
    return saas_df_clean

def extract_service_details(saas_df):
    """提取服務詳細信息"""
    
    service_mapping = {
        'cursor': 'Cursor AI IDE',
        'openai': 'OpenAI (ChatGPT/API)',
        'anthropic': 'Anthropic Claude',
        'leonardo': 'Leonardo AI',
        'heygen': 'HeyGen Video AI',
        'figma': 'Figma Design',
        'adobe': 'Adobe Creative Suite',
        'google': 'Google Cloud/Services',
        'reportdash': 'ReportDash Analytics',
        'gandi': 'Gandi Domain/Hosting',
        'colab': 'Google Colab Pro',
        'manychat': 'ManyChat Marketing',
        'seasalt': 'Seasalt.AI',
        'spotify': 'Spotify Premium',
        'paddle': 'Paddle Payment'
    }
    
    saas_df['service_name'] = saas_df['saas_service'].map(service_mapping).fillna(saas_df['saas_service'])
    
    # 檢測訂閱類型
    def detect_subscription_type(description):
        desc_upper = description.upper()
        if 'USAGE' in desc_upper:
            return '按使用量計費'
        elif 'SUBSCR' in desc_upper or 'SUBSCRIPTION' in desc_upper:
            return '月度訂閱'
        elif any(word in desc_upper for word in ['PRO', 'PREMIUM', 'PLUS']):
            return '月度訂閱'
        else:
            return '一次性/其他'
    
    saas_df['subscription_type'] = saas_df['description'].apply(detect_subscription_type)
    
    return saas_df

def analyze_saas_spending(saas_df):
    """分析 SaaS 支出"""
    
    total_saas_spending = saas_df['amount_abs'].sum()
    num_services = saas_df['service_name'].nunique()
    num_transactions = len(saas_df)
    avg_transaction = saas_df['amount_abs'].mean()
    
    # 按服務分類統計
    category_stats = saas_df.groupby('saas_category').agg({
        'amount_abs': ['sum', 'count', 'mean'],
        'service_name': 'nunique'
    }).round(2)
    
    # 按具體服務統計
    service_stats = saas_df.groupby('service_name').agg({
        'amount_abs': ['sum', 'count', 'mean']
    }).round(2)
    
    # 按訂閱類型統計
    subscription_stats = saas_df.groupby('subscription_type').agg({
        'amount_abs': ['sum', 'count', 'mean']
    }).round(2)
    
    analysis = {
        'total_spending': total_saas_spending,
        'num_services': num_services,
        'num_transactions': num_transactions,
        'avg_transaction': avg_transaction,
        'category_stats': category_stats,
        'service_stats': service_stats,
        'subscription_stats': subscription_stats
    }
    
    return analysis

def create_saas_visualizations(saas_df, analysis):
    """創建 SaaS 支出可視化圖表"""
    
    # 嘗試找到可用的中文字體
    chinese_fonts = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'Microsoft JhengHei']
    available_font = None
    
    for font_name in chinese_fonts:
        try:
            # 檢查字體是否可用
            font_files = fm.findSystemFonts()
            for font_file in font_files:
                try:
                    font_prop = fm.FontProperties(fname=font_file)
                    if font_name.lower() in font_prop.get_name().lower():
                        available_font = font_name
                        break
                except:
                    continue
            if available_font:
                break
        except:
            continue
    
    # 如果找不到中文字體，使用英文標題
    if available_font:
        plt.rcParams['font.sans-serif'] = [available_font, 'Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        use_chinese = True
    else:
        plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']
        use_chinese = False
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    if use_chinese:
        fig.suptitle('企業 SaaS 服務支出分析 - 2025年5月\nThe Pocket Company by Accucrazy', fontsize=16, fontweight='bold')
    else:
        fig.suptitle('SaaS Service Spending Analysis - May 2025\nThe Pocket Company by Accucrazy', fontsize=16, fontweight='bold')
    
    # 1. 按服務類別的支出餅圖
    category_spending = saas_df.groupby('saas_category')['amount_abs'].sum()
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_spending)))
    
    # 翻譯類別名稱
    if use_chinese:
        category_labels = {
            'AI/ML Tools': 'AI/ML 工具',
            'Cloud Services': '雲端服務',
            'Design Tools': '設計工具',
            'Development Tools': '開發工具',
            'Marketing Tools': '行銷工具',
            'Media': '媒體工具'
        }
        display_labels = [category_labels.get(cat, cat) for cat in category_spending.index]
    else:
        display_labels = category_spending.index
    
    axes[0, 0].pie(category_spending.values, 
                   labels=display_labels, 
                   autopct='%1.1f%%',
                   colors=colors,
                   startangle=90)
    
    if use_chinese:
        axes[0, 0].set_title('SaaS 支出按類別分布')
    else:
        axes[0, 0].set_title('Spending by SaaS Category')
    
    # 2. 前10大服務支出條形圖
    top_services = saas_df.groupby('service_name')['amount_abs'].sum().sort_values(ascending=True).tail(10)
    
    axes[0, 1].barh(range(len(top_services)), top_services.values, color='skyblue')
    axes[0, 1].set_yticks(range(len(top_services)))
    axes[0, 1].set_yticklabels(top_services.index)
    
    if use_chinese:
        axes[0, 1].set_xlabel('支出金額 (NT$)')
        axes[0, 1].set_title('前10大 SaaS 服務支出')
    else:
        axes[0, 1].set_xlabel('Amount (NT$)')
        axes[0, 1].set_title('Top 10 SaaS Services by Spending')
    
    # 3. 訂閱類型分布
    subscription_counts = saas_df['subscription_type'].value_counts()
    
    # 翻譯訂閱類型
    if use_chinese:
        subscription_labels = subscription_counts.index
    else:
        subscription_translation = {
            '按使用量計費': 'Usage-based',
            '月度訂閱': 'Monthly Subscription',
            '一次性/其他': 'One-time/Other'
        }
        subscription_labels = [subscription_translation.get(label, label) for label in subscription_counts.index]
    
    axes[0, 2].pie(subscription_counts.values, labels=subscription_labels, 
                   autopct='%1.1f%%', startangle=90)
    
    if use_chinese:
        axes[0, 2].set_title('訂閱類型分布')
    else:
        axes[0, 2].set_title('Subscription Type Distribution')
    
    # 4. 交易金額分布
    axes[1, 0].hist(saas_df['amount_abs'], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
    
    if use_chinese:
        axes[1, 0].set_xlabel('交易金額 (NT$)')
        axes[1, 0].set_ylabel('頻次')
        axes[1, 0].set_title('SaaS 交易金額分布')
    else:
        axes[1, 0].set_xlabel('Transaction Amount (NT$)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Transaction Amount Distribution')
    
    # 5. AI/ML 工具詳細分析
    ai_ml_data = saas_df[saas_df['saas_category'] == 'AI/ML Tools']
    if not ai_ml_data.empty:
        ai_spending = ai_ml_data.groupby('service_name')['amount_abs'].sum().sort_values(ascending=True)
        
        axes[1, 1].barh(range(len(ai_spending)), ai_spending.values, color='orange')
        axes[1, 1].set_yticks(range(len(ai_spending)))
        axes[1, 1].set_yticklabels(ai_spending.index)
        
        if use_chinese:
            axes[1, 1].set_xlabel('支出金額 (NT$)')
            axes[1, 1].set_title('AI/ML 工具支出詳細')
        else:
            axes[1, 1].set_xlabel('Amount (NT$)')
            axes[1, 1].set_title('AI/ML Tools Spending Detail')
    else:
        no_data_text = '無 AI/ML 工具數據' if use_chinese else 'No AI/ML Tools Data'
        axes[1, 1].text(0.5, 0.5, no_data_text, ha='center', va='center', transform=axes[1, 1].transAxes)
    
    # 6. Cursor 專項分析
    cursor_data = saas_df[saas_df['saas_service'] == 'cursor']
    if not cursor_data.empty:
        cursor_by_type = cursor_data.groupby('subscription_type')['amount_abs'].sum()
        
        axes[1, 2].bar(range(len(cursor_by_type)), cursor_by_type.values, color='purple', alpha=0.7)
        axes[1, 2].set_xticks(range(len(cursor_by_type)))
        
        if use_chinese:
            type_labels = cursor_by_type.index
            axes[1, 2].set_ylabel('支出金額 (NT$)')
            axes[1, 2].set_title('Cursor AI 支出按類型')
        else:
            type_translation = {
                '按使用量計費': 'Usage-based',
                '月度訂閱': 'Monthly Sub',
                '一次性/其他': 'One-time'
            }
            type_labels = [type_translation.get(label, label) for label in cursor_by_type.index]
            axes[1, 2].set_ylabel('Amount (NT$)')
            axes[1, 2].set_title('Cursor AI Spending by Type')
        
        axes[1, 2].set_xticklabels(type_labels, rotation=45)
    else:
        no_cursor_text = '無 Cursor 數據' if use_chinese else 'No Cursor Data'
        axes[1, 2].text(0.5, 0.5, no_cursor_text, ha='center', va='center', transform=axes[1, 2].transAxes)
    
    plt.tight_layout()
    
    # 在圖表底部添加公司標識
    fig.text(0.5, 0.02, 'The Pocket Company by Accucrazy', ha='center', va='bottom', 
             fontsize=10, style='italic', alpha=0.7)
    
    plt.savefig('saas_spending_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("SaaS 分析圖表已保存為 'saas_spending_analysis.png'")

def generate_saas_report(saas_df, analysis):
    """生成 SaaS 支出分析報告"""
    
    report = f"""
================================================
企業 SaaS 服務支出分析報告
第一銀行信用卡帳單 - 2025年5月
The Pocket Company by Accucrazy
================================================

總體概況：
- SaaS 總支出：NT$ {analysis['total_spending']:,.2f}
- 使用服務數量：{analysis['num_services']} 個
- 總交易次數：{analysis['num_transactions']} 筆
- 平均每筆交易：NT$ {analysis['avg_transaction']:,.2f}

按服務類別分析：
"""
    
    for category in analysis['category_stats'].index:
        total = analysis['category_stats'].loc[category, ('amount_abs', 'sum')]
        count = analysis['category_stats'].loc[category, ('amount_abs', 'count')]
        percentage = (total / analysis['total_spending']) * 100
        
        report += f"""
{category}：
  - 總支出：NT$ {total:,.2f} ({percentage:.1f}%)
  - 交易次數：{count} 筆
"""
    
    report += "\n前10大 SaaS 服務支出：\n"
    
    top_services = analysis['service_stats'].sort_values(('amount_abs', 'sum'), ascending=False).head(10)
    
    for i, (service, data) in enumerate(top_services.iterrows(), 1):
        total = data[('amount_abs', 'sum')]
        count = data[('amount_abs', 'count')]
        percentage = (total / analysis['total_spending']) * 100
        
        report += f"{i:2d}. {service}: NT$ {total:,.2f} ({percentage:.1f}%) - {count}筆交易\n"
    
    # AI/ML 工具詳細分析
    ai_ml_tools = saas_df[saas_df['saas_category'] == 'AI/ML Tools']
    if not ai_ml_tools.empty:
        ai_ml_total = ai_ml_tools['amount_abs'].sum()
        
        report += f"""
AI/ML 工具詳細分析：
總支出：NT$ {ai_ml_total:,.2f}

具體工具：
"""
        
        ai_tools_detail = ai_ml_tools.groupby('service_name')['amount_abs'].agg(['sum', 'count'])
        
        for tool in ai_tools_detail.index:
            tool_total = ai_tools_detail.loc[tool, 'sum']
            tool_count = ai_tools_detail.loc[tool, 'count']
            report += f"• {tool}：NT$ {tool_total:,.2f} ({tool_count}筆)\n"
    
    report += """
成本優化建議：

1. Cursor AI 使用監控：檢查使用量計費是否合理
2. OpenAI API 成本控制：設置使用限額
3. 訂閱整合：檢查重複功能的工具
4. 定期評估：每月檢查 ROI

================================================
報告生成：The Pocket Company by Accucrazy
分析日期：2025年
================================================
"""
    
    return report

def main():
    """主要執行函數"""
    print("開始 SaaS 服務支出分析...")
    
    saas_df = load_and_filter_saas_data('clean_transactions.csv')
    
    if saas_df.empty:
        print("沒有找到 SaaS 相關交易數據")
        return
    
    saas_df = extract_service_details(saas_df)
    analysis = analyze_saas_spending(saas_df)
    
    create_saas_visualizations(saas_df, analysis)
    
    report = generate_saas_report(saas_df, analysis)
    print(report)
    
    with open('saas_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    saas_df.to_csv('saas_transactions.csv', index=False, encoding='utf-8')
    
    print("\n" + "="*60)
    print("SaaS 分析完成！")
    print("="*60)

if __name__ == "__main__":
    main() 