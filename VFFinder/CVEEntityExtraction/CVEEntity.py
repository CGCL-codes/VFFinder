


class CVEEntity(object):
    def __init__(self):
        self.CVE_ID = ""
        self.CVE_description = ""
        self.clz_name = []
        self.AV = ''
        self.RC = ''
        self.IM = ''
        self.ven_pro_ver = ''
        self.entity_meaningless = []
        self.all_entity = []
        self.CWE_ID = ""


    def set_CVE_ID(self, CVE_ID):
        self.CVE_ID = CVE_ID

    def get_CVE_ID(self):
        return self.CVE_ID

    def set_CVE_description(self, CVE_description):
        self.CVE_description = CVE_description

    def get_CVE_description(self):
        return self.CVE_description

    def set_clz_name(self, clz_name):
        self.clz_name = clz_name

    def get_clz_name(self):
        return self.clz_name

    def set_vullogic(self, vullogic):
        self.vullogic = vullogic

    def get_vullogic(self):
        return self.vullogic

    def set_all_entity(self, all_entity):
        self.all_entity = all_entity

    def get_all_entity(self):
        return self.all_entity

    def set_atc_rc(self, atc_rc):
        self.atc_rc = atc_rc

    def get_atc_rc(self):
        return self.atc_rc

    def set_ven_pro_ver(self, ven_pro_ver):
        self.ven_pro_ver = ven_pro_ver

    def get_ven_pro_ver(self):
        return self.ven_pro_ver

    def set_entity_meaningless(self, entity_meaningless):
        self.entity_meaningless = entity_meaningless

    def get_entity_meaningless(self):
        return self.entity_meaningless

    def set_CWE_ID(self, CWE_ID):
        self.CWE_ID = CWE_ID

    def get_CWE_ID(self):
        return self.CWE_ID