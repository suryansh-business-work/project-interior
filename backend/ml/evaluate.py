"""
Evaluation script for the trained model.

Usage:
    python -m ml.evaluate --model_path ./ml/models/interior_style_classifier.pth --test_dir ../dataset_test/dataset_test
"""

import argparse
import json
import os
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from ml.model import InteriorStyleClassifier
from ml.train import get_transforms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--test_dir", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--device", type=str, default="auto")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    print(f"Using device: {device}")

    # Load class mapping
    model_dir = os.path.dirname(args.model_path)
    mapping_path = os.path.join(model_dir, "class_mapping.json")
    with open(mapping_path) as f:
        mapping = json.load(f)

    idx_to_class = {int(k): v for k, v in mapping["idx_to_class"].items()}
    num_classes = len(idx_to_class)

    # Load model
    model = InteriorStyleClassifier.load_trained(args.model_path, num_classes, device)
    print("Model loaded successfully.")

    # Load test dataset
    test_dataset = datasets.ImageFolder(args.test_dir, transform=get_transforms("val"))
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    print(f"Test samples: {len(test_dataset)}")

    # Predict
    all_preds = []
    all_labels = []

    model.eval()
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    # Classification report
    class_names = [idx_to_class[i] for i in range(num_classes)]
    report = classification_report(all_labels, all_preds, target_names=class_names, digits=4)
    print("\nClassification Report:")
    print(report)

    # Overall accuracy
    accuracy = (all_preds == all_labels).mean() * 100
    print(f"Overall Test Accuracy: {accuracy:.2f}%")

    # Save results
    results = {
        "accuracy": float(accuracy),
        "report": classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
    }
    results_path = os.path.join(model_dir, "evaluation_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
