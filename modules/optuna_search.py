import optuna


def suggest_hparams(trial: optuna.Trial, model_name: str) -> dict:
    output = {}

    list_models = [
        "RandomForest",
        "XGBoost",
        "LogisticRegression",
        "AdaBoost",
        # "SVM",
        "GradientBoosting",
        "DecisionTree",
    ]
    if model_name is None:
        output["model_name"] = trial.suggest_categorical("model", list_models)
    else:
        if model_name not in list_models:
            raise ValueError(
                f"Model {model_name} is not supported."
                + f" Supported models are: {list_models}"
            )
        output["model_name"] = model_name

    if output["model_name"] == "RandomForest":
        model_params = {}
        model_params["n_estimators"] = trial.suggest_int("n_estimators", 10, 200)
        model_params["criterion"] = trial.suggest_categorical(
            "criterion", ["gini", "entropy", "log_loss"]
        )
        model_params["max_features"] = trial.suggest_categorical(
            "max_features", ["sqrt", "log2"]
        )
        model_params["max_depth"] = trial.suggest_int("max_depth", 1, 20)
        model_params["min_samples_split"] = trial.suggest_int(
            "min_samples_split", 2, 10
        )
        model_params["min_samples_leaf"] = trial.suggest_int("min_samples_leaf", 1, 10)
        model_params["bootstrap"] = trial.suggest_categorical(
            "bootstrap", [True, False]
        )
        output["model_params"] = model_params
    elif output["model_name"] == "XGBoost":
        model_params = {}
        model_params["n_estimators"] = trial.suggest_int("n_estimators", 2, 200)
        model_params["max_depth"] = trial.suggest_int("max_depth", 1, 10)
        model_params["learning_rate"] = trial.suggest_float(
            "learning_rate", 0.0001, 0.3
        )
        model_params["subsample"] = trial.suggest_float("subsample", 0.5, 1.0)
        output["model_params"] = model_params
    elif output["model_name"] == "LogisticRegression":
        model_params = {}
        model_params["C"] = trial.suggest_float("C", 0.01, 10.0)
        model_params["solver"] = trial.suggest_categorical(
            "solver", ["liblinear", "saga"]
        )
        model_params["penalty"] = trial.suggest_categorical("penalty", ["l1", "l2"])

        output["model_params"] = model_params
    elif output["model_name"] == "AdaBoost":
        model_params = {}
        model_params["n_estimators"] = trial.suggest_int("n_estimators", 50, 200)
        model_params["learning_rate"] = trial.suggest_float("learning_rate", 0.01, 1.0)
        output["model_params"] = model_params
    elif output["model_name"] == "LightGBM":
        model_params = {}
        model_params["n_estimators"] = trial.suggest_int("n_estimators", 50, 200)
        model_params["max_depth"] = trial.suggest_int("max_depth", 3, 10)
        model_params["learning_rate"] = trial.suggest_float("learning_rate", 0.01, 0.3)
        model_params["subsample"] = trial.suggest_float("subsample", 0.5, 1.0)
        output["model_params"] = model_params
    elif output["model_name"] == "SVM":
        model_params = {}
        model_params["C"] = trial.suggest_float("C", 0.01, 10.0)
        model_params["kernel"] = trial.suggest_categorical(
            "kernel", ["linear", "rbf", "poly"]
        )
        model_params["gamma"] = trial.suggest_categorical("gamma", ["scale", "auto"])
        output["model_params"] = model_params
    elif output["model_name"] == "KNN":
        model_params = {}
        model_params["n_neighbors"] = trial.suggest_int("n_neighbors", 1, 20)
        model_params["weights"] = trial.suggest_categorical(
            "weights", ["uniform", "distance"]
        )
        model_params["algorithm"] = trial.suggest_categorical(
            "algorithm", ["auto", "ball_tree", "kd_tree", "brute"]
        )
        output["model_params"] = model_params
    elif output["model_name"] == "GradientBoosting":
        model_params = {}
        model_params["n_estimators"] = trial.suggest_int("n_estimators", 50, 200)
        model_params["max_depth"] = trial.suggest_int("max_depth", 3, 10)
        model_params["learning_rate"] = trial.suggest_float("learning_rate", 0.01, 0.3)
        model_params["subsample"] = trial.suggest_float("subsample", 0.5, 1.0)
        output["model_params"] = model_params
    elif output["model_name"] == "DecisionTree":
        model_params = {}
        model_params["max_depth"] = trial.suggest_int("max_depth", 1, 20)
        model_params["min_samples_split"] = trial.suggest_int(
            "min_samples_split", 2, 10
        )
        model_params["min_samples_leaf"] = trial.suggest_int("min_samples_leaf", 1, 10)
        output["model_params"] = model_params
    else:
        raise ValueError(f"Model {output['model_name']} is not supported.")

    return output
