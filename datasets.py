from abc import ABC

import networkx as nx
import numpy as np
import pandas as pd
import torch
from nilearn.connectome import ConnectivityMeasure
from numpy.random import default_rng
from sklearn.preprocessing import RobustScaler
from torch_geometric.data import InMemoryDataset, Data

from scipy.stats import skew, kurtosis
from entropy import app_entropy, perm_entropy, sample_entropy, spectral_entropy, svd_entropy, \
    detrended_fluctuation, higuchi_fd, katz_fd, petrosian_fd
import nolds


from utils import Normalisation, ConnType, AnalysisType, EncodingStrategy
from utils_datasets import OLD_NETMATS_PEOPLE, DESIKAN_COMPLETE_TS, DESIKAN_TRACKS, UKB_IDS_PATH, UKB_PHENOTYPE_PATH, \
    UKB_TIMESERIES_PATH, NODE_FEATURES_NAMES, STRUCT_COLUMNS

PEOPLE_DEMOGRAPHICS_PATH = 'meta_data/people_demographics.csv'


def get_adj_50_path(person: int, index: int, ts_split: int):
    return f'/space/hcp_50_timeseries/processed_{ts_split}_split_50/{person}_{index}.npy'


def get_50_ts_path(person: int):
    return f'../hcp_timecourses/3T_HCP1200_MSMAll_d50_ts2/{person}.txt'


def get_desikan_tracks_path(person: int):
    return f'/space/desikan_tracks/{person}/{person}_conn_aparc+aseg_RS_sl.txt'


def get_desikan_ts_path(person: int, direction: str):
    return f'/space/desikan_timeseries/{person}_{direction}/{person}_rfMRI_REST{direction}_rfMRI_REST{direction}_hp2000_clean_T1_2_MNI2mm_shadowreg_aparc+aseg_nodes.txt'


def threshold_adj_array(adj_array: np.ndarray, threshold: int, num_nodes: int) -> np.ndarray:
    num_to_filter: int = int((threshold / 100.0) * (num_nodes * (num_nodes - 1) / 2))

    # For threshold operations, zero out lower triangle (including diagonal)
    adj_array[np.tril_indices(num_nodes)] = 0

    # Following code is similar to bctpy
    indices = np.where(adj_array)
    sorted_indices = np.argsort(adj_array[indices])[::-1]
    adj_array[(indices[0][sorted_indices][num_to_filter:], indices[1][sorted_indices][num_to_filter:])] = 0

    # Just to get a symmetrical matrix
    adj_array = adj_array + adj_array.T

    # Diagonals need connection of 1 for graph operations
    adj_array[np.diag_indices(num_nodes)] = 1.0

    return adj_array


def random_downsample(data_list: list) -> list:
    negative_num = len(list(filter(lambda x: x.y == 0, data_list)))
    positive_num = len(list(filter(lambda x: x.y == 1, data_list)))
    print("Negative class:", negative_num)
    print("Positive class:", positive_num)

    smallest_value = 1 if positive_num < negative_num else 0
    highest_value = 0 if positive_num < negative_num else 1

    if positive_num > negative_num:
        negative_num, positive_num = positive_num, negative_num

    # Randomly undersampling
    rng = default_rng(seed=0)
    numbers_sample = rng.choice(negative_num, size=positive_num, replace=False)

    y_0 = list(filter(lambda x: x.y == highest_value, data_list))
    data_list = list(filter(lambda x: x.y == smallest_value, data_list))
    y_0 = [elem for id, elem in enumerate(y_0) if id in numbers_sample]
    data_list.extend(y_0)

    return data_list

