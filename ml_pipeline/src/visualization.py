"""
visualization.py - Visualization Module for GlicoSaliva ML Pipeline

Creates comprehensive visualizations for data exploration and model evaluation:
- Feature distributions (histograms, box plots)
- Correlation heatmap
- Decision boundary plots (2D projections)
- Confusion matrix visualization
- ROC curve and AUC

Target: Generate publication-ready figures for analysis
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Tuple, Dict

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    roc_auc_score
)
from sklearn.preprocessing import StandardScaler, label_binarize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VisualizationError(ValueError):
    """Error in visualization."""
    pass


# Default figure settings
DEFAULT_FIGURE_SETTINGS = {
    "figsize": (10, 8),
    "dpi": 300,
    "font_size": 12,
    "color_normal": "#2ecc71",  # Green for Normal
    "color_prediabetes": "#f39c12",  # Orange for Pre-Diabetes
    "color_diabetes": "#e74c3c",  # Red for Diabetes
    "color_palette": ["#2ecc71", "#f39c12", "#e74c3c"]
}

# Clinical category labels
CATEGORY_LABELS = {
    0: "Normal",
    1: "Pre-Diabetes",
    2: "Diabetes"
}


def _set_style():
    """Set matplotlib style for publication-ready figures."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.size'] = DEFAULT_FIGURE_SETTINGS["font_size"]
    plt.rcParams['figure.dpi'] = DEFAULT_FIGURE_SETTINGS["dpi"]
    plt.rcParams['savefig.dpi'] = DEFAULT_FIGURE_SETTINGS["dpi"]


def _get_colors():
    """Get color palette for different classes."""
    return DEFAULT_FIGURE_SETTINGS["color_palette"].copy()


