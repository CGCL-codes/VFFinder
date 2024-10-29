

class API(object):
    def __init__(self):
        self.name = ""
        self.file_name = ""
        self.misc_content = ""
        self.source = ""
        self.description = ""
        self.para_name_list = []
        self.para_type_list = []

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_misc_content(self):
        return self.misc_content

    def set_misc_content(self, misc_content):
        self.misc_content = misc_content

    def get_source(self):
        return self.source

    def set_source(self, source):
        self.source = source

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_file_name(self):
        return self.file_name

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_para_name_list(self):
        return self.para_name_list

    def set_para_name_list(self, para_name_list):
        self.para_name_list = para_name_list

    def get_para_type_list(self):
        return self.para_type_list

    def set_para_type_list(self, para_type_list):
        self.para_type_list = para_type_list

    def get_para_type_str(self):
        return ":".join(self.para_type_list)