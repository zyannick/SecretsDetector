import os


import sys
import pathlib

import dotenv

dotenv.load_dotenv(pathlib.Path(__file__).parent.parent / ".env")


SECRETS_DETECTOR_ROOT = os.getenv(
    "SECRETS_DETECTOR_ROOT", default=pathlib.Path(__file__).parent.parent
)

sys.path.append(SECRETS_DETECTOR_ROOT)
import numpy as np
import random
from modules.machine_learning_model import MachineLearningModel
import ml_collections
from typing import Dict, Any

import string
import re
from entropy import analyze_string
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
import yaml
import json


def get_features(s: str):
    analysis = analyze_string(s)
    features = [
        sum(c.isdigit() for c in s) / len(s),
        sum(c.islower() for c in s) / len(s),
        sum(c.isupper() for c in s) / len(s),
        sum(c in string.punctuation for c in s) / len(s),
        analysis["overall_entropy"],
        analysis["max_substring_entropy"],
        float(analysis["high_entropy_regions"]),
        float(analysis["cpp_heuristic_is_secret"]),
        float(analysis["is_base64_pattern"]),
        len(s),
    ]
    return features


def extract_candidate_from_line(line: str):
    patterns = [
        r'["\'](.*?)["\']',
        r"[:=]\s*(\S+)",
        r"(\S+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            for group in match.groups():
                if group:
                    return group
    return line


class ModelTrainer:
    def __init__(
        self,
        config: ml_collections.ConfigDict,
        model_params: Dict[str, Any],
        is_best_model: bool = False,
    ):
        reproducibility_seed = config.seed
        os.environ["PYTHONHASHSEED"] = str(reproducibility_seed)
        np.random.seed(reproducibility_seed)
        random.seed(reproducibility_seed)

        self.model_params = model_params
        self.is_best_model = is_best_model
        self.model_name = config.model_name
        self.model = MachineLearningModel(config, self.model_name, model_params)
        self.config = config

    @staticmethod
    def load_model_and_predict(text_line: str):
        try:
            model_path = os.path.join(
                SECRETS_DETECTOR_ROOT, "output", "secret_classifier.pkl"
            )
            model = joblib.load(model_path)
            candidate_string = extract_candidate_from_line(text_line)
            features = [get_features(candidate_string)]
            probability_is_secret = model.predict_proba(features)[0][1]
            is_secret = probability_is_secret >= 0.5
            return is_secret, probability_is_secret
        except FileNotFoundError:
            print("[WARNING] ML model not found. Skipping false positive check.")
            return True, 1.0

    def run(self):
        df = pd.read_csv("secrets_dataset.csv")

        print("Extracting features...")
        df["candidate"] = df["text"].apply(extract_candidate_from_line)
        features = df["candidate"].apply(get_features).tolist()
        labels = df["label"].tolist()

        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )

        target_metric_value = []

        metrics = self.model.train_evaluate(
            X_train,
            y_train,
            X_test,
            y_test,
        )
        target_metric_value.append(metrics[self.config.target_metric])

        if len(target_metric_value) == 0:
            raise ValueError("No target metric values found. Check your data splits.")

        mean_target_metric_value = sum(target_metric_value) / len(target_metric_value)

        loss_metric = 1 - mean_target_metric_value

        if self.is_best_model:
            metrics_path = os.path.join(
                SECRETS_DETECTOR_ROOT, self.config.output_dir, "metrics.json"
            )

            with open(metrics_path, "w") as f:
                json.dump(metrics, f)
            model_path = os.path.join(
                SECRETS_DETECTOR_ROOT, self.config.output_dir, "secret_classifier.pkl"
            )
            joblib.dump(self.model.model, model_path)
            print(f"Model saved to {model_path}")

        return loss_metric


if __name__ == "__main__":

    best_model_params_path = "output/best_params.yaml"
    best_config_path = "output/best_config.yaml"
    if os.path.exists(best_model_params_path):
        with open(best_model_params_path, "r") as f:
            best_model_params = yaml.safe_load(f)
    else:
        raise FileNotFoundError(
            f"Best model parameters file not found: {best_model_params_path}"
        )

    print(f"Best model parameters: {best_model_params}")

    if os.path.exists(best_config_path):
        with open(best_config_path, "r") as f:
            best_config = yaml.safe_load(f)
        best_config["model_name"] = best_model_params.pop("model")
    else:
        raise FileNotFoundError(f"Best config file not found: {best_config_path}")

    print(f"Best config: {best_config}")

    model_trainer = ModelTrainer(
        config=ml_collections.ConfigDict(best_config),
        model_params=best_model_params,
        is_best_model=True,  
    )
    loss = model_trainer.run()
    print(f"Final loss: {loss}")