def calculate_stats_features(timeseries: np.ndarray) -> np.ndarray:
    assert timeseries.shape[1] > timeseries.shape[0]
    means = timeseries.mean(axis=1)
    variances = timeseries.std(axis=1)
    mins = timeseries.min(axis=1)
    maxs = timeseries.max(axis=1)
    skewnesses = skew(timeseries, axis=1)
    kurtos = kurtosis(timeseries, axis=1, bias=False)
    # Approximate entropy
    entro_app = np.apply_along_axis(app_entropy, 1, timeseries)
    # Permutation Entropy
    entro_perm = np.apply_along_axis(perm_entropy, 1, timeseries, normalize=True)
    # Sample Entropy
    entro_sample = np.apply_along_axis(sample_entropy, 1, timeseries)
    # Spectral Entropy with Fourier Transform
    entro_spectr = np.apply_along_axis(spectral_entropy, 1, timeseries, sf=1, normalize=True)
    # Singular Value Decomposition entropy
    entro_svd = np.apply_along_axis(svd_entropy, 1, timeseries, normalize=True)
    # Detrended fluctuation analysis (DFA)
    fractal_dfa = np.apply_along_axis(detrended_fluctuation, 1, timeseries)
    # Higuchi Fractal Dimension
    fractal_higuchi = np.apply_along_axis(higuchi_fd, 1, timeseries)
    # Katz Fractal Dimension.
    fractal_katz = np.apply_along_axis(katz_fd, 1, timeseries)
    # Petrosian fractal dimension
    fractal_petro = np.apply_along_axis(petrosian_fd, 1, timeseries)
    # Hurst Exponent
    hursts = np.apply_along_axis(nolds.hurst_rs, 1, timeseries)

    merged_stats = (means, variances, mins, maxs, skewnesses, kurtos, entro_app, entro_perm, entro_sample, entro_spectr,
                    entro_svd, fractal_dfa, fractal_higuchi, fractal_katz, fractal_petro, hursts)
    merged_stats = np.vstack(merged_stats).T
    return merged_stats

def normalise_timeseries(timeseries: np.ndarray, normalisation: Normalisation) -> np.ndarray:
    """
    :param normalisation:
    :param timeseries: In  format TS x N
    :return:
    """
    if normalisation == Normalisation.ROI:
        scaler = RobustScaler().fit(timeseries)
        timeseries = scaler.transform(timeseries).T
    elif normalisation == Normalisation.SUBJECT:
        flatten_timeseries = timeseries.flatten().reshape(-1, 1)
        scaler = RobustScaler().fit(flatten_timeseries)
        timeseries = scaler.transform(flatten_timeseries).reshape(timeseries.shape).T
    else:  # No normalisation
        timeseries = timeseries.T

    return timeseries


def create_thresholded_graph(adj_array: np.ndarray, threshold: int, num_nodes: int) -> nx.DiGraph:
    adj_array = threshold_adj_array(adj_array, threshold, num_nodes)

    return nx.from_numpy_array(adj_array, create_using=nx.DiGraph)


class BrainDataset(InMemoryDataset, ABC):
    def __init__(self, root, target_var: str, num_nodes: int, threshold: int, connectivity_type: ConnType,
                 normalisation: Normalisation, analysis_type: AnalysisType, time_length: int,
                 encoding_strategy: EncodingStrategy,
                 transform=None, pre_transform=None):
        if threshold < 0 or threshold > 100:
            print("NOT A VALID threshold!")
            exit(-2)
        if normalisation not in [Normalisation.NONE, Normalisation.ROI, Normalisation.SUBJECT]:
            print("BrainDataset not prepared for that normalisation!")
            exit(-2)

        self.target_var: str = target_var
        self.num_nodes: int = num_nodes
        self.connectivity_type: ConnType = connectivity_type
        self.time_length: int = time_length
        self.threshold: int = threshold
        self.normalisation: Normalisation = normalisation
        self.analysis_type: AnalysisType = analysis_type
        self.encoding_strategy: EncodingStrategy = encoding_strategy

        super(BrainDataset, self).__init__(root, transform, pre_transform)

    @property
    def raw_file_names(self):
        return []

    def download(self):
        # Download to `self.raw_dir`.
        pass


