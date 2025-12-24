#!/usr/bin/env python3
"""
Comprehensive Confusion Matrix for Rule-Based Medical Diet Recommendation System
All domains in one visualization
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
from typing import Dict, List, Tuple
import pandas as pd

from app.data.schema import from_dict
from app.rules.engine import build_constraints

def create_comprehensive_test_data() -> Tuple[List[str], List[str], List[str]]:
    """Create comprehensive test data for all medical conditions"""
    
    # Define all medical conditions and their expected rules
    medical_domains = {
        'diabetes': {
            'expected_required': ['low_gi'],
            'expected_preferred': ['high_fiber'],
            'expected_avoid': ['high_gi', 'refined_sugar', 'refined_carbs'],
            'profile': {
                "personal": {"age": 45, "gender": "male", "height": 175, "weight": 80},
                "medical": {"conditions": ["diabetes"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'hypertension': {
            'expected_required': [],
            'expected_preferred': ['low_sodium'],
            'expected_avoid': ['high_sodium'],
            'profile': {
                "personal": {"age": 55, "gender": "female", "height": 165, "weight": 70},
                "medical": {"conditions": ["hypertension"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'heart_disease': {
            'expected_required': [],
            'expected_preferred': ['omega3', 'anti_inflammatory', 'low_saturated_fat'],
            'expected_avoid': ['high_saturated_fat', 'fried', 'processed'],
            'profile': {
                "personal": {"age": 60, "gender": "male", "height": 170, "weight": 75},
                "medical": {"conditions": ["heart disease"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'kidney_disease': {
            'expected_required': [],
            'expected_preferred': ['low_potassium', 'low_phosphorus'],
            'expected_avoid': ['high_potassium', 'high_phosphorus'],
            'profile': {
                "personal": {"age": 50, "gender": "male", "height": 172, "weight": 85},
                "medical": {"conditions": ["kidney disease"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'pcos': {
            'expected_required': ['low_gi'],
            'expected_preferred': ['anti_inflammatory', 'high_fiber', 'lean_protein'],
            'expected_avoid': ['refined_sugar', 'refined_carbs', 'fried'],
            'profile': {
                "personal": {"age": 30, "gender": "female", "height": 160, "weight": 65},
                "medical": {"conditions": ["pcos"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'gastric': {
            'expected_required': [],
            'expected_preferred': ['high_fiber'],
            'expected_avoid': ['spicy', 'fried'],
            'profile': {
                "personal": {"age": 40, "gender": "male", "height": 175, "weight": 80},
                "medical": {"conditions": ["gastric"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        },
        'thyroid': {
            'expected_required': [],
            'expected_preferred': [],
            'expected_avoid': [],  # Special case - avoids specific names
            'profile': {
                "personal": {"age": 35, "gender": "female", "height": 162, "weight": 68},
                "medical": {"conditions": ["thyroid"]},
                "dietary": {"diet_type": "veg"},
                "lifestyle": {}, "nutrition": {}, "special": {}
            }
        }
    }
    
    all_expected = []
    all_predicted = []
    all_domains = []
    
    # Test each domain
    for domain, rules in medical_domains.items():
        profile = from_dict(rules['profile'])
        constraints, explanations = build_constraints(profile)
        
        # Test required tags
        for expected_tag in rules['expected_required']:
            all_expected.append(f"{domain}_required_{expected_tag}")
            if expected_tag in constraints.required_tags:
                all_predicted.append(f"{domain}_required_{expected_tag}")
            else:
                all_predicted.append(f"{domain}_required_missing")
            all_domains.append(domain)
        
        # Test preferred tags
        for expected_tag in rules['expected_preferred']:
            all_expected.append(f"{domain}_preferred_{expected_tag}")
            if expected_tag in constraints.prefer_tags:
                all_predicted.append(f"{domain}_preferred_{expected_tag}")
            else:
                all_predicted.append(f"{domain}_preferred_missing")
            all_domains.append(domain)
        
        # Test avoid tags
        for expected_tag in rules['expected_avoid']:
            all_expected.append(f"{domain}_avoid_{expected_tag}")
            if expected_tag in constraints.avoid_tags:
                all_predicted.append(f"{domain}_avoid_{expected_tag}")
            else:
                all_predicted.append(f"{domain}_avoid_missing")
            all_domains.append(domain)
        
        # Special case for thyroid (name avoidance)
        if domain == 'thyroid':
            all_expected.append("thyroid_avoid_tofu")
            if any('tofu' in name for name in constraints.avoid_names):
                all_predicted.append("thyroid_avoid_tofu")
            else:
                all_predicted.append("thyroid_avoid_missing")
            all_domains.append(domain)
    
    return all_expected, all_predicted, all_domains

def create_comprehensive_confusion_matrix(expected: List[str], predicted: List[str], domains: List[str]):
    """Create comprehensive confusion matrix for all domains"""
    
    # Create binary classification data (correct vs incorrect)
    binary_expected = []
    binary_predicted = []
    domain_labels = []
    
    for exp, pred, domain in zip(expected, predicted, domains):
        binary_expected.append(1)  # Expected to be correct
        binary_predicted.append(1 if exp == pred else 0)
        domain_labels.append(domain)
    
    # Create overall confusion matrix with both labels
    overall_cm = confusion_matrix(binary_expected, binary_predicted, labels=[0, 1])
    
    # Create domain-specific confusion matrices
    unique_domains = list(set(domains))
    domain_cms = {}
    for domain in unique_domains:
        domain_expected = []
        domain_predicted = []
        
        for exp, pred, d in zip(expected, predicted, domains):
            if d == domain:
                domain_expected.append(1)
                domain_predicted.append(1 if exp == pred else 0)
        
        if len(domain_expected) > 0:
            # Ensure both labels are present for proper confusion matrix
            domain_cms[domain] = confusion_matrix(domain_expected, domain_predicted, labels=[0, 1])
    
    return overall_cm, domain_cms, unique_domains

def create_comprehensive_visualization(overall_cm, domain_cms, unique_domains):
    """Create comprehensive visualization with all confusion matrices"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # Create grid layout
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    # Overall confusion matrix (top left, spanning 2x2)
    ax_main = fig.add_subplot(gs[0:2, 0:2])
    sns.heatmap(overall_cm, annot=True, fmt='d', cmap='Blues', ax=ax_main,
                xticklabels=['Incorrect', 'Correct'],
                yticklabels=['Expected Correct', 'Expected Incorrect'])
    ax_main.set_title('Overall System Performance', fontsize=16, fontweight='bold')
    ax_main.set_xlabel('Predicted')
    ax_main.set_ylabel('Actual')
    
    # Calculate overall accuracy
    accuracy = (overall_cm[1, 1] + overall_cm[0, 0]) / overall_cm.sum() * 100
    ax_main.text(0.5, -0.15, f'Overall Accuracy: {accuracy:.1f}%', 
                ha='center', va='center', transform=ax_main.transAxes, 
                fontsize=14, fontweight='bold', color='green')
    
    # Domain-specific confusion matrices
    positions = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)]
    
    for i, (domain, cm) in enumerate(domain_cms.items()):
        if i < len(positions):
            row, col = positions[i]
            ax = fig.add_subplot(gs[row, col])
            
            # Calculate accuracy for this domain
            domain_acc = (cm[1, 1] + cm[0, 0]) / cm.sum() * 100 if cm.sum() > 0 else 0
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                        xticklabels=['Inc', 'Cor'], yticklabels=['Exp', 'Not'])
            ax.set_title(f'{domain.replace("_", " ").title()}\n({domain_acc:.1f}%)', 
                        fontsize=12, fontweight='bold')
            ax.set_xlabel('Predicted', fontsize=10)
            ax.set_ylabel('Actual', fontsize=10)
    
    # Performance summary table
    ax_summary = fig.add_subplot(gs[2:, 2:])
    ax_summary.axis('off')
    
    # Create summary data
    summary_data = []
    for domain, cm in domain_cms.items():
        total = cm.sum()
        correct = cm[1, 1] + cm[0, 0]
        accuracy = (correct / total * 100) if total > 0 else 0
        precision = cm[1, 1] / (cm[1, 1] + cm[0, 1]) if (cm[1, 1] + cm[0, 1]) > 0 else 0
        recall = cm[1, 1] / (cm[1, 1] + cm[1, 0]) if (cm[1, 1] + cm[1, 0]) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        summary_data.append({
            'Domain': domain.replace('_', ' ').title(),
            'Total Rules': total,
            'Correct': correct,
            'Accuracy': f'{accuracy:.1f}%',
            'Precision': f'{precision:.2f}',
            'Recall': f'{recall:.2f}',
            'F1-Score': f'{f1:.2f}'
        })
    
    # Create table
    df = pd.DataFrame(summary_data)
    table = ax_summary.table(cellText=df.values, colLabels=df.columns,
                            cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style the table
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4ECDC4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax_summary.set_title('Performance Summary by Domain', fontsize=14, fontweight='bold', pad=20)
    
    # Overall title
    fig.suptitle('Rule-Based Medical Diet Recommendation System - Comprehensive Confusion Matrix Analysis', 
                fontsize=18, fontweight='bold', y=0.98)
    
    plt.savefig('comprehensive_confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig, summary_data

def generate_detailed_report(summary_data):
    """Generate detailed performance report"""
    
    report = []
    report.append("# Rule-Based Medical Diet Recommendation System - Comprehensive Performance Report")
    report.append("=" * 80)
    report.append("")
    
    # Overall summary
    total_rules = sum(item['Total Rules'] for item in summary_data)
    total_correct = sum(item['Correct'] for item in summary_data)
    overall_accuracy = (total_correct / total_rules * 100) if total_rules > 0 else 0
    
    report.append("## Overall System Performance")
    report.append(f"- Total Rules Tested: {total_rules}")
    report.append(f"- Total Correct Applications: {total_correct}")
    report.append(f"- Overall System Accuracy: {overall_accuracy:.1f}%")
    report.append("")
    
    # Domain-wise performance
    report.append("## Domain-wise Performance Analysis")
    report.append("")
    
    for item in summary_data:
        report.append(f"### {item['Domain']}")
        report.append(f"- Total Rules: {item['Total Rules']}")
        report.append(f"- Correct Applications: {item['Correct']}")
        report.append(f"- Accuracy: {item['Accuracy']}")
        report.append(f"- Precision: {item['Precision']}")
        report.append(f"- Recall: {item['Recall']}")
        report.append(f"- F1-Score: {item['F1-Score']}")
        report.append("")
    
    # Performance analysis
    report.append("## Performance Analysis")
    report.append("")
    
    best_performer = max(summary_data, key=lambda x: float(x['Accuracy'].replace('%', '')))
    worst_performer = min(summary_data, key=lambda x: float(x['Accuracy'].replace('%', '')))
    
    report.append(f"### Key Insights:")
    report.append(f"- **Best Performing Domain**: {best_performer['Domain']} ({best_performer['Accuracy']})")
    report.append(f"- **Needs Improvement**: {worst_performer['Domain']} ({worst_performer['Accuracy']})")
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    report.append("1. Review rule implementation for domains with lower accuracy")
    report.append("2. Enhance test coverage for edge cases")
    report.append("3. Consider rule refinement for complex multi-condition scenarios")
    report.append("4. Implement continuous monitoring of rule performance")
    report.append("")
    
    report.append("---")
    report.append("*Report generated by Comprehensive Confusion Matrix Analysis*")
    
    return '\n'.join(report)

if __name__ == "__main__":
    print("Generating Comprehensive Confusion Matrix Analysis...")
    
    # Create test data
    expected, predicted, domains = create_comprehensive_test_data()
    print(f"Created {len(expected)} test cases across {len(set(domains))} medical domains")
    
    # Generate confusion matrices
    overall_cm, domain_cms, unique_domains = create_comprehensive_confusion_matrix(expected, predicted, domains)
    
    # Create visualization
    print("Creating comprehensive visualization...")
    fig, summary_data = create_comprehensive_visualization(overall_cm, domain_cms, unique_domains)
    
    # Generate report
    print("Generating detailed performance report...")
    report = generate_detailed_report(summary_data)
    
    # Save report
    with open('comprehensive_performance_report.txt', 'w') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"✓ Confusion Matrix Visualization: 'comprehensive_confusion_matrix.png'")
    print(f"✓ Performance Report: 'comprehensive_performance_report.txt'")
    print(f"✓ Total Rules Evaluated: {len(expected)}")
    print(f"✓ Medical Domains Covered: {len(unique_domains)}")
    
    # Print summary
    print("\nQUICK SUMMARY:")
    for item in summary_data:
        print(f"  • {item['Domain']}: {item['Accuracy']} accuracy ({item['Correct']}/{item['Total Rules']} rules)")
    
    print(f"\nOverall System Accuracy: {sum(item['Correct'] for item in summary_data)}/{sum(item['Total Rules'] for item in summary_data)} = {(sum(item['Correct'] for item in summary_data) / sum(item['Total Rules'] for item in summary_data) * 100):.1f}%")
