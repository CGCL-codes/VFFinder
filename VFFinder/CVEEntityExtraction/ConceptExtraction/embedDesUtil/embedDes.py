

from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.treeBuild import tree_build
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.embedModel.deepwalkEmbed import deepwalk_embed
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.embedModel.sequenceEmbed import embed_treesequence
from CVEEntityExtraction.ConceptExtractionRAG.embedDesUtil.utils import convert_tree_to_networkx_with_sorted_child


autoencoder_model = load_trained_autoencoder()

def tree_embed(description_tree, embed_mode:str, treesequence_model=None):
    pass
    if embed_mode == "deepwalk":
        G = convert_tree_to_networkx_with_sorted_child(description_tree)
        return deepwalk_embed(G)
    if embed_mode == "treesequence":
        return embed_treesequence(description_tree, treesequence_model)


def embed_des(CVE_ID:str, description:str, nlp_model, componet_dir:str, embed_mode,  vul_simi_model, vul_dict_dir):
    """
    Embed the description into the model
    :param description: str, the description of the CVE
    :return: str, the embedded description
    """

    description_tree = tree_build(CVE_ID, description, nlp_model, componet_dir, vul_simi_model, vul_dict_dir)
    if embed_mode == "deepwalk":
        tree_embedding = tree_embed(description_tree, embed_mode)
    if embed_mode == "treesequence":
        tree_embedding = tree_embed(description_tree, embed_mode, treesequence_model=autoencoder_model)
    return tree_embedding

