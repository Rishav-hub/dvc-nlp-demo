import argparse
import os
import shutil
from tqdm import tqdm
import logging
from src.utils.all_utils import read_yaml, create_directory
from src.utils.data_management import process_posts
import random

logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, 'running_logs.log'), level=logging.INFO, format=logging_str,
                    filemode="a")

def main(config_path, params_path):
    """
    Main function for stage_01_prepare.py to convert xml to tsv
    :param config_path: path to config file
    :config_path type: str
    """
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    source_data = config['source_data']
    input_data = os.path.join(source_data['data_dir'], source_data['data_file'])

    split = params['prepare']['split']
    seed = params['prepare']['seed']

    random.seed(seed)

    artifacts = config['artifacts']
    prepare_data_dir_path = os.path.join(artifacts['ARTIFACTS_DIR'], artifacts['PREPARED_DATA'])

    create_directory([prepare_data_dir_path])

    train_data_path = os.path.join(prepare_data_dir_path, artifacts['TRAIN_DATA'])
    test_data_path = os.path.join(prepare_data_dir_path, artifacts['TEST_DATA'])

    with open(input_data, encoding="utf8") as fd_in:
        with open(train_data_path, "w", encoding="utf8") as fd_out_train:
            with open(test_data_path, "w",encoding="utf8") as fd_out_test:
                    process_posts(fd_in, fd_out_train, fd_out_test, "<python>",split)
                
        




    

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="config/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")

    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(">>>>> stage one started <<<<<")
        main(config_path=parsed_args.config, params_path=parsed_args.params)
        logging.info(">>>>> stage one completed! all the data are saved in local <<<<<n")
    except Exception as e:
        logging.exception(e)
        raise e