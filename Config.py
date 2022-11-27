import os
import numpy as np
import torch

MANIFOLD_DIR = '/Manifold/build'  # path to manifold software (https://github.com/hjwdzh/Manifold)

class Args(object):

    # HParams - files
    fix_sample_cnt = 4096  # for now [2048, 4096] from sdf_try.py
    data_path = '/data/processed/%d' %(fix_sample_cnt)
    complete_path = os.path.join(data_path, '04_query_npz')
    partial_path = os.path.join(data_path, '05_als_npz')
    save_path = "/data/processed/%s/net_outputs/checkpoints" %(fix_sample_cnt)

    # HParams - Rec
    torch_seed = 5
    samples = 15000  # number of points to sample reconstruction with ???
    initial_mesh = None  # if available, replace this with path
    initial_num_faces = 2000
    init_samples = 10000
    iterations = 1000
    upsamp = 1000  # upsample each {upsamp}th iteration
    max_faces = 10000  # maximum number of faces to upsample to
    faces_to_part = [8000, 16000, 20000]  # after how many faces to split

    # HParams - net
    gpu = 0
    lr = 1.1e-4
    ang_wt = 1e-1  # weight of the cosine loss for normals
    res_blks = 3
    lrelu_alpha = 0.01
    local_non_uniform = 0.1  # weight of local non uniform loss
    convs = [16, 32, 64, 64, 128]
    pools = [0.0, 0.0, 0.0, 0.0]  # percent to pool from orig. resolution in each layer')
    transfer_data = True
    overlap = 0  # overlap for bfs
    global_step = True  #perform the optimization step after all the parts are forwarded (only matters if nparts > 2)
    manifold_res = 50000  # resolution for manifold upsampling
    unoriented = True  # take the normals loss term without any preferred orientation
    init_weights = 0.002
    export_interval = 100
    beamgap_iterations = 0  # the num of iters to which the beamgap loss will be calculated
    beamgap_modulo = 1  # skip iterations with beamgap loss, calc beamgap when: iter % (beamgap-modulo) == 0
    manifold_always = True  # always run manifold even when the maximum number of faces is reached

    if not os.path.exists(save_path):
        os.makedirs(save_path)

def get_num_parts(Args, num_faces):
    lookup_num_parts = [1, 2, 4, 8]
    num_parts = lookup_num_parts[np.digitize(num_faces, Args.faces_to_part, right=True)]
    return num_parts

def dtype():
    return torch.float32

def get_num_samples(Args, cur_iter):
    slope = (Args.samples - Args.begin_samples) / int(0.8 * Args.upsamp)
    return int(slope * min(cur_iter, 0.8 * Args.upsamp)) + Args.begin_samples