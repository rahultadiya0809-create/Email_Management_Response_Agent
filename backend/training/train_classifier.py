"""
Training script for the email classifier.

Usage:
    python train_classifier.py [--data path/to/data.csv]

This will train the TF-IDF + Logistic Regression model on the
provided labeled data and save the model to disk.
"""

import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.classifier import email_classifier


def main():
    parser = argparse.ArgumentParser(description="Train the email classifier")
    parser.add_argument(
        "--data",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "sample_data.csv"),
        help="Path to the training data CSV (columns: text, category)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  EMAIL CLASSIFIER TRAINING")
    print("=" * 60)
    print(f"\nTraining data: {args.data}")

    if not os.path.exists(args.data):
        print(f"Error: Training data not found at {args.data}")
        sys.exit(1)

    print("\nTraining model...")
    results = email_classifier.train(args.data)

    print(f"\n✅ Training complete!")
    print(f"   Accuracy: {results['accuracy']:.2%}")
    print(f"   Cross-validation: {results['cv_mean_accuracy']:.2%} "
          f"(±{results['cv_std']:.2%})")

    print("\n📊 Classification Report:")
    report = results["classification_report"]
    print(f"   {'Category':<16} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print(f"   {'-' * 52}")
    for category in ["urgent", "informational", "promotional"]:
        if category in report:
            r = report[category]
            print(
                f"   {category:<16} {r['precision']:<12.2%} "
                f"{r['recall']:<12.2%} {r['f1-score']:<12.2%}"
            )

    print(f"\n💾 Model saved successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
