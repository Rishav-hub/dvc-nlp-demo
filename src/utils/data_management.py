import logging
from tqdm import tqdm
import random
import xml.etree.ElementTree as ET
import re
def process_posts(fd_in, fd_out_train, fd_out_test, target_tag, split):
    for line in tqdm(fd_in):
        try:
            fd_out = fd_out_train if random.random() > split else fd_out_test
            attr = ET.fromstring(line).attrib

            pid = attr.get("Id", "")
            label = 1 if target_tag in attr.get("Tags", "") else 0
            title = re.sub(r"\s+", " ", attr.get("Title", "").strip())
            body = re.sub(r"\s+", " ", attr.get("Body", "").strip())
            text = title + " " + body
            fd_out.write("{}\t{}\t{}\n".format(pid, label, text))
        except Exception as e:
            logging.exception("Skiping the broken line while processg line: {}".format(line))
            logging.error(line)
            continue    