class HCPDataset(BrainDataset):
    def __init__(self, root, target_var: str, num_nodes: int, threshold: int, connectivity_type: ConnType,
                 normalisation: Normalisation, analysis_type: AnalysisType, time_length: int = 1200,
                 encoding_strategy: EncodingStrategy = EncodingStrategy.NONE,
                 transform=None, pre_transform=None):

        if target_var not in ['gender']:
            print("HCPDataset not prepared for that target_var!")
            exit(-2)
        if connectivity_type not in [ConnType.STRUCT]:
            print("HCPDataset not prepared for that connectivity_type!")
            exit(-2)
        if analysis_type not in [AnalysisType.ST_MULTIMODAL]:
            print("HCPDataset not prepared for that analysis_type!")
            exit(-2)

        self.ts_split_num: int = int(4800 / time_length)
        self.info_df = pd.read_csv(PEOPLE_DEMOGRAPHICS_PATH).set_index('Subject')
        self.nodefeats_df = pd.read_csv('meta_data/node_features_powtransformer.csv', index_col=0)

        super(HCPDataset, self).__init__(root, target_var=target_var, num_nodes=num_nodes, threshold=threshold,
                                         connectivity_type=connectivity_type, normalisation=normalisation,
                                         analysis_type=analysis_type, time_length=time_length,
                                         encoding_strategy=encoding_strategy,
                                         transform=transform, pre_transform=pre_transform)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def processed_file_names(self):
        return ['data_hcp_brain.dataset']

    def __create_data_object(self, person: int, ts: np.ndarray, ind: int, edge_index: torch.Tensor):
        assert ts.shape[0] > ts.shape[1]  # TS > N

        timeseries = normalise_timeseries(timeseries=ts, normalisation=self.normalisation)

        if self.encoding_strategy == EncodingStrategy.STATS:
            assert timeseries.shape == (self.num_nodes, self.time_length)
            timeseries = calculate_stats_features(timeseries)
            assert timeseries.shape == (self.num_nodes, 16)
            timeseries[np.isnan(timeseries)] = 0
            assert not np.isnan(timeseries).any()

        if self.analysis_type == AnalysisType.ST_UNIMODAL:
            x = torch.tensor(timeseries, dtype=torch.float)
        elif self.analysis_type == AnalysisType.ST_MULTIMODAL:
            x = [self.nodefeats_df.loc[person, [f'fs_{col}_{feat}' for feat in NODE_FEATURES_NAMES]].values
                 for col in STRUCT_COLUMNS]
            x = np.array(x)
            x = torch.tensor(np.concatenate((x, timeseries), axis=1), dtype=torch.float)

        if self.target_var == 'gender':
            y = torch.tensor([self.info_df.loc[person, 'Gender']], dtype=torch.float)
        data = Data(x=x, edge_index=edge_index, y=y)
        data.hcp_id = torch.tensor([person])
        data.index = torch.tensor([ind])

        return data

    def process(self):
        # Read data into huge `Data` list.
        data_list: list[Data] = []
        assert self.time_length == 1200

        # No sorted needed?
        if self.num_nodes == 50:
            print('TODO: This needs to be rethought')
            filtered_people = OLD_NETMATS_PEOPLE
            exit(-1)
        else:  # multimodal part
            filtered_people = sorted(list(set(DESIKAN_COMPLETE_TS).intersection(set(DESIKAN_TRACKS))))

        for person in filtered_people:
            if self.connectivity_type == ConnType.FMRI:
                print("ConnType.FMRI not ready now")
                exit(-2)

                all_ts = np.genfromtxt(get_50_ts_path(person))

                for ind, slice_start in enumerate(range(0, 4800, self.time_length)):
                    ts = all_ts[slice_start:slice_start + self.time_length, :]

                    corr_arr = np.load(get_adj_50_path(person, ind, ts_split=self.ts_split_num))
                    G = create_thresholded_graph(corr_arr, threshold=self.threshold, num_nodes=self.num_nodes)
                    edge_index = torch.tensor(np.array(G.edges()), dtype=torch.long).t().contiguous()

                    data = self.__create_data_object(person=person, ts=ts, ind=ind, edge_index=edge_index)

                    data_list.append(data)

            elif self.connectivity_type == ConnType.STRUCT:
                # arr_struct will only have values in the upper triangle
                idx_to_filter = np.concatenate((np.arange(0, 34), np.arange(49, 83)))
                arr_struct = np.genfromtxt(get_desikan_tracks_path(person))
                # Removing non-cortical areas
                arr_struct = arr_struct[idx_to_filter, :][:, idx_to_filter]

                G = create_thresholded_graph(arr_struct, threshold=self.threshold, num_nodes=self.num_nodes)
                edge_index = torch.tensor(np.array(G.edges()), dtype=torch.long).t().contiguous()

                for ind, direction in enumerate(['1_LR', '1_RL', '2_LR', '2_RL']):
                    ts = np.genfromtxt(get_desikan_ts_path(person, direction))
                    # Because of normalisation part
                    ts = ts.T
                    ts = ts[:, idx_to_filter]
                    assert ts.shape[0] == 1200
                    assert ts.shape[1] == 68

                    data = self.__create_data_object(person=person, ts=ts, ind=ind, edge_index=edge_index)

                    data_list.append(data)

        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])


