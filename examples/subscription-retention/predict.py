"""Score a complete feature-only CSV using the frozen plain JSON model."""
import argparse
from pathlib import Path
import pandas as pd
from workflow import load_model, predict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = predict(pd.read_csv(args.input), load_model(args.model))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Scored {len(result)} rows: {args.output}")
