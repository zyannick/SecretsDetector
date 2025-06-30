from typing import Any, Dict, Tuple, Union
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import mlflow
import os
import seaborn as sns
import matplotlib.pyplot as plt
import ml_collections
import datetime

import joblib



def model_selector(model_name, model_params={}) -> Union[object, None]:
    print(f"Selecting model: {model_name} with params: {model_params}")
    if model_name == "RandomForest":
        from sklearn.ensemble import RandomForestClassifier

        return RandomForestClassifier(**model_params)
    elif model_name == "DecisionTree":
        from sklearn.tree import DecisionTreeClassifier

        return DecisionTreeClassifier(**model_params)
    elif model_name == "SVM":
        from sklearn.svm import SVC

        return SVC(**model_params)
    elif model_name == "KNN":
        from sklearn.neighbors import KNeighborsClassifier

        return KNeighborsClassifier(**model_params)
    elif model_name == "GradientBoosting":
        from sklearn.ensemble import GradientBoostingClassifier

        return GradientBoostingClassifier(**model_params)
    elif model_name == "AdaBoost":
        from sklearn.ensemble import AdaBoostClassifier

        return AdaBoostClassifier(**model_params)
    elif model_name == "XGBoost":
        from xgboost import XGBClassifier

        return XGBClassifier(**model_params)
    elif model_name == "LightGBM":
        from lightgbm import LGBMClassifier

        return LGBMClassifier(**model_params)
    elif model_name == "LogisticRegression":
        from sklearn.linear_model import LogisticRegression

        return LogisticRegression(**model_params)
    else:
        raise ValueError(f"Model {model_name} is not supported.")


class MachineLearningModel(object):
    """
    A class to represent a traditional machine learning model.
    """

    def __init__(
        self,
        global_configs: ml_collections.ConfigDict,
        model_name: str,
        model_params: Dict[str, Any] = {},
        trial_id=None,
    ):
        self.global_configs = global_configs
        model_params["random_state"] = self.global_configs.seed
        self.model = model_selector(model_name, model_params)
        if self.model is None:
            raise ValueError(f"Model {model_name} is not supported.")
        self.model_name = model_name
        self.model_params = model_params
        self.trial_id = trial_id
        self.trained = False
        self.metrics = {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None,
            "classification_report": None,
        }
        self.time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.experiment_name = "Experiment"
        self.experiment_path = os.path.join( # type: ignore
            self.global_configs.output_dir, # type: ignore
            "experiments",
            model_name,
            self.experiment_name,
            self.time_str,
        ) # type: ignore
        if not os.path.exists(self.experiment_path):
            os.makedirs(self.experiment_path)

    def __init_mlflow(self):
        print("Initializing logs for mlflow")

        if not os.path.exists(self.experiment_path):
            os.makedirs(self.experiment_path)

        def recursive_log_params(config, prefix=""):
            for key, value in config.items():
                if isinstance(value, dict):
                    recursive_log_params(value, prefix + key + ".")
                else:
                    mlflow.log_param(prefix + key, value)

        for key, value in self.model_params.items():
            try:
                if isinstance(value, dict):
                    recursive_log_params(value, key + ".")
                else:
                    mlflow.log_param(key, value)
            except Exception as err:
                try:
                    mlflow.log_param(key, str(value))
                except Exception as err:
                    print("Couldn't log {} because of {}".format(key, err))

        mlflow.log_param("trial_id", self.trial_id)
        mlflow.log_param("model_name", self.model_name)

        mlflow.log_param("data_path", self.experiment_path)
        runs = mlflow.search_runs()
        runs_csv_file = runs.to_csv(os.path.join(self.experiment_path, "mlflow.csv"))

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)

    def evaluate(self, X_test, y_test):
        y_pred = self.predict(X_test)

        self.metrics["accuracy"] = accuracy_score(y_test, y_pred)
        self.metrics["precision"] = precision_score(y_test, y_pred, average="weighted")
        self.metrics["recall"] = recall_score(y_test, y_pred, average="weighted")
        self.metrics["f1_score"] = f1_score(y_test, y_pred, average="weighted")
        self.metrics["classification_report"] = classification_report(y_test, y_pred)

        print("Classification Report:")
        print(self.metrics["classification_report"])

        result_confusion_matrix = confusion_matrix(y_test, y_pred)

        print("Confusion Matrix:")
        print(result_confusion_matrix)
        print("Accuracy:", self.metrics["accuracy"])
        print("Precision:", self.metrics["precision"])
        print("Recall:", self.metrics["recall"])
        print("F1 Score:", self.metrics["f1_score"])

        mlflow.log_metric("Accuracy", self.metrics["accuracy"])
        mlflow.log_metric("Precision", self.metrics["precision"])
        mlflow.log_metric("Recall", self.metrics["recall"])
        mlflow.log_metric("F1 Score", self.metrics["f1_score"])
        mlflow.log_param("model_name", self.model_name)
        mlflow.log_param("model_params", self.model_params)

        plt.figure(figsize=(10, 7))
        sns.heatmap(result_confusion_matrix, annot=True, fmt="d")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")
        plt.savefig(os.path.join(self.experiment_path, "confusion_matrix.png"))
        plt.close()

        mlflow.log_artifact(os.path.join(self.experiment_path, "confusion_matrix.png"))

        return self.metrics

    def train_evaluate(self, X_train, y_train, X_test, y_test):
        mlflow.set_experiment(self.experiment_name)
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        experiment_id = experiment.experiment_id

        with mlflow.start_run(experiment_id=experiment_id):
            self.__init_mlflow()

            self.train(X_train, y_train)
            self.evaluate(X_test, y_test)

        return self.metrics
