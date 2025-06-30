import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Argument parser for training scripts."
    )

    parser.add_argument(
        "--study_name",
        type=str,
        default="SecretsDetectorStudy",
        help="Name of the Optuna study.",
    )
    parser.add_argument(
        "--model_name", type=str, default=None, help="Name of the model."
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--n_trials", type=int, default=200, help="Number of Optuna trials."
    )
    parser.add_argument(
        "--target_metric",
        type=str,
        default="f1_score",
        help="Target metric for optimization.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save output files.",
    )

    return parser.parse_args()
