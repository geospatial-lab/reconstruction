import logging
from datetime import datetime
from pathlib import Path

class Args(object):

    # HParams - files
    experiment_dir = Path('/outputs/experiments/ISPRS_R1')
    experiment_dir.mkdir(exist_ok=True)
    file_dir = Path(str(experiment_dir) + '/' + str(datetime.now().strftime('%Y-%m-%d_%H-%M')))
    file_dir.mkdir(exist_ok=True)
    ckpts_dir = file_dir.joinpath('checkpoints/')
    ckpts_dir.mkdir(exist_ok=True)
    log_dir = file_dir.joinpath('logs/')
    log_dir.mkdir(exist_ok=True)

    record_step = 2  # print/log the model info/metrics every ...
    # save_interval = 10  # save every ...
    val_interval = 2  # run the validation model every ...
    # p2p_interval = 10
    # p2p = True
    tr_loss = 'cdp' # cdp, dcd, emd
    # t_alpha = 200
    # n_lambda = 0.5

    # HParams - net
    gpu = 0
    lr = 0.0006
    eta_min = 0.0000001
    wd = 0.01  # weight decay (AdamW default)
    max_epoch = 140
    bs = 8  # batch_size
    npoints = 2048  # number of input points

    #HParams - chkpnting
    load_chkpnt = False
    chkpnt_path = '/outputs/experiments/2023-02-01_07-58/checkpoints/pccnet_128_0.01709_0.00082.pth'
    fix_lr = 0.00007 
    if load_chkpnt:
        val_interval = 1

def start_logger(log_dir, fname):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # logging to file
    file_handler = logging.FileHandler(str(log_dir) + '/%s_log.txt'%(fname))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(message)s'))  # %(asctime)s - %(levelname)s -
    logger.addHandler(file_handler)

    # logging to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('\t\t %(message)s'))
    logger.addHandler(stream_handler)

    return logger



