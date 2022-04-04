#In [1]
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)



#In [3]

from tensorflow.keras.preprocessing.image import ImageDataGenerator

image_directory = 'C:/Users/COMPUTER/Desktop/skin_cancer_images/melanoma'

train_datagen= ImageDataGenerator( #여기다가 여러 파라미터를 넣어서 새로운 이미지들을 만들어야한다
    rescale = 1. /255,
    horizontal_flip = True,
    vertical_flip = True,
    shear_range = 0.3,
    rotation_range = 60,
    width_shift_range = 0.3,
    height_shift_range = 0.3,
    fill_mode = 'nearest'
)

test_datagen = ImageDataGenerator(
    rescale = 1. /255,
)

valid_datagen = ImageDataGenerator(
    rescale = 1. /255,
)

train_generator = train_datagen.flow_from_directory(
    image_directory+'/train',
    target_size = (512,512),
    color_mode = 'rgb',
    class_mode = 'binary',
    shuffle = True,
    batch_size = 8,
)

test_generator = test_datagen.flow_from_directory(
    image_directory+'/test',
    target_size = (512,512),
    color_mode = 'rgb',
    class_mode = 'binary',
    shuffle = False,
    batch_size = 8,
)

valid_generator = valid_datagen.flow_from_directory(
    image_directory+'/valid',
    target_size = (512,512),
    color_mode = 'rgb',
    class_mode = 'binary',
    shuffle = False,
    batch_size = 8,
)




#In [4]
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Model

vgg16 = VGG16(weights='imagenet', include_top=False, input_shape=(512,512,3)) #3채널만 됨

vgg16.trainable = False

flat = GlobalAveragePooling2D()(vgg16.output)

Add_layer = Dense(64, activation = 'relu')(flat)
Add_layer = Dense(1, activation = 'sigmoid')(Add_layer)
model = Model(inputs=vgg16.input, outputs=Add_layer)

model.summary()

#In [5]
vgg16.trainable = True

#In [6]
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
save_dir = 'C:/Users/COMPUTER/Desktop/skin_cancer/model(vgg)/checkpoint/'
checkpoint = ModelCheckpoint(
    save_dir+'{epoch:02d}-{val_loss:.5f}.h5', #모델 저장 경로
    monitor='val_loss', #모델을 저장할 때 기준이 되는 값
    verbose = 1, # 1이면 저장되었다고 화면에 뜨고 0이면 안뜸
    save_best_only=True,
    mode = 'auto',
    #val_acc인 경우, 정확도이기 때문에 클수록 좋으므로 max를 쓰고, val_loss일 경우, loss값이기 떄문에 작을수록 좋으므로 min을써야한다
    #auto일 경우 모델이 알아서 min,max를 판단하여 모델을 저장한다
    save_weights_only=False, #가중치만 저장할것인가 아닌가
    save_freq = 1 #1번째 에포크마다 가중치를 저장 period를 안쓰고 save_freq룰 씀
)

earlystop = EarlyStopping(
    monitor='val_loss',
    min_delta = 0.001,
    patience = 3,
    verbose=1,
    mode='auto'
)

callbacks = [checkpoint]


#In [7]

from tensorflow import keras
model.compile(optimizer=keras.optimizers.Adam(lr=0.0001) ,loss='binary_crossentropy',metrics=['accuracy'])
#러닝레이트를 설정안해주면 트레이닝은 잘되지만 valid는 이상하게 된다
tf.debugging.set_log_device_placement(True)

with tf.device("/gpu:0"):
    history = model.fit_generator(train_generator,
                                 steps_per_epoch=len(train_generator),
                                 epochs=100,
                                 validation_data=valid_generator,
                                 validation_steps=len(valid_generator),
                                 callbacks = callbacks,
                                 shuffle=True)

#In [7]
                                
import matplotlib.pyplot as plt
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train_loss','val_loss'])
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train_accuracy','val_accuracy'])
plt.show()

#In [8]
directory = 'C:/Users/COMPUTER/Desktop/skin_cancer'
model.save(directory+'/model(vgg)/skincancer_model(93).h5')