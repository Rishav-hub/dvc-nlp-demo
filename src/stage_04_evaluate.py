import argparse
import os
import math
from tqdm import tqdm
import logging
from src.utils.all_utils import read_yaml, create_directory, save_reports
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve

STAGE = "Four"

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )

def main(config_path):
    config = read_yaml(config_path)
    # params = read_yaml(params_path)

    artifacts = config["artifacts"]
    featurized_data_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"], artifacts["FEATURIZED_DATA"])
    featurized_test_data_path = os.path.join(featurized_data_dir_path, artifacts["FEATURIZED_OUT_TEST"])


    model_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"], artifacts["MODEL_DIR"])
    model_path = os.path.join(model_dir_path, artifacts["MODEL_NAME"])

    # Load matrix
    matrix = joblib.load(featurized_test_data_path)


    # Load model
    model = joblib.load(model_path)

    labels = np.squeeze(matrix[:, 1].toarray())
    X = matrix[:,2:]

    # Predict
    predictions_by_class = model.predict_proba(X)
    predictions = predictions_by_class[:, 1]

    PRC_json_path = config['plots']['PRC']
    ROC_json_path = config['plots']['ROC']
    scores_json_path = config['metrics']['SCORES']


    avg_prec = average_precision_score(labels, predictions)
    roc_auc = roc_auc_score(labels, predictions)

    scores = {
        "avg_prec": avg_prec,
        "roc_auc": roc_auc
    }
    save_reports(scores, scores_json_path)

    # PRC
    precision, recall, thresh = precision_recall_curve(labels, predictions)

    nth_point = math.ceil(len(thresh)/1000)
    prc_points = list(zip(precision, recall, thresh))[::nth_point]

    prc_data = {
        "prc": [
            {"precision": p, "recall": r, "threshold": t}
            for p, r, t in prc_points
        ]
    }
    
    save_reports(prc_data, PRC_json_path)
    
    fpr, tpr, roc_threshold = roc_curve(labels, predictions)

    roc_data = {
        "roc": [
            {"fpr": fp, "tpr": tp, "threshold": t}
            for fp, tp, t in zip(fpr, tpr, roc_threshold)
        ]
    }

    save_reports(roc_data, ROC_json_path)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="config/config.yaml")
    # args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main(config_path=parsed_args.config)
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e