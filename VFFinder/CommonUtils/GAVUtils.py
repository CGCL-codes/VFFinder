

src_jar_GAV_dict = {}
bin_jar_GAV_dict = {}

with open("//data/alan/VFlocation/resource/CVE_jar", "r") as f:
    GAV_list = [i.split("@")[-1].strip() for i in f.readlines()]

with open("//data/alan/VFlocation/resource/CVE_jar", "r") as f:
    CVE_GAV_dict = {i.split("@")[0].strip(): i.split("@")[-1].strip() for i in f.readlines()}

with open("//data/alan/VFlocation/resource/CVE_jar", "r") as f:
    GAV_CVE_dict = {}
    for i in f.readlines():
        GAV = i.split("@")[-1].strip()
        CVE = i.split("@")[0].strip()
        if GAV in GAV_CVE_dict:
            GAV_CVE_dict[GAV].append(CVE)
        else:
            GAV_CVE_dict[GAV] = [CVE]

for GAV in GAV_list:
    G,A,V = GAV.split(":")
    src_jar_name = A + "-" + V + "-sources.jar"
    bin_jar_name = A + "-" + V + ".jar"
    src_jar_GAV_dict[src_jar_name] = GAV
    bin_jar_GAV_dict[bin_jar_name] = GAV


def transfer_src_jar_GAV(jar_name:str):
    return src_jar_GAV_dict[jar_name]


def transfer_bin_jar_GAV(jar_name:str):
    return bin_jar_GAV_dict[jar_name]


def transfer_GAV_src_jar(GAV:str):
    G, A, V = GAV.split(":")
    src_jar_name = A + "-" + V + "-sources.jar"
    return src_jar_name


def transfer_GAV_bin_jar(GAV:str):
    G, A, V = GAV.split(":")
    bin_jar_name = A + "-" + V + ".jar"
    return bin_jar_name