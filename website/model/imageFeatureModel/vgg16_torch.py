import torch
import torch.nn as nn
from torch.autograd import Variable
from functools import reduce

class LambdaBase(nn.Sequential):
    def __init__(self, fn, *args):
        super(LambdaBase, self).__init__(*args)
        self.lambda_func = fn

    def forward_prepare(self, input):
        output = []
        for module in self._modules.values():
            output.append(module(input))
        return output if output else input

class Lambda(LambdaBase):
    def forward(self, input):
        return self.lambda_func(self.forward_prepare(input))

class LambdaMap(LambdaBase):
    def forward(self, input):
        return list(map(self.lambda_func,self.forward_prepare(input)))

class LambdaReduce(LambdaBase):
    def forward(self, input):
        return reduce(self.lambda_func,self.forward_prepare(input))


vgg16_torch = nn.Sequential( # Sequential,
	nn.Conv2d(3,64,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(64,64,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.MaxPool2d((2, 2),(2, 2),(0, 0),ceil_mode=True),
	nn.Conv2d(64,128,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(128,128,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.MaxPool2d((2, 2),(2, 2),(0, 0),ceil_mode=True),
	nn.Conv2d(128,256,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(256,256,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(256,256,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.MaxPool2d((2, 2),(2, 2),(0, 0),ceil_mode=True),
	nn.Conv2d(256,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(512,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(512,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.MaxPool2d((2, 2),(2, 2),(0, 0),ceil_mode=True),
	nn.Conv2d(512,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(512,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.Conv2d(512,512,(3, 3),(1, 1),(1, 1)),
	nn.ReLU(),
	nn.MaxPool2d((2, 2),(2, 2),(0, 0),ceil_mode=True),
	Lambda(lambda x: x.view(x.size(0),-1)), # View,
	nn.Sequential(Lambda(lambda x: x.view(1,-1) if 1==len(x.size()) else x ),nn.Linear(25088,4096)), # Linear,
	nn.ReLU(),
	nn.Dropout(0.5),
	nn.Sequential(Lambda(lambda x: x.view(1,-1) if 1==len(x.size()) else x ),nn.Linear(4096,4096)), # Linear,
	nn.ReLU(),
	nn.Dropout(0.5),
	nn.Sequential(Lambda(lambda x: x.view(1,-1) if 1==len(x.size()) else x ),nn.Linear(4096,1365)), # Linear,
)
