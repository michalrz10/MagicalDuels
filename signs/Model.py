import tensorflow as tf
import numpy as np
import os

class Model:
    def __init__(self):
        self.model=tf.keras.Sequential([
            tf.keras.layers.Conv2D(4, 8, activation='relu',input_shape=(64, 64,1)),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(16, 4, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 2, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')
        ])
        self.model.compile('Adam','mean_squared_error',metrics=['accuracy'])


    def learn(self,inputt,expected):
        inputt=np.array(inputt)
        expected=np.array(expected)
        return self.model.fit(inputt,expected,epochs=10,batch_size=10,validation_split=0.33,verbose=0)

    def predict(self,inputt):
        inputt=np.reshape(inputt,(-1,64,64,1))
        res=self.model.predict(inputt)[0]
        minn=np.argmax(res)
        if res[minn]>=0.8: return minn
        return -1

    def save(self):
        self.model.save_weights('signs')

    def load(self):
        self.model.load_weights('signs')
