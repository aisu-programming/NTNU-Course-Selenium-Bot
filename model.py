import os
import tensorflow as tf
from PIL import Image


gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)]
        )
    except RuntimeError as e:
        print(e)


class_num = 41
id_to_word = {
    0 : 'b',
    1 : '7',
    2 : 'e',
    3 : '*',
    4 : 'g',
    5 : '0',
    6 : 'i',
    7 : 'c',
    8 : 'k',
    9 : '9',
    10: '+',
    11: 'z',
    12: 'l',
    13: 'r',
    14: 'w',
    15: '=',
    16: '1',
    17: 'n',
    18: 'o',
    19: '3',
    20: 't',
    21: 'x',
    22: 'p',
    23: '5',
    24: '8',
    25: 'v',
    26: 'h',
    27: '-',
    28: 's',
    29: 'd',
    30: 'm',
    31: '4',
    32: 'j',
    33: 'u',
    34: 'q',
    35: 'f',
    36: 'a',
    37: '/',
    38: 'y',
    39: '6',
    40: '2',
}
resize_height, resize_width = 60, 216


class MyConv(tf.keras.layers.Layer):
    def __init__(self, filter, kernel_size, strides):
        super(MyConv, self).__init__()
        self.cv  = tf.keras.layers.Conv2D(filter, kernel_size=kernel_size, strides=strides, padding="same", use_bias=False)
        self.bn  = tf.keras.layers.BatchNormalization()
        self.act = tf.nn.silu

    def call(self, inputs):
        return self.act(self.bn(self.cv(inputs)))


class MyBottleneck(tf.keras.layers.Layer):
    def __init__(self, filter, shortcut=True):
        super().__init__()
        self.cv  = MyConv(filter, kernel_size=3, strides=1)
        self.add = shortcut

    def forward(self, x):
        return x + self.cv(x) if self.add else self.cv(x)


class MyCSPBottleneck(tf.keras.layers.Layer):
    def __init__(self, filter, n=1, shortcut=True):
        super().__init__()
        self.cv1 = MyConv(filter, kernel_size=1, strides=1)
        self.b   = [ MyBottleneck(filter, shortcut) for _ in range(n) ]
        self.cv3 = tf.keras.layers.Conv2D(filter, kernel_size=1, strides=1, use_bias=False)
        self.bn  = tf.keras.layers.BatchNormalization()
        self.act = tf.nn.leaky_relu
        self.cv4 = MyConv(filter, kernel_size=1, strides=1)

    def forward(self, x):
        y1 = self.cv1(x)
        for b in self.b: y1 = b(y1)
        y2 = self.cv3(x)
        return self.cv4(self.act(self.bn(tf.concat([y1, y2], axis=1)), alpha=0.1))


class Detector(tf.keras.layers.Layer):
    def __init__(self):
        super(Detector, self).__init__()
        self.denses = [ tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(16, activation="relu"),
        ]) for _ in range(4) ]
        self.detect = tf.keras.layers.Dense(class_num, activation="softmax")

    def call(self, x):
        y = tf.concat([
            tf.expand_dims(self.detect(self.denses[i](x)), axis=1) for i in range(4)
        ], axis=1)
        return y


class MyModel(tf.keras.Model):
    def __init__(self, dropout_rate):
        super(MyModel, self).__init__()
        self.cv    = MyConv(32, kernel_size=3, strides=1)
        self.cv_p1 = MyConv(64, kernel_size=3, strides=2)    # (30, 108,   64)
        self.bn_p1 = MyCSPBottleneck(64, 1)
        self.cv_p2 = MyConv(128, kernel_size=3, strides=2)   # (15,  54,  128)
        self.bn_p2 = MyCSPBottleneck(128, 3)
        self.cv_p3 = MyConv(256, kernel_size=3, strides=2)   # ( 8,  27,  256)
        self.bn_p3 = MyCSPBottleneck(256, 15)
        self.cv_p4 = MyConv(512, kernel_size=3, strides=2)   # ( 4,  14,  512)
        self.bn_p4 = MyCSPBottleneck(512, 15)
        self.cv_p5 = MyConv(1024, kernel_size=3, strides=2)  # ( 2,   7, 1024)
        self.bn_p5 = MyCSPBottleneck(1024, 7)
        self.cv_p6 = MyConv(2048, kernel_size=3, strides=2)  # ( 1,   4, 2048)
        self.bn_p6 = MyCSPBottleneck(2048, 7)
        self.flatten  = tf.keras.layers.Flatten()
        self.dropout  = tf.keras.layers.Dropout(dropout_rate)
        self.detector = Detector()

    def call(self, x):
        x = self.bn_p1(self.cv_p1(self.cv(x)))
        x = self.bn_p2(self.cv_p2(x))
        x = self.bn_p3(self.cv_p3(x))
        x = self.bn_p4(self.cv_p4(x))
        x = self.bn_p5(self.cv_p5(x))
        x = self.bn_p6(self.cv_p6(x))
        y = self.flatten(self.dropout(x))
        y = self.detector(y)
        return y


def process_image(img):
    return Image.open(img).convert('L').resize((resize_width, resize_height))


def load_MyModel():
    if "val_acc.h5" not in os.listdir("weights"):
        print("Please download the weights file (val_acc.h5) first at here:\n" + 
              "https://drive.google.com/file/d/1qdB1SECI-cwqbUQNbJ834EcRAX07i4Z5/view?usp=sharing\n" + 
              "And make sure that you put it in the directory 'weights'.")
        return
    else:
        dropout_rate = 0.955
        model = MyModel(dropout_rate)
        model.build(input_shape=(None, resize_height, resize_width, 1))
        model.load_weights("weights/val_acc.h5")
        return model