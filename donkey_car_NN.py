import time

import cv2 as cv
import numpy
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable

import jetson_nano_move as jm


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    jm.set_throttle(0)
    cv.destroyAllWindows()


class Net(nn.Module):  # 640 x 360 input
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(6960, 910)
        self.fc2 = nn.Linear(910, 60)
        self.fc3 = nn.Linear(60, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(1, -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def debug_print(a):
    if debug:
        print(a)


def cv2img2tensor(image):
    tensor_img = numpy.transpose(image, (2, 0, 1))
    tensor_img = torch.from_numpy(tensor_img)
    return tensor_img.unsqueeze_(0)


net: Net = Net()
net.cuda()
criterion = nn.CrossEntropyLoss().cuda()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

jm.set_throttle(0)
time.sleep(1)
# camera init
img = jm.cap

debug = True


def main_loop():
    if not debug:
        jm.set_throttle(0.12)
    while True:
        if learning_stage():
            break

    cv.destroyAllWindows()
    jm.set_throttle(0)
    jm.set_angle(90)
    time.sleep(5)
    if not debug:
        jm.set_throttle(0.12)

    while True:
        real_action()


def real_action():
    _, raw_img = img.read()
    cv.imshow('cam', raw_img)
    cv.waitKey(1)
    input_tensor = cv2img2tensor(raw_img)
    output = net(Variable(input_tensor.cuda()).float())
    print('\n\n')
    print(output)
    output = torch.argmax(output)
    print(output)
    if output == 0:
        jm.set_angle(130)
    elif output == 1:
        jm.set_angle(90)
    elif output == 2:
        jm.set_angle(50)


def learning_stage() -> bool:
    _, raw_img = img.read()
    input_tensor = cv2img2tensor(raw_img)
    optimizer.zero_grad()
    inputs = Variable(input_tensor.cuda()).float()
    deg = 1  # straight
    cv.imshow('judge', raw_img)
    in_char = cv.waitKey(1)  # getch()
    if in_char == ord('a'):
        deg = 0  # jm.MAX_STEER_DEV
        jm.set_angle(130)
    elif in_char == ord('d'):
        deg = 2  # -jm.MAX_STEER_DEV
        jm.set_angle(50)
    elif in_char == ord('w'):
        return True
    else:
        jm.set_angle(90)
    debug_print(f'\n\ninput: {in_char}')
    label = Variable(torch.tensor([deg]).cuda()).long()
    debug_print(f'label: {label}')
    outputs = net(inputs)
    debug_print(f'output: {outputs}')
    loss = criterion(outputs, label).cuda()
    loss.backward()
    optimizer.step()
    return False


try:
    main_loop()
except KeyboardInterrupt:
    print('ctrl + C trapped')

finish_program(img)
