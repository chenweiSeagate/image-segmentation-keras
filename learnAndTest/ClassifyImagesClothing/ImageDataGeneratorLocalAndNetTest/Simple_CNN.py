#region import
import os
# 导入 random(随机数) 模块
import random
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

# TensorFlow and tf.keras
import tensorflow as tf
# Helper libraries
import numpy as np
import matplotlib.pyplot as plt
print(tf.__version__)
#endregion

#region load datasets
cifar10 = tf.keras.datasets.cifar10
mnist = tf.keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
#  0-T恤/上衣,1-裤子,2-套头衫,3-连衣裙,4-外套,5-凉鞋,6-衬衫,7-运动鞋,8-包,9-短靴
class_names = ['0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9']
train_images = train_images / 255.0
test_images = test_images / 255.0
print(train_images.shape)
print(len(train_labels))
#endregion

def plot_image(i, predictions_array, true_label, img):
    predictions_array, true_label, img = predictions_array, true_label[i], img[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.imshow(img, cmap=plt.cm.binary)

    predicted_label = np.argmax(predictions_array)
    if predicted_label == true_label:
      color = 'blue'
    else:
      color = 'red'

    plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],\
                                  100*np.max(predictions_array),\
                                  class_names[true_label[0]]),\
                                  color=color)

def plot_value_array(i, predictions_array, true_label):
    predictions_array, true_label = predictions_array, true_label[i]
    plt.grid(False)
    plt.xticks(range(10))
    plt.yticks([])
    thisplot = plt.bar(range(10), predictions_array, color="#777777")
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)

    thisplot[predicted_label].set_color('red')
    thisplot[true_label[0]].set_color('blue')
def create_model():
  model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(32, (3,3), padding="same",activation='relu', input_shape=(32, 32, 3)),
      tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
      tf.keras.layers.Conv2D(32, (3,3), padding="same",activation='relu', input_shape=(32, 32, 3)),
      tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
      tf.keras.layers.Conv2D(64, (3,3), padding="same",activation='relu', input_shape=(32, 32, 3)),
      tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
      tf.keras.layers.Flatten(input_shape=(32, 32, 3)),
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.Dropout(0.5),
      tf.keras.layers.Dense(10, activation='softmax')
  ])
  model.compile(optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                metrics=['acc'])

  return model

# 创建一个基本的模型实例
model = create_model()

# 显示模型的结构
model.summary()
EPOCHS = 2

#region SaveModel
checkpoint_path = "BasicClassificationForCifar20/cp-{epoch:04d}-{acc:.04f}.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
latest = tf.train.latest_checkpoint(checkpoint_dir)

if(latest is not None):
    model.load_weights(latest)

model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path,
    save_weights_only=True,
    monitor='acc',
    mode='max')

#model.save_weights(checkpoint_path.format(epoch=0))
#endregion

hist = model.fit(train_images, train_labels, 
                epochs=EPOCHS, 
                batch_size=128,
                validation_data=(test_images,test_labels),
                callbacks=[model_checkpoint_callback])

test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)

#path = manager.save(checkpoint_number=0)       
print('\nTest accuracy:', test_acc)

probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

predictions = probability_model.predict(test_images)
# Plot the first X test images, their predicted labels, and the true labels.
# Color correct predictions in blue and incorrect predictions in red.
num_rows = 5
num_cols = 3
num_images = num_rows*num_cols
plt.figure(figsize=(2*2*num_cols, 2*num_rows))
randList=np.random.randint(len(predictions),size=num_images)
for i in range(num_images):
  plt.subplot(num_rows, 2*num_cols, 2*i+1)
  plot_image(randList[i], predictions[randList[i]], test_labels, test_images)
  plt.subplot(num_rows, 2*num_cols, 2*i+2)
  plot_value_array(randList[i], predictions[randList[i]], test_labels)
plt.tight_layout()
plt.show()

#region Test Save load weights
# loss, acc = model.evaluate(test_images,  test_labels, verbose=2)
# print("Untrained model, accuracy: {:5.2f}%".format(100*acc))

# model2 = create_model()
# latest = tf.train.latest_checkpoint(checkpoint_dir)
# model2.load_weights(latest)

# # 重新评估模型
# loss,acc = model2.evaluate(test_images,  test_labels, verbose=2)
# print("Restored model2, accuracy: {:5.2f}%".format(100*acc))
#endregion
hist_dict = hist.history
print("train acc:")
print(hist_dict['acc'])
print("validation acc:")
print(hist_dict['val_acc'])
train_acc = hist.history['acc']
val_acc = hist.history['val_acc']
train_loss = hist.history['loss']
val_loss = hist.history['val_loss']
# 绘图
epochs = range(1, len(train_acc)+1)
plt.figure() # 新建一个图
plt.plot(epochs, train_acc, 'bo', label = 'Training acc')
plt.plot(epochs, val_acc, 'r', label = 'Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.savefig("accuracy.png")
plt.figure() # 新建一个图
plt.plot(epochs, train_loss, 'bo', label = 'Training loss')
plt.plot(epochs, val_loss, 'r', label = 'Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.savefig("loss.png")