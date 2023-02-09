# Main SMPLpix Evaluation Script
#
# (c) Sergey Prokudin (sergey.prokudin@gmail.com), 2021
# camera_params 폴더를 test 데이터 폴더에 넣어두기

import os
import shutil
import pprint
import torch
from torch.utils.data import DataLoader

from smplpix.args import get_smplpix_arguments
from smplpix.utils import generate_mp4
from smplpix.dataset import SMPLPixDataset
from smplpix.unet import UNet
from smplpix.training import train, evaluate
from smplpix.utils import download_and_unzip


    
def generate_eval_video(args, data_dir, unet, frame_rate=25, save_target=False, save_input=True):

    print("rendering SMPLpix predictions for %s..." % data_dir)
    data_part_name = os.path.split(data_dir)[-1]

    test_dataset_per_1 = SMPLPixDataset(data_dir=data_dir,
                                  downsample_factor=args.downsample_factor,
                                  perform_augmentation=False,
                                  n_input_channels=args.n_input_channels,
                                  n_output_channels=args.n_output_channels,
                                  augmentation_probability=args.aug_prob)
    test_dataloader_1 = DataLoader(test_dataset_per_1, batch_size=args.batch_size)
    final_renders_path_1 = os.path.join(args.workdir, 'renders_%s' % data_part_name)
    _ = evaluate(unet, test_dataloader_1, final_renders_path_1, args.device, save_target=save_target, save_input=save_input)
    
    # test_dataset_per_2 = SMPLPixDataset(data_dir=data_dir,
    #                               downsample_factor=args.downsample_factor,
    #                               perform_augmentation=False,
    #                               n_input_channels=args.n_input_channels,
    #                               n_output_channels=args.n_output_channels,
    #                               augmentation_probability=args.aug_prob)
    # test_dataloader_2 = DataLoader(test_dataset_per_2, batch_size=args.batch_size)
    # final_renders_path_2 = os.path.join(args.workdir, 'renders_%s' % data_part_name)
    # _ = evaluate(unet, test_dataloader_2, final_renders_path_2, args.device, save_target=save_target, save_input=save_input)

    print("generating video animation for data %s..." % data_dir)

    video_animation_path_1 = os.path.join(args.workdir, '%s_animation_1.mp4' % data_part_name)
    _ = generate_mp4(final_renders_path_1, video_animation_path_1, frame_rate=frame_rate)
    print("saved animation video to %s" % video_animation_path_1)

    return

def main():

    print("******************************************************************************************\n"+
          "****************************** SMPLpix Evaluation Loop  **********************************\n"+
          "******************************************************************************************\n"+
          "******** Copyright (c) 2021 - now, Sergey Prokudin (sergey.prokudin@gmail.com) ***********")

    args = get_smplpix_arguments()
    print("ARGUMENTS:")
    pprint.pprint(args)

    if args.checkpoint_path is None:
        print("no model checkpoint was specified, looking in the log directory...")
        ckpt_path = os.path.join(args.workdir, 'network.h5')
    else:
        ckpt_path = args.checkpoint_path
    if not os.path.exists(ckpt_path):
        print("checkpoint %s not found!" % ckpt_path)
        return
    
    print("defining the neural renderer model (U-Net)...")
    unet = UNet(in_channels=args.n_input_channels, out_channels=args.n_output_channels,
                n_blocks=args.n_unet_blocks, dim=2, up_mode='resizeconv_linear').to(args.device)

    print("loading the model from checkpoint: %s" % ckpt_path)
    unet.load_state_dict(torch.load(ckpt_path))
    unet.eval()
    generate_eval_video(args, args.data_dir, unet, save_target=args.save_target)

    return

if __name__== '__main__':
    main()
