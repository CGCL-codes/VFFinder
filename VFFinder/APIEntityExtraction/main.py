
import os.path
import sys
sys.path.append("../")
import spacy
from CommonUtils.FileUtils import parse_json_content, mk_opt_binary_dir
from APIEntityExtraction.utils import store_API_entity, enumerate_opt
from APIEntityExtraction.extractAPIEntity import extract_API_entity
from APIEntityExtraction.inline import inline_API_elemenet
from CommonUtils.GAVUtils import transfer_src_jar_GAV, GAV_CVE_dict
from tqdm import tqdm

API_json_dir = "../resource/VFContentJson"
CG_dir = "../resource/jarCG"
API_entity_dir = "../resource/APIEntity/APIEntity"


############Option for API entity extraction################

APIName = "APIName"
APIClz = "APIClz"
APIVar = "APIVar"
APIParaName = "APIParaName"
APIParaType = "APIParaType"
APIString = "APIString"
APIInline = "APIInline"

extraction_opt_dict = {

APIName: True,
APIClz: True,
APIVar: True,
APIParaName: False,
APIParaType: False,
APIString: True,
APIInline:True
}

#############################################################


def main():
    jar_API_dict = parse_json_content(API_json_dir)
    nlp = spacy.load('en_core_web_sm')
    opt_dict = extraction_opt_dict
    API_entity_opt_dir = mk_opt_binary_dir(API_entity_dir, opt_dict)
    for jar_name, API_list in tqdm(jar_API_dict.items()):
        GAV_name = transfer_src_jar_GAV(jar_name)
        if os.path.exists(os.path.join(API_entity_opt_dir, GAV_name)):
            print(f"API entity for {GAV_name} already exists")
            continue
        API_entity_list = []
        for api in API_list:
            api_entity = extract_API_entity(nlp, api, opt_dict)
            API_entity_list.append(api_entity)

        if opt_dict[APIInline]:
            bin_jar_name = jar_name.replace("-sources.jar", ".jar")
            jar_dir = os.path.join(CG_dir, bin_jar_name)
            for CVE in GAV_CVE_dict[GAV_name]:
                API_entity_list = inline_API_elemenet(CVE, API_entity_list, jar_dir, nlp)

        store_API_entity(API_entity_list, API_entity_opt_dir, GAV_name)


if __name__ == "__main__":
    main()