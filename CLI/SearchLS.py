from scipy.spatial import distance
from .SearchOutput import SearchOutput
from .load_files import load_ls_file, latent_space_list, load_family


class SearchLS:
    def __init__(self, ls, metric, p_norm):
        self.ls_name = ls
        self.ls_data = load_ls_file(ls)
        self.metric = metric
        self.p_norm = p_norm
        self.result = self.do_search()

    def do_search(self):
        min_dist = float("inf")
        for i in range(len(latent_space_list)):
            if self.metric == distance.minkowski:
                distance_result = self.metric(self.ls_data, load_family(latent_space_list[i]), self.p_norm)
            else:
                distance_result = self.metric(self.ls_data, load_family(latent_space_list[i]))

            if distance_result < min_dist:
                min_dist = distance_result
                closest_family = latent_space_list[i]
        return SearchOutput(self.ls_name, self.metric.__name__, closest_family[:-4], str(min_dist))
