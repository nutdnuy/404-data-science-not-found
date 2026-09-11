"""Train and evaluate from the documented synthetic CSV schema."""
import argparse
from workflow import SEED, train_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    train_file(args.data, args.output_dir, args.seed)
    print(f"Training and evaluation complete: {args.output_dir}")
