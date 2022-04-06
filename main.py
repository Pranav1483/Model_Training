from torchvision.datasets import CIFAR10
from torchvision.transforms import transforms
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torchvision
import torch.nn.functional as F
from torch.optim import Adam
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
import torch.cuda

transformations = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
batch_size = 10
no_of_labels = 10

train_set = CIFAR10(root="./data", train=True, transform=transformations, download=True)

train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0)
print("Number of Images in a Training Set is ", len(train_loader) * batch_size)

test_set = CIFAR10(root="./data", train=False, transform=transformations, download=True)

test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=0)
print("Number of Images in a Test Set is ", len(test_loader) * batch_size)

print("Number of Batches in an Epoch is ", len(train_loader))
classes = ('Plane', 'Car', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck')


class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=3, out_channels=12, kernel_size=5, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(12)
        self.conv2 = nn.Conv2d(in_channels=12, out_channels=12, kernel_size=5, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(12)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv4 = nn.Conv2d(in_channels=12, out_channels=24, kernel_size=5, stride=1, padding=1)
        self.bn4 = nn.BatchNorm2d(24)
        self.conv5 = nn.Conv2d(in_channels=24, out_channels=24, kernel_size=5, stride=1, padding=1)
        self.bn5 = nn.BatchNorm2d(24)
        self.fc1 = nn.Linear(24 * 10 * 10, 10)

    def forward(self, inp):
        output = F.relu(self.bn1(self.conv1(inp)))
        output = F.relu(self.bn2(self.conv2(output)))
        output = self.pool(output)
        output = F.relu(self.bn4(self.conv4(output)))
        output = F.relu(self.bn5(self.conv5(output)))
        output = output.view(-1, 24 * 10 * 10)
        output = self.fc1(output)

        return output


model = Network()


loss_fn = nn.CrossEntropyLoss()
optimiser = Adam(model.parameters(), lr=0.001, weight_decay=0.0001)


def saveModel():
    p = "./MyFirstModel.pth"
    torch.save(model.state_dict(), p)


def testAccuracy():
    model.eval()
    accuracy = 0.0
    total = 0.0

    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            accuracy += (predicted == labels).sum().item()

    accuracy = (100*accuracy)/total
    return accuracy


def train(num_epochs):

    best_accuracy = 0.0
    device = torch.device("cpu")
    print("The model will be running on ", device, " device")
    model.to(device)

    for epoch in range(num_epochs):
        running_loss = 0.0
        running_ac = 0.0

        for i, (images, labels) in enumerate(train_loader, 0):
            images = Variable(images.to(device))
            labels = Variable(labels.to(device))

            optimiser.zero_grad()
            outputs = model(images)
            loss = loss_fn(outputs, images)
            loss.backward()
            optimiser.step()

            running_loss += loss.item()
            if i % 1000 == 999:
                print('[%d %5d] loss : %.3f' % (epoch + 1, i + 1, running_loss/1000))
                running_loss = 0.0

        accuracy = testAccuracy()
        print('For Epoch ', epoch + 1, ' the Test Accuracy over the Whole Test Set is %d %%' % accuracy)

        if accuracy > best_accuracy:
            saveModel()
            best_accuracy = accuracy


def imageshow(img):
    img = img / 2 + 0.5
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


def testBatch():
    images, labels = next(iter(test_loader))
    imageshow(torchvision.utils.make_grid(images))
    print("Real Labels : ", " ".join("%5s" % classes[labels[j]] for j in range(batch_size)))
    outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    print("Predicted : ", " ".join("%5s" % classes[predicted[j]] for j in range(batch_size)))


if __name__ == "__main__":
    train(5)
    print("Finished Training")
    testAccuracy()
    model = Network()
    path = "myFirstModel.pth"
    model.load_state_dict(torch.load(path))

    testBatch()
