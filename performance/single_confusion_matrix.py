#!/usr/bin/env python3
"""
Single Comprehensive Confusion Matrix for Rule-Based Medical Diet Recommendation System
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
import seaborn as sns
from typing import List, Dict

from app.data.schema import from_dict
from app.rules.engine import build_constraints

def create_test_data_for_all_domains() -> Dict[str, List]:
    """Create test data for all medical domains"""
    
    medical_domains = {
        'Diabetes': {
            'conditions': ['diabetes'],
            'expected_rules': ['low_gi', 'high_fiber', 'avoid_refined_sugar', 'avoid_refined_carbs']
        },
        'Hypertension': {
            'conditions': ['hypertension'],
            'expected_rules': ['low_sodium', 'avoid_high_sodium']
        },
        'Heart Disease': {
            'conditions': ['heart disease'],
            'expected_rules': ['omega3', 'anti_inflammatory', 'low_saturated_fat', 'avoid_fried', 'avoid_processed']
        },
        'Kidney Disease': {
            'conditions': ['kidney disease'],
            'expected_rules': ['low_potassium', 'low_phosphorus', 'avoid_high_potassium', 'avoid_high_phosphorus']
        },
        'PCOS': {
            'conditions': ['pcos'],
            'expected_rules': ['low_gi', 'anti_inflammatory', 'high_fiber', 'lean_protein', 'avoid_refined_sugar', 'avoid_refined_carbs', 'avoid_fried']
        },
        'Gastric': {
            'conditions': ['gastric'],
            'expected_rules': ['high_fiber', 'avoid_spicy', 'avoid_fried']
        },
        'Thyroid': {
            'conditions': ['thyroid'],
            'expected_rules': ['avoid_tofu']
        }
    }
    
    all_predictions = []
    all_actual = []
    all_domains = []
    
    for domain_name, domain_data in medical_domains.items():
        profile = {
            "personal": {"age": 40, "gender": "male", "height": 170, "weight": 70},
            "medical": {"conditions": domain_data['conditions']},
            "dietary": {"diet_type": "veg"},
            "lifestyle": {}, "nutrition": {}, "special": {}
        }
        
        user_profile = from_dict(profile)
        constraints, explanations = build_constraints(user_profile)
        
        # Test each expected rule
        for rule in domain_data['expected_rules']:
            all_domains.append(domain_name)
            all_actual.append(1)  # Expected to be applied
            
            # Check if rule was actually applied
            applied = False
            
            if rule.startswith('avoid_'):
                tag = rule.replace('avoid_', '')
                if tag in constraints.avoid_tags:
                    applied = True
            elif rule == 'avoid_tofu':
                if any('tofu' in name for name in constraints.avoid_names):
                    applied = True
            elif rule in constraints.required_tags or rule in constraints.prefer_tags:
                applied = True
            
            all_predictions.append(1 if applied else 0)
    
    return {
        'predictions': all_predictions,
        'actual': all_actual,
        'domains': all_domains,
        'domain_names': list(medical_domains.keys())
    }

def create_single_confusion_matrix():
    """Create single comprehensive confusion matrix"""
    
    # Get test data
    data = create_test_data_for_all_domains()
    
    # Create confusion matrix
    cm = confusion_matrix(data['actual'], data['predictions'], labels=[0, 1])
    
    # Calculate metrics
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn) * 100
    precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Create visualization
    plt.figure(figsize=(12, 10))
    
    # Create subplot layout
    gs = plt.GridSpec(3, 3, figure=plt.gcf(), hspace=0.3, wspace=0.3)
    
    # Main confusion matrix
    ax_main = plt.subplot(gs[0:2, 0:2])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_main,
                xticklabels=['Not Applied', 'Applied'],
                yticklabels=['Expected Not Applied', 'Expected Applied'],
                annot_kws={'size': 16, 'weight': 'bold'})
    
    ax_main.set_title('Confusion Matrix - All Medical Domains', fontsize=16, fontweight='bold', pad=20)
    ax_main.set_xlabel('Predicted', fontsize=14)
    ax_main.set_ylabel('Actual', fontsize=14)
    
    # Metrics panel
    ax_metrics = plt.subplot(gs[0, 2])
    ax_metrics.axis('off')
    
    metrics_text = f"""
    PERFORMANCE METRICS
    
    Accuracy: {accuracy:.1f}%
    Precision: {precision:.1f}%
    Recall: {recall:.1f}%
    F1-Score: {f1_score:.1f}%
    
    Total Rules: {len(data['actual'])}
    Correct: {tp + tn}
    Incorrect: {fp + fn}
    """
    
    ax_metrics.text(0.1, 0.9, metrics_text, transform=ax_metrics.transAxes,
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Domain-wise accuracy
    ax_domains = plt.subplot(gs[1, 2])
    domain_accuracies = {}
    
    for domain in data['domain_names']:
        domain_correct = 0
        domain_total = 0
        
        for i, d in enumerate(data['domains']):
            if d == domain:
                domain_total += 1
                if data['actual'][i] == data['predictions'][i]:
                    domain_correct += 1
        
        if domain_total > 0:
            domain_accuracies[domain] = (domain_correct / domain_total) * 100
    
    # Create bar chart for domain accuracies
    domains = list(domain_accuracies.keys())
    accuracies = list(domain_accuracies.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    bars = ax_domains.bar(range(len(domains)), accuracies, color=colors[:len(domains)])
    ax_domains.set_title('Accuracy by Domain', fontsize=12, fontweight='bold')
    ax_domains.set_ylabel('Accuracy (%)', fontsize=10)
    ax_domains.set_xticks(range(len(domains)))
    ax_domains.set_xticklabels(domains, rotation=45, ha='right', fontsize=9)
    ax_domains.set_ylim(0, 100)
    
    # Add percentage labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax_domains.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{acc:.0f}%', ha='center', va='bottom', fontsize=8)
    
    # Summary statistics
    ax_summary = plt.subplot(gs[2, :])
    ax_summary.axis('off')
    
    summary_text = f"""
    SUMMARY: Rule-Based Medical Diet Recommendation System Performance
    
    • Total Medical Domains Evaluated: {len(data['domain_names'])}
    • Total Diet Rules Tested: {len(data['actual'])}
    • Overall System Accuracy: {accuracy:.1f}%
    • Best Performing Domain: {max(domain_accuracies, key=domain_accuracies.get)} ({max(domain_accuracies.values()):.1f}%)
    • Domains Needing Attention: {[d for d, acc in domain_accuracies.items() if acc < 90]}
    
    The confusion matrix shows the system's ability to correctly apply dietary rules across all medical conditions.
    True Positives (TP): Rules correctly applied | False Positives (FP): Rules incorrectly applied
    True Negatives (TN): Rules correctly not applied | False Negatives (FN): Rules missed
    """
    
    ax_summary.text(0.05, 0.5, summary_text, transform=ax_summary.transAxes,
                    fontsize=11, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Overall title
    plt.suptitle('Rule-Based Medical Diet Recommendation System - Comprehensive Confusion Matrix Analysis',
                fontsize=18, fontweight='bold', y=0.98)
    
    # Save the figure
    plt.savefig('single_comprehensive_confusion_matrix.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    return {
        'confusion_matrix': cm,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'domain_accuracies': domain_accuracies
    }

if __name__ == "__main__":
    print("Creating Single Comprehensive Confusion Matrix...")
    
    # Generate the confusion matrix
    results = create_single_confusion_matrix()
    
    print("\n" + "="*60)
    print("COMPREHENSIVE CONFUSION MATRIX GENERATED!")
    print("="*60)
    print(f"✓ Image saved as: 'single_comprehensive_confusion_matrix.png'")
    print(f"✓ Overall Accuracy: {results['accuracy']:.1f}%")
    print(f"✓ Precision: {results['precision']:.1f}%")
    print(f"✓ Recall: {results['recall']:.1f}%")
    print(f"✓ F1-Score: {results['f1_score']:.1f}%")
    
    print("\nDomain-wise Performance:")
    for domain, accuracy in results['domain_accuracies'].items():
        print(f"  • {domain}: {accuracy:.1f}%")
    
    print(f"\nTotal Rules Evaluated: {sum(results['confusion_matrix'].flatten())}")
    print("Confusion Matrix:")
    print(results['confusion_matrix'])
