"""
Interior Design Style Classifier - Training Script
Trains a ResNet50 model on the interior design dataset.

Usage:
    python -m ml.train --data_dir ../dataset_train/dataset_train --epochs 25 --batch_size 32
"""

import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
import matplotlib.pyplot as plt
import json
from ml.model import InteriorStyleClassifier

STYLE_CLASSES = [
    "asian", "coastal", "contemporary", "craftsman", "eclectic",
    "farmhouse", "french-country", "industrial", "mediterranean",
    "mid-century-modern", "modern", "rustic", "scandinavian",
    "shabby-chic-style", "southwestern", "traditional", "transitional",
    "tropical", "victorian"
]


def get_transforms(phase: str):
    if phase == "train":
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training")
    for inputs, labels in pbar:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        pbar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "acc": f"{100. * correct / total:.2f}%"
        })

    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc


def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in tqdm(dataloader, desc="Evaluating"):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc


def plot_training_history(history, save_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(history["train_loss"], label="Train Loss")
    ax1.plot(history["val_loss"], label="Val Loss")
    ax1.set_title("Loss over Epochs")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.legend()

    ax2.plot(history["train_acc"], label="Train Acc")
    ax2.plot(history["val_acc"], label="Val Acc")
    ax2.set_title("Accuracy over Epochs")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Training plot saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Interior Style Classifier")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to training dataset")
    parser.add_argument("--test_dir", type=str, default=None, help="Path to test dataset")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--output_dir", type=str, default="./ml/models")
    parser.add_argument("--device", type=str, default="auto")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    print(f"Using device: {device}")
    os.makedirs(args.output_dir, exist_ok=True)

    # Load datasets
    train_dataset = datasets.ImageFolder(
        args.data_dir,
        transform=get_transforms("train")
    )

    # Use 90/10 split from training data for validation
    val_size = int(0.1 * len(train_dataset))
    train_size = len(train_dataset) - val_size
    train_subset, val_subset = torch.utils.data.random_split(
        train_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    num_workers = 0 if os.name == 'nt' else 4  # Windows doesn't support multiprocessing in DataLoader well
    train_loader = DataLoader(train_subset, batch_size=args.batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_subset, batch_size=args.batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    # Save class mapping
    class_to_idx = train_dataset.class_to_idx
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    with open(os.path.join(args.output_dir, "class_mapping.json"), "w") as f:
        json.dump({"class_to_idx": class_to_idx, "idx_to_class": {str(k): v for k, v in idx_to_class.items()}}, f, indent=2)

    print(f"Classes: {list(class_to_idx.keys())}")
    print(f"Training samples: {train_size}, Validation samples: {val_size}")

    # Initialize model
    model = InteriorStyleClassifier(num_classes=len(class_to_idx), pretrained=True).to(device)

    # Freeze backbone initially, train only classifier head
    for param in model.backbone.parameters():
        param.requires_grad = False
    for param in model.backbone.fc.parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0

    # Phase 1: Train classifier head (5 epochs)
    head_epochs = min(5, args.epochs)
    print(f"\n--- Phase 1: Training classifier head for {head_epochs} epochs ---")

    for epoch in range(head_epochs):
        print(f"\nEpoch {epoch + 1}/{head_epochs}")
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(args.output_dir, "interior_style_classifier.pth"))
            print(f"  -> Best model saved (val_acc: {val_acc:.2f}%)")

    # Phase 2: Fine-tune entire model
    remaining_epochs = args.epochs - head_epochs
    if remaining_epochs > 0:
        print(f"\n--- Phase 2: Fine-tuning full model for {remaining_epochs} epochs ---")
        for param in model.backbone.parameters():
            param.requires_grad = True

        optimizer = optim.Adam(model.parameters(), lr=args.lr * 0.1)
        scheduler = CosineAnnealingLR(optimizer, T_max=remaining_epochs)

        for epoch in range(remaining_epochs):
            print(f"\nEpoch {head_epochs + epoch + 1}/{args.epochs}")
            train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc = evaluate(model, val_loader, criterion, device)
            scheduler.step()

            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)

            print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), os.path.join(args.output_dir, "interior_style_classifier.pth"))
                print(f"  -> Best model saved (val_acc: {val_acc:.2f}%)")

    # Save training history
    with open(os.path.join(args.output_dir, "training_history.json"), "w") as f:
        json.dump(history, f, indent=2)

    plot_training_history(history, os.path.join(args.output_dir, "training_plot.png"))
    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: {os.path.join(args.output_dir, 'interior_style_classifier.pth')}")


if __name__ == "__main__":
    main()
