
import os.path
import pickle
from CVEEntityExtraction.CVEEntity import CVEEntity


def store_entity(CVE_ID:str, CVE_entity: CVEEntity, entity_storage_dir:str):

    '''

    :param entity_dict:
    :return:
    '''
    with open(os.path.join(entity_storage_dir, CVE_ID), "wb") as f:
        pickle.dump(CVE_entity, f)
    print(CVE_ID + " Entity stored successfully!")


def store_logic(CVE_ID:str, CVE_logic: str, entity_storage_dir:str):
    with open(os.path.join(entity_storage_dir, CVE_ID), "w") as f:
        f.write(CVE_logic)
    print(CVE_ID + " Logic stored successfully!")