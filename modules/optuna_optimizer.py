import os


import sys
import pathlib
import dotenv

dotenv.load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
SECRETS_DETECTOR_ROOT = os.getenv(
    "SECRETS_DETECTOR_ROOT", default=pathlib.Path(__file__).parent.parent
)
print(SECRETS_DETECTOR_ROOT)
sys.path.append(SECRETS_DETECTOR_ROOT)
import pandas as pd
import numpy as np
import random

from modules.model_trainer import ModelTrainer

from argument_parser import parse_arguments
import optuna
import traceback
import copy
import ml_collections
import numpy as np
from modules.optuna_search import suggest_hparams
import yaml

def setting_seed(reproducibility_seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(reproducibility_seed)
    np.random.seed(reproducibility_seed)
    random.seed(reproducibility_seed)


setting_seed(42)

arguments = parse_arguments()


def create_and_optimize_study(trials) -> None:
    def objective(trial: optuna.Trial) -> float:
        suggestions = suggest_hparams(trial, arguments.model_name)
        model_name = suggestions["model_name"]
        model_params = suggestions["model_params"]
        config = {}
        config.update(vars(arguments))
        config["model_name"] = model_name
        for key, value in model_params.items():
            config[key] = value

        config["trial_id"] = trial.number

        ml_collections_config = ml_collections.ConfigDict(config)

        model_trainer = ModelTrainer(
            config=ml_collections_config, model_params=model_params
        )

        loss = model_trainer.run()

        return loss

    storage_path = os.path.join(
        SECRETS_DETECTOR_ROOT, arguments.output_dir, "optuna_study.db"
    )
    storage = f"sqlite:///{storage_path}"

    study = optuna.create_study(
        study_name=arguments.study_name,
        load_if_exists=True,
        direction="minimize",
        storage=storage,
    )

    study.optimize(
        objective,
        n_trials=trials,
        gc_after_trial=True,
        show_progress_bar=True,
    )

    print(f"Best params: {study.best_params}")

    best_params_path = os.path.join(
        SECRETS_DETECTOR_ROOT, arguments.output_dir, "best_params.yaml"
    )
    with open(best_params_path, "w") as f:
        yaml.dump(study.best_params, f)
        
    config_path = os.path.join(
        SECRETS_DETECTOR_ROOT, arguments.output_dir, "best_config.yaml"
    )
    with open(config_path, "w") as f:
        yaml.dump(vars(arguments), f)

    study.optimize(objective, n_trials=trials, n_jobs=1)


if __name__ == "__main__":
    if not os.path.exists(arguments.output_dir):
        os.makedirs(arguments.output_dir)

    print(f"Starting Optuna study with {arguments.n_trials} trials...")
    print(f"Study name: {arguments.study_name}")
    print(f"Output directory: {arguments.output_dir}")
    create_and_optimize_study(arguments.n_trials)
