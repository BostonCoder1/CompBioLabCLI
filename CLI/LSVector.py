from .load_files import load_family, load_ls_file, is_pf


class LSVector:
    def __init__(self, ls_name, ls_data=None):
        self.ls_name = ls_name
        if ls_data is None:
            self.ls_data = self.load_vector()
        else:
            self.ls_data = ls_data

    def load_vector(self):
        if is_pf(self.ls_name):
            return load_family(self.ls_name + '.txt')
        else:
            return load_ls_file(self.ls_name)