class UKBDataset(BrainDataset):
    def __init__(self, root, target_var: str, num_nodes: int, threshold: int, connectivity_type: ConnType,
                 normalisation: Normalisation, analysis_type: AnalysisType, time_length=490,
                 transform=None, pre_transform=None):

        if target_var not in ['gender']:
            print("UKBDataset not prepared for that target_var!")
            exit(-2)
        if connectivity_type not in [ConnType.FMRI]:
            print("UKBDataset not prepared for that connectivity_type!")
            exit(-2)
        if analysis_type not in [AnalysisType.ST_UNIMODAL]:
            print("UKBDataset not prepared for that analysis_type!")
            exit(-2)

        super(UKBDataset, self).__init__(root, target_var=target_var, num_nodes=num_nodes, threshold=threshold,
                                         connectivity_type=connectivity_type, normalisation=normalisation,
                                         analysis_type=analysis_type, time_length=time_length, transform=transform,
                                         pre_transform=pre_transform)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def processed_file_names(self):
        return ['data_ukb_brain.dataset']

    #################################################
    def process(self):
        # Read data into huge `Data` list.
        data_list: list[Data] = []

        filtered_people = np.load(UKB_IDS_PATH)
        main_covars = pd.read_csv(UKB_PHENOTYPE_PATH).set_index('ID')

        conn_measure = ConnectivityMeasure(
            kind='correlation',
            vectorize=False)

        for person in filtered_people:
            if self.connectivity_type == ConnType.FMRI:
                ts = np.loadtxt(f'{UKB_TIMESERIES_PATH}/UKB{person}_ts_raw.txt', delimiter=',')
                if ts.shape[0] < 84:
                    continue
                elif ts.shape[1] == 523:
                    ts = ts[:, :490]
                assert ts.shape == (84, 490)

                # Getting only the last 68 cortical regions
                ts = ts[-68:, :]
                # For normalisation part and connectivity
                ts = ts.T

                corr_arr = conn_measure.fit_transform([ts])
                assert corr_arr.shape == (1, 68, 68)
                corr_arr = corr_arr[0]

                G = self.__create_thresholded_graph(corr_arr)
                edge_index = torch.tensor(np.array(G.edges()), dtype=torch.long).t().contiguous()

                timeseries = self.__normalise_timeseries(ts)
                x = torch.tensor(timeseries, dtype=torch.float)

                if self.target_var == 'gender':
                    y = torch.tensor([main_covars.loc[person, 'Sex']], dtype=torch.float)
                data = Data(x=x, edge_index=edge_index, y=y)
                data.ukb_id = torch.tensor([person])
                data.bmi = main_covars.loc[person, 'BMI.at.scan']
                data.age = main_covars.loc[person, 'Age.at.scan']
                data_list.append(data)

        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])


def create_ukb_corrs_flatten(num_nodes=376):
    final_dict = {}

    for person in np.load(UKB_IDS_PATH):
        corr_arr = None#np.load(f'{UKB_ADJ_ARR_PATH}/{person}.npy')

        # Getting upper triangle only (without diagonal)
        flatten_array = corr_arr[np.triu_indices(num_nodes, k=1)]

        final_dict[person] = flatten_array

    return final_dict


def create_hcp_correlation_vals(num_nodes=50, ts_split_num=64, binarise=False, threshold=100):
    final_dict = {}

    for person in OLD_NETMATS_PEOPLE:
        for ind in range(ts_split_num):
            corr_arr = np.load(get_adj_50_path(person, ind, ts_split=ts_split_num))

            if binarise:
                corr_arr = threshold_adj_array(corr_arr, threshold, num_nodes)
            # Getting upper triangle only (without diagonal)
            flatten_array = corr_arr[np.triu_indices(num_nodes, k=1)]

            if binarise:
                flatten_array[flatten_array != 0] = 1

            final_dict[(person, ind)] = flatten_array

    return final_dict
