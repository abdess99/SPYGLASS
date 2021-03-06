""" Main Python file to start routines """

from argparse import ArgumentParser
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import LearningRateLogger, EarlyStopping, ModelCheckpoint
from pytorch_lightning.callbacks import model_checkpoint
from model import LightningModel
from data import SpyGlassDataModule, Dataset2DGenerator
from config import Config


# +-------------------------------------------------------------------------------------+ #
# |                                                                                     | #
# |                                          INIT                                       | #
# |                                                                                     | #
# +-------------------------------------------------------------------------------------+ #

def init_data(cfg):
    return SpyGlassDataModule(cfg.data_2d_root, cfg.medical_data_csv_path,
                              cfg.train_batch_size, cfg.val_batch_size, cfg.num_workers)

def init_model(cfg):
    return LightningModel(use_label_smoothing=cfg.use_label_smoothing,
                          smoothing=cfg.smoothing,
                          reduction=cfg.reduction)

def init_trainer():
    """ Init a Lightning Trainer using from_argparse_args
    Thus every CLI command (--gpus, distributed_backend, ...) become available.
    """
    parser = ArgumentParser()
    parser = Trainer.add_argparse_args(parser)
    args   = parser.parse_args()
    lr_logger      = LearningRateLogger()
    early_stopping = EarlyStopping(monitor='val_loss', mode='min', min_delta=0.001, patience=10, verbose=True)
    return Trainer.from_argparse_args(args, callbacks = [lr_logger, early_stopping])




# +-------------------------------------------------------------------------------------+ #
# |                                                                                     | #
# |                                          RUN                                        | #
# |                                                                                     | #
# +-------------------------------------------------------------------------------------+ #

def make_2d_dataset(cfg):
    dataset_generator = Dataset2DGenerator(cfg.video_root, cfg.output_root, 
                                           cfg.sampling_factor, cfg.crop)
    dataset_generator.run()

def run_training(cfg):
    """ Instanciate a datamodule, a model and a trainer and run trainer.fit(model, data) """
    data   = init_data(cfg)
    model, trainer = init_model(cfg), init_trainer()
    trainer.fit(model, data)

def test(input_root, model_path):
    data    = init_data(input_root)
    model   = LightningModel.load_from_checkpoint(model_path)
    trainer = init_trainer()
    trainer.test()


if __name__ == '__main__':
    cfg = Config()
    # make_2d_dataset(cfg)
    run_training(cfg) 

