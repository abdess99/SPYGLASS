""" Adapted from:
https://github.com/HHTseng/video-classification/blob/master/ResNetCRNN/functions.py.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models



class ResCNNEncoder(nn.Module):

    """ 2D CNN encoder using ResNet-152 pretrained. 
    Notation:
        (N,C,T,W,H) = (batch_size, num_channels, time_depth, x_size, y_size).
    """

    def __init__(self, fc_hidden1: int=512, fc_hidden2: int=512, drop_p: float=0.3, CNN_embed_dim: int=300):
        """Load the pretrained ResNet-152 and replace top fc layer."""
        super(ResCNNEncoder, self).__init__()
        self.fc_hidden1 = fc_hidden1
        self.fc_hidden2 = fc_hidden2
        self.drop_p     = drop_p
        resnet = models.resnet152(pretrained=True)
        modules = list(resnet.children())[:-1] # delete the last fc layer.
        self.resnet = nn.Sequential(*modules)
        self.fc1 = nn.Linear(resnet.fc.in_features, fc_hidden1)
        self.bn1 = nn.BatchNorm1d(fc_hidden1, momentum=0.01)
        self.fc2 = nn.Linear(fc_hidden1, fc_hidden2)
        self.bn2 = nn.BatchNorm1d(fc_hidden2, momentum=0.01)
        self.fc3 = nn.Linear(fc_hidden2, CNN_embed_dim)
        
    def forward(self, x_3d: torch.Tensor) -> torch.Tensor:
        """ A usual resnet forward pass minus the last layer.
        Hence acts as an encoder.

        Args:
            x_3d (torch.Tensor): Shape (N,C,T,W,H).
                                 
        Returns:
            torch.Tensor: Shape (batch_size, num_channels, CNN_embed_dims).
        """
        cnn_embed_seq = []
        for t in range(x_3d.size(1)):
            # ResNet CNN
            with torch.no_grad():
                x = self.resnet(x_3d[:, :, t, :, :])  # ResNet
                x = x.view(x.size(0), -1)             # flatten output of conv
            # FC layers
            x = self.bn1(self.fc1(x))
            x = F.relu(x)
            x = self.bn2(self.fc2(x))
            x = F.relu(x)
            x = F.dropout(x, p=self.drop_p, training=self.training)
            x = self.fc3(x)
            cnn_embed_seq.append(x)
        # swap time and sample dim such that (sample dim, time dim, CNN latent dim)
        cnn_embed_seq = torch.stack(cnn_embed_seq, dim=0).transpose_(0, 1)
        # cnn_embed_seq: shape=(batch, time_step, input_size)
        return cnn_embed_seq