def create_feature_distributions(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    target_col: str = "bg_class",
    output_dir: str = "figures/feature_distributions",
    format: str = "png",
    show_plot: bool = False
) -> Dict[str, str]:
    """Create histograms and box plots for feature distributions.
    
    Args:
        df: Input DataFrame
        feature_cols: List of feature columns to plot. If None, uses all numeric features.
        target_col: Column name for class labels
        output_dir: Directory to save figures
        format: Output format ('png' or 'svg')
        show_plot: Whether to show plots (for interactive use)
        
    Returns:
        Dictionary mapping plot names to file paths
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Determine features to plot
    if feature_cols is None:
        feature_cols = [col for col in df.columns 
                       if col not in [target_col, "id"] 
                       and df[col].dtype in ['int64', 'float64']]
    
    results = {}
    
    # Plot histograms with class overlay
    logger.info("Creating feature histograms with class overlay")
    for i, feature in enumerate(feature_cols):
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
        
        colors = _get_colors()
        
        for class_id in sorted(df[target_col].unique()):
            class_data = df[df[target_col] == class_id][feature]
            label = CATEGORY_LABELS.get(class_id, f"Class {class_id}")
            color = colors[class_id % len(colors)]
            
            ax.hist(class_data, bins=20, alpha=0.6, label=label, color=color, edgecolor='black')
        
        ax.set_xlabel(feature)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Distribution of {feature} by Blood Glucose Class")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plot_name = f"{feature}_distribution"
        plot_path = output_path / f"{plot_name}.{format}"
        fig.savefig(plot_path, bbox_inches='tight')
        plt.close(fig)
        
        results[plot_name] = str(plot_path)
        logger.info(f"Saved histogram: {plot_path}")
        
        if show_plot:
            plt.show()
            plt.close(fig)
    
    # Plot box plots per class
    logger.info("Creating box plots per class")
    for feature in feature_cols:
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
        
        colors = _get_colors()
        
        # Prepare data for box plot
        data_to_plot = []
        labels = []
        box_colors = []
        
        for class_id in sorted(df[target_col].unique()):
            class_data = df[df[target_col] == class_id][feature]
            data_to_plot.append(class_data)
            labels.append(CATEGORY_LABELS.get(class_id, f"Class {class_id}"))
            box_colors.append(colors[class_id % len(colors)])
        
        bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
        
        # Set box colors
        for patch, color in zip(bp['boxes'], box_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel("Blood Glucose Class")
        ax.set_ylabel(feature)
        ax.set_title(f"{feature} Distribution by Class")
        ax.grid(True, alpha=0.3, axis='y')
        
        plot_name = f"{feature}_boxplot"
        plot_path = output_path / f"{plot_name}.{format}"
        fig.savefig(plot_path, bbox_inches='tight')
        plt.close(fig)
        
        results[plot_name] = str(plot_path)
        logger.info(f"Saved box plot: {plot_path}")
        
        if show_plot:
            plt.show()
            plt.close(fig)
    
    # Create summary report
    summary = {
        "plot_type": "feature_distributions",
        "features": feature_cols,
        "target_column": target_col,
        "plots_saved": list(results.keys()),
        "output_directory": str(output_path),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    return results


def create_correlation_heatmap(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    target_col: str = "bg_class",
    output_dir: str = "figures/correlation",
    format: str = "png",
    show_plot: bool = False
) -> Dict[str, str]:
    """Create correlation heatmap for features.
    
    Args:
        df: Input DataFrame
        feature_cols: List of feature columns. If None, uses all numeric features.
        target_col: Target column to include in correlation
        output_dir: Directory to save figures
        format: Output format ('png' or 'svg')
        show_plot: Whether to show plots
        
    Returns:
        Dictionary with plot paths and correlation matrix
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Determine columns to include
    if feature_cols is None:
        feature_cols = [col for col in df.columns 
                       if col not in ["id"] 
                       and df[col].dtype in ['int64', 'float64']]
    
    # Select columns for correlation
    cols_to_include = [col for col in feature_cols if col in df.columns]
    
    if target_col in df.columns and target_col not in cols_to_include:
        cols_to_include.append(target_col)
    
    # Calculate correlation matrix
    corr_matrix = df[cols_to_include].corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
    
    # Create mask for upper triangle (optional)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Create heatmap
    im = ax.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    
    # Add labels
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels([col.replace('_', '\n') for col in corr_matrix.columns], rotation=45, ha='right')
    ax.set_yticklabels([col.replace('_', '\n') for col in corr_matrix.columns])
    
    # Add colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Correlation Coefficient')
    
    # Add correlation values
    for i in range(len(corr_matrix)):
        for j in range(len(corr_matrix)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha='center', va='center', color='black', fontsize=9)
    
    ax.set_title('Feature Correlation Heatmap')
    
    plot_name = "correlation_heatmap"
    plot_path = output_path / f"{plot_name}.{format}"
    fig.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"Saved correlation heatmap: {plot_path}")
    
    if show_plot:
        plt.show()
        plt.close(fig)
    
    # Save correlation matrix
    corr_path = output_path / "correlation_matrix.json"
    corr_dict = corr_matrix.to_dict()
    with open(corr_path, "w") as f:
        import json
        json.dump(corr_dict, f, indent=2)
    
    logger.info(f"Saved correlation matrix: {corr_path}")
    
    return {
        plot_name: str(plot_path),
        "correlation_matrix": corr_dict,
        "output_directory": str(output_path),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def create_decision_boundaries(
    model,
    X: np.ndarray,
    y: np.ndarray,
    feature_indices: Tuple[int, int] = (0, 1),
    output_dir: str = "figures/decision_boundaries",
    format: str = "png",
    show_plot: bool = False
) -> Dict[str, str]:
    """Create decision boundary plot for 2D projections.
    
    Args:
        model: Trained model with predict method
        X: Feature array
        y: Label array
        feature_indices: Tuple of (feature1_idx, feature2_idx) to use
        output_dir: Directory to save figures
        format: Output format ('png' or 'svg')
        show_plot: Whether to show plots
        
    Returns:
        Dictionary with plot paths
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract selected features
    X_selected = X[:, feature_indices]
    
    # Create mesh for decision boundary
    x_min, x_max = X_selected[:, 0].min() - 0.5, X_selected[:, 0].max() + 0.5
    y_min, y_max = X_selected[:, 1].min() - 0.5, X_selected[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                        np.linspace(y_min, y_max, 100))
    
    # Reshape for prediction
    X_mesh = np.c_[xx.ravel(), yy.ravel()]
    
    # Make predictions
    try:
        Z = model.predict(X_mesh)
        Z = Z.reshape(xx.shape)
    except Exception as e:
        logger.warning(f"Decision boundary plot failed: {e}")
        return {"error": str(e)}
    
    # Create plot
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
    
    # Plot decision boundary
    colors = _get_colors()
    contour = ax.contourf(xx, yy, Z, alpha=0.3, cmap='Pastel1')
    
    # Plot data points
    scatter = ax.scatter(X_selected[:, 0], X_selected[:, 1],
                        c=y, cmap='Pastel1', edgecolor='k', s=50, alpha=0.7)
    
    # Add labels
    feature_names = [f"Feature {feature_indices[0]}", f"Feature {feature_indices[1]}"]
    ax.set_xlabel(feature_names[0])
    ax.set_ylabel(feature_names[1])
    ax.set_title(f'Decision Boundaries (Features {feature_indices[0]} vs {feature_indices[1]})')
    
    # Add colorbar
    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels([CATEGORY_LABELS.get(i, f"Class {i}") for i in [0, 1, 2]])
    
    plot_name = f"decision_boundary_f{feature_indices[0]}_f{feature_indices[1]}"
    plot_path = output_path / f"{plot_name}.{format}"
    fig.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"Saved decision boundary plot: {plot_path}")
    
    if show_plot:
        plt.show()
        plt.close(fig)
    
    return {
        plot_name: str(plot_path),
        "output_directory": str(output_path),
        "feature_indices": feature_indices,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def create_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_dir: str = "figures/confusion_matrix",
    format: str = "png",
    show_plot: bool = False
) -> Dict[str, str]:
    """Create confusion matrix visualization.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        output_dir: Directory to save figures
        format: Output format ('png' or 'svg')
        show_plot: Whether to show plots
        
    Returns:
        Dictionary with plot paths and matrix data
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Create figure
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
    
    # Display confusion matrix
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=[CATEGORY_LABELS.get(i, f"Class {i}") for i in range(3)]
    )
    disp.plot(ax=ax, cmap='Blues', colorbar=True,
              xticks_rotation=45)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    ax.set_title('Confusion Matrix')
    
    plot_name = "confusion_matrix"
    plot_path = output_path / f"{plot_name}.{format}"
    fig.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"Saved confusion matrix: {plot_path}")
    
    if show_plot:
        plt.show()
        plt.close(fig)
    
    # Save matrix data
    matrix_data = {
        "matrix": cm.tolist(),
        "class_labels": [CATEGORY_LABELS.get(i, f"Class {i}") for i in range(3)],
        "total_samples": int(len(y_true)),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    matrix_path = output_path / "confusion_matrix_data.json"
    with open(matrix_path, "w") as f:
        import json
        json.dump(matrix_data, f, indent=2)
    
    logger.info(f"Saved confusion matrix data: {matrix_path}")
    
    return {
        "confusion_matrix_plot": str(plot_path),
        "matrix_data_path": str(matrix_path),
        "confusion_matrix": cm.tolist(),
        "output_directory": str(output_path),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def create_roc_curves(
    y_true: np.ndarray,
    y_score: np.ndarray,
    output_dir: str = "figures/roc_curves",
    format: str = "png",
    show_plot: bool = False
) -> Dict[str, str]:
    """Create ROC curves and AUC calculation.
    
    Args:
        y_true: Ground truth labels
        y_score: Predicted probabilities (shape: n_samples x n_classes)
        output_dir: Directory to save figures
        format: Output format ('png' or 'svg')
        show_plot: Whether to show plots
        
    Returns:
        Dictionary with plot paths and AUC scores
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Binarize labels for ROC
    y_true_bin = label_binarize(y_true, classes=[0, 1, 2])
    n_classes = y_true_bin.shape[1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SETTINGS["figsize"])
    
    colors = _get_colors()
    auc_scores = {}
    
    # Plot ROC curve for each class
    for i in range(n_classes):
        if y_score.shape[1] >= n_classes:
            display = RocCurveDisplay.from_predictions(
                y_true_bin[:, i], y_score[:, i],
                name=f"ROC curve for {CATEGORY_LABELS.get(i, i)}",
                ax=ax
            )
            if hasattr(display, "line_") and display.line_ is not None:
                display.line_.set_color(colors[i])
            auc = roc_auc_score(y_true_bin[:, i], y_score[:, i])
            auc_scores[CATEGORY_LABELS.get(i, str(i))] = float(auc)
            ax.plot([0, 1], [0, 1], 'k--', linestyle='--', alpha=0.5)
    
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves (One-vs-Rest)')
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    
    plot_name = "roc_curves"
    plot_path = output_path / f"{plot_name}.{format}"
    fig.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"Saved ROC curves: {plot_path}")
    
    if show_plot:
        plt.show()
        plt.close(fig)
    
    # Calculate macro-averaged AUC
    if len(auc_scores) > 0:
        macro_auc = np.mean(list(auc_scores.values()))
    else:
        macro_auc = 0.0
    
    # Save AUC scores
    auc_data = {
        "auc_scores": {k: float(v) for k, v in auc_scores.items()},
        "macro_auc": float(macro_auc),
        "n_classes": n_classes,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    auc_path = output_path / "auc_scores.json"
    with open(auc_path, "w") as f:
        import json
        json.dump(auc_data, f, indent=2)
    
    logger.info(f"Saved AUC scores: {auc_path}")
    
    return {
        plot_name: str(plot_path),
        "auc_scores": auc_scores,
        "macro_auc": float(macro_auc),
        "output_directory": str(output_path),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def create_comprehensive_dashboard(
    df: pd.DataFrame,
    model: Optional = None,
    X_test: Optional[np.ndarray] = None,
    y_test: Optional[np.ndarray] = None,
    y_pred: Optional[np.ndarray] = None,
    output_dir: str = "figures/dashboard",
    format: str = "png"
) -> Dict[str, str]:
    """Create a comprehensive visualization dashboard.
    
    Args:
        df: Input DataFrame
        model: Trained model (optional)
        X_test: Test features (optional)
        y_test: Test labels (optional)
        y_pred: Predictions (optional)
        output_dir: Directory to save figures
        format: Output format
        
    Returns:
        Dictionary with all plot paths
    """
    _set_style()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get features
    feature_cols = [col for col in df.columns 
                   if col not in ["id", "bg_class"] 
                   and df[col].dtype in ['int64', 'float64']]
    
    all_plots = {}
    
    # 1. Feature distributions
    all_plots.update(create_feature_distributions(
        df, feature_cols, "bg_class", output_dir, format, show_plot=False
    ))
    
    # 2. Correlation heatmap
    all_plots.update(create_correlation_heatmap(
        df, feature_cols, "bg_class", output_dir, format, show_plot=False
    ))
    
    # 3. Confusion matrix if model and predictions provided
    if model is not None and X_test is not None and y_test is not None:
        y_pred = y_pred if y_pred is not None else model.predict(X_test)
        
        all_plots.update(create_confusion_matrix(
            y_test, y_pred, output_dir, format, show_plot=False
        ))
        
        # 4. ROC curves
        y_score = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
        if y_score is not None:
            all_plots.update(create_roc_curves(
                y_test, y_score, output_dir, format, show_plot=False
            ))
        
        # 5. Decision boundaries
        if len(feature_cols) >= 2:
            all_plots.update(create_decision_boundaries(
                model, X_test, y_test, (0, 1), output_dir, format, show_plot=False
            ))
    
    # Create dashboard summary
    summary = {
        "dashboard_type": "comprehensive",
        "output_directory": str(output_path),
        "all_plots": all_plots,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Save summary
    summary_path = output_path / "dashboard_summary.json"
    with open(summary_path, "w") as f:
        import json
        json.dump(summary, f, indent=2)
    
    logger.info(f"Saved dashboard summary: {summary_path}")
    
    return all_plots


def save_figure(
    fig: plt.Figure,
    output_path: str,
    format: str = "png"
) -> str:
    """Save matplotlib figure to file.
    
    Args:
        fig: matplotlib Figure object
        output_path: Output file path
        format: Output format ('png', 'svg', 'pdf')
        
    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.savefig(output_path, bbox_inches='tight', format=format)
    plt.close(fig)
    
    logger.info(f"Saved figure to {output_path}")
    
    return str(output_path)


def export_visualizations(
    output_dir: str,
    format: str = "png"
) -> str:
    """Export all visualizations from standard directories.
    
    Args:
        output_dir: Base output directory
        format: Output format
        
    Returns:
        Path to export manifest
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Collect all figure files
    figure_files = []
    
    figure_dirs = [
        "figures/feature_distributions",
        "figures/correlation",
        "figures/confusion_matrix",
        "figures/roc_curves",
        "figures/decision_boundaries"
    ]
    
    for fig_dir in figure_dirs:
        fig_path = Path(fig_dir)
        if fig_path.exists():
            for file in fig_path.glob(f"*.{format}"):
                # Copy to output
                dest = output_path / file.name
                import shutil
                shutil.copy(file, dest)
                figure_files.append(str(dest))
    
    # Create manifest
    manifest = {
        "export_directory": str(output_path),
        "format": format,
        "files_exported": figure_files,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    manifest_path = output_path / "export_manifest.json"
    with open(manifest_path, "w") as f:
        import json
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Exported {len(figure_files)} figures to {output_path}")
    
    return str(manifest_path)


if __name__ == "__main__":
    # Example usage
    print("Testing visualization module...")
    
    # Import test data
    from src.data_loader import load_data
    
    df, _ = load_data(auto_fallback=True, random_state=42)
    
    # Create visualizations
    print("\nCreating feature distributions...")
    plot_paths = create_feature_distributions(
        df, 
        output_dir="figures/feature_distributions",
        format="png"
    )
    print(f"Saved plots: {list(plot_paths.keys())}")
    
    print("\nCreating correlation heatmap...")
    corr_result = create_correlation_heatmap(
        df,
        output_dir="figures/correlation",
        format="png"
    )
    print(f"Correlation heatmap saved: {corr_result['correlation_heatmap']}")
    
    print("\nVisualization tests complete!")
