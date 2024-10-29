
import sys
sys.path.append("../CVEEntityExtraction/")
sys.path.append("../")
import traceback
from CVEEntityExtraction.EntityExtraction import extract_entity_by_parts
from CVEEntityExtraction.EntityStore import store_entity
from CommonUtils.FileUtils import get_CVE_description, mk_opt_dir
from tqdm import tqdm
import os
import spacy
from CVEEntityExtraction.utils import CVE_entity_storage_dir, CVE_description_file_dir, CVE_CWE_dir


################## Opt for CVE entity extraction################
CoT = "CoT"
TF_IDF = "TF_IDF"
percentage = "percentage"
min_words = "min_words"
embed_mode = "embed_mode"

CVE_entity_extraction_dict = {
CoT: "RCAV_TMP",
embed_mode:"treesequence",
}
##############################################################


cve_part_dir = "//data/alan/VFlocation/resource/CVETree/CVEPart"

def filter_done_CVE(CVE_description_dict:dict, entity_storage_dir:str)->dict:
    '''
    Filter out the CVEs that have already been processed
    :param CVE_description_dict:
    :param entity_storage_dir:
    :return:
    '''
    done_CVE = set(os.listdir(entity_storage_dir))
    for CVE_ID in done_CVE:
        if CVE_ID in CVE_description_dict:
            del CVE_description_dict[CVE_ID]
    return CVE_description_dict


def main():
    CVE_description_dict = get_CVE_description(CVE_description_file_dir)
    CVE_entity_storage_opt_dir = mk_opt_dir(CVE_entity_storage_dir, CVE_entity_extraction_dict)
    nlp = spacy.load('en_core_web_sm')
    # CVE_description_dict = filter_done_CVE(CVE_description_dict, CVE_entity_storage_opt_dir)
    CVE_CWE_dict = {}
    with open(CVE_CWE_dir, "r") as f:
        for line in f.readlines():
            CVE, CWE = line.split(":")[0], line.split(":")[-1].strip()
            CVE_CWE_dict[CVE] = CWE
    for CVE_ID, description in tqdm(CVE_description_dict.items()):
        try:
            entity_list = extract_entity_by_parts(CVE_ID, description, CVE_CWE_dict, nlp, CVE_entity_extraction_dict, cve_part_dir=cve_part_dir)
        except Exception as e:
            print("Error encountered when extracting entity from " + CVE_ID)
            traceback.print_exc()
            continue

        store_entity(CVE_ID, entity_list, CVE_entity_storage_opt_dir)


if __name__ == "__main__":
    main()
