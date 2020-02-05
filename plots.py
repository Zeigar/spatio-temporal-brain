import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import roc_curve, auc, roc_auc_score, classification_report

NAME_MODEL_LOSS = 'gender_2_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_20_5_roi_norm_150_False_272_struct'
NAME_MODEL_AUC = 'gender_2_0_auc_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.5_20_5_roi_norm_150_False_272_struct'

labels_auc = np.load('labels_' + NAME_MODEL_AUC + '.npy')
preds_auc = np.load('predictions_' + NAME_MODEL_AUC + '.npy')

labels_loss = np.load('labels_' + NAME_MODEL_LOSS + '.npy')
preds_loss = np.load('predictions_' + NAME_MODEL_LOSS + '.npy')

fpr_auc, tpr_auc, _ = roc_curve(labels_auc, preds_auc)
roc_auc = auc(fpr_auc, tpr_auc)
fpr_loss, tpr_loss, _ = roc_curve(labels_loss, preds_loss)
roc_loss = auc(fpr_loss, tpr_loss)

plt.figure()
plt.plot(fpr_auc, tpr_auc, color='darkorange', lw=2, label=f'ROC curve for AUC (area = {round(roc_auc, 3)})')
plt.plot(fpr_loss, tpr_loss, color='darkred', lw=2, label=f'ROC curve for Loss (area = {round(roc_loss, 3)})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()


#######################
#######################

ordered_named_results = [
'gender_1_0_loss_D_0.5__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0.5__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0.005_30_20_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',

'gender_1_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_1e-05_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_1e-05_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_1_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',


'gender_2_0_loss_D_0.5__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0.5__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',

'gender_2_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_1e-05_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_1e-05_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_2_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',


'gender_3_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_1e-05_0.005_30_20_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',

'gender_3_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_1e-05_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_3_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',


'gender_4_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',

'gender_4_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_4_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy',


'gender_5_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.5__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_False__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',

'gender_5_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_5_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.7__A_relu__P_mean__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0_30_20_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_5_roi_norm_500_False_50_fmri.npy',
'gender_5_0_loss_D_0.7__A_relu__P_diff_pool__CS_entire__CHC_8__FS_True__GCN_True__GAT_False_0.0001_0.005_30_20_roi_norm_500_False_50_fmri.npy'
]

import warnings
warnings.filterwarnings("ignore")
for i, name in enumerate(['mean_5', 'mean_20', 'diff_5', 'diff_20', 'gcn_mean_5', 'gcn_mean_20', 'gcn_diff_5', 'gcn_diff_20']):
    print(name, ':')

    all_rocs = []
    all_specificities = []
    all_sensitivities = []
    for fold, ord_index in enumerate(range(i, 40, 8)):
        name = ordered_named_results[ord_index]
        labels = np.load('results/labels_' + name)
        predictions = np.load('results/predictions_' + name)
        pred_binary = np.where(predictions > 0.5, 1, 0)

        roc_auc = round(roc_auc_score(labels, predictions), 4)
        all_rocs.append(roc_auc)

        report = classification_report(labels, pred_binary, output_dict=True)
        sens = round(report['1.0']['recall'], 4)
        all_sensitivities.append(sens)
        spec = round(report['0.0']['recall'], 4)
        all_specificities.append(spec)

        print('fold', fold, ':', roc_auc, 'Sens:', sens, 'Spec:', spec)

    print("roc :", round(np.mean(all_rocs), 3), "(", round(np.std(all_rocs), 3), ")")
    print("sens :", round(np.mean(all_sensitivities), 3), "(", round(np.std(all_sensitivities), 3), ")")
    print("spec :", round(np.mean(all_specificities), 3), "(", round(np.std(all_specificities), 3), ")")
    print()


########################
########################
# Adapted from https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc_crossval.html
from scipy import interp
tprs = []
aucs = []
mean_fpr = np.linspace(0, 1, 100)

fig, ax = plt.subplots()
for fold, ord_index in enumerate(range(4, 40, 8)):
    name = ordered_named_results[ord_index]
    labels = np.load('results/labels_' + name)
    predictions = np.load('results/predictions_' + name)

    fpr, tpr, _ = roc_curve(labels, predictions)
    roc_val = auc(fpr, tpr)

    ax.plot(fpr, tpr, lw=2, alpha=0.5, label=f'Roc fold {fold}')
    interp_tpr = interp(mean_fpr, fpr, tpr)
    interp_tpr[0] = 0.0
    tprs.append(interp_tpr)
    aucs.append(roc_val)

ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
            label='Chance', alpha=.8)

mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0
mean_auc = auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)
ax.plot(mean_fpr, mean_tpr, color='b',
        label=r'Mean ROC (AUC = %0.3f $\pm$ %0.3f)' % (mean_auc, std_auc),
        lw=2, alpha=.8)

std_tpr = np.std(tprs, axis=0)
tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                label=r'$\pm$ 1 std. dev.')

ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05])#,
       #title="Receiver Operating Characteristic curves for ST-mean")
ax.legend(loc="lower right")
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
plt.tight_layout()
plt.savefig('rocs_st_mean.pdf', bbox_inches = 'tight', pad_inches = 0)
plt.show()

########################
########################
def get_adj_50_path(person, index):
    return f'../../../space/hcp_50_timeseries/processed_4_split_50/{person}_{index}.npy'

def get_50_ts_path(person):
    return f'../hcp_timecourses/3T_HCP1200_MSMAll_d50_ts2/{person}.txt'
person = 100206
all_ts = np.genfromtxt(get_50_ts_path(person))
t1 = all_ts[:1200, :]

import pandas as pd
plt.rcParams.update({'font.size': 17})
#fig, axes = plt.subplots(1, 2)
#
plt.figure(figsize=(6,6))
data = {'ICA_1' : t1[:,0], 'ICA_2' : t1[:,1], 'ICA_25' : t1[:,24], 'ICA_50' : t1[:,49]}
df = pd.DataFrame(data)
axes = df.plot(subplots=True, figsize=(6, 6), legend=False)
for ax in axes:
    ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig('50_50_timeseries_example.pdf', bbox_inches = 'tight', pad_inches = 0)
#
corr_arr = np.load(get_adj_50_path(100206, 0))
corr_arr[np.tril_indices(50)] = 0
corr_arr_5 = corr_arr.copy()

num_to_filter_5 = int((5 / 100.0) * (50 * (50 - 1) / 2))
num_to_filter_20 = int((20 / 100.0) * (50 * (50 - 1) / 2))
indices = np.where(corr_arr)
sorted_indices = np.argsort(corr_arr[indices])[::-1]
corr_arr[(indices[0][sorted_indices][num_to_filter_20:], indices[1][sorted_indices][num_to_filter_20:])] = 0
corr_arr[corr_arr > 0] = 1

corr_arr_5[(indices[0][sorted_indices][num_to_filter_5:], indices[1][sorted_indices][num_to_filter_5:])] = 0
corr_arr_5[corr_arr_5 > 0] = 2

corr_arr[corr_arr_5 == 2] = 2

import matplotlib.patches as mpatches
plt.rcParams.update({'font.size': 20})
plt.figure(figsize=(6,6))
im = plt.imshow(corr_arr, cmap='viridis')

patches = [ mpatches.Patch(color=im.cmap(im.norm(0)), label='No correlation'),
            mpatches.Patch(color=im.cmap(im.norm(2)), label='With 5% threshold'),
            mpatches.Patch(color=im.cmap(im.norm(1)), label='With 20% threshold')
            ]
# put those patched as legend-handles into the legend
plt.legend(handles=patches, loc='lower left', prop={"size":20})
plt.tight_layout()
plt.savefig('50_threshold_example.pdf', bbox_inches = 'tight', pad_inches = 0)