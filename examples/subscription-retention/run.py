"""Generate synthetic data and execute the complete audited workflow."""
import argparse
from pathlib import Path
from workflow import SEED, generate_data, train_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/subscription-retention")
    parser.add_argument("--rows", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    source = output / "synthetic_data.csv"
    generate_data(args.rows, args.seed).to_csv(source, index=False)
    metrics, _, _ = train_file(source, output, args.seed)
    print(f"Synthetic demo complete: {output / 'report.md'}")
    print(f"Selected: {metrics['selected']}; test AUC: {metrics['partitions']['test']['selected_model']['roc_auc']:.4f}")
