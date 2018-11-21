from keras.layers import Input, Add, Dense, Activation, Flatten, Convolution2D, MaxPooling2D, ZeroPadding2D, \
    AveragePooling2D, TimeDistributed
from keras import backend as K
from model.RoIpoolingConv import RoIpoolingConv
from model.BatchNormalization import BatchNormalization

def identity_block(input_tensor, kernel_size, filters, stage, block, trainable=True):
    nb_filter1,nb_filter2,nb_filter3=filters
    bn_axis=3
    conv_name_base='res'+str(stage)+block+'_branch'
    bn_name_base='bn'+str(stage)+block+'_branch'
    x=Convolution2D(nb_filter1,(1,1),name=conv_name_base+'2a',
                    trainable=trainable)(input_tensor)
    x=BatchNormalization(axis=bn_axis,name=bn_name_base+'2a')(x)
    x=Activation('relu')(x)

    x=Convolution2D(nb_filter2,(kernel_size,kernel_size),padding='same',
                    name=conv_name_base+'2b',trainable=trainable)(x)
    x=BatchNormalization(axis=bn_axis,name=bn_name_base+'2b')(x)
    x=Activation('relu')(x)

    x=Convolution2D(nb_filter3,(1,1),name=conv_name_base+'2c',
                    trainable=trainable)(x)
    x=BatchNormalization(axis=bn_axis,name=bn_name_base+'2c')(x)

    x=Add()[x,input_tensor]
    x=Activation('relu')(x)
    return x


def identity_block_td(input_tensor,kernel_size,filters,stage,block,trainable=True):
    nb_filter1,nb_filter2,nb_filter3=filters
    bn_axis=3
    conv_name_base='res'+str(stage)+block+'_branch'
    bn_name_base='bn'+str(stage)+block+'_branch'

    x=TimeDistributed(Convolution2D(nb_filter1,(1,1),trainable=trainable,
                                    kernel_initializer='normal'),name=conv_name_base+'2a')(input_tensor)
    x=TimeDistributed(BatchNormalization(axis=bn_axis),name=bn_name_base+'2b')(x)
    x=Activation('relu')(x)
    x = TimeDistributed(
        Convolution2D(nb_filter2, (kernel_size, kernel_size), trainable=trainable, kernel_initializer='normal',
                      padding='same'), name=conv_name_base + '2b')(x)
    x = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = TimeDistributed(Convolution2D(nb_filter3, (1, 1), trainable=trainable, kernel_initializer='normal'),
                        name=conv_name_base + '2c')(x)
    x = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '2c')(x)

    x = Add()([x, input_tensor])
    x = Activation('relu')(x)
    return x



def conv_block(input_tensor, kernel_size, filters, stage, block, strides=(2, 2), trainable=True):
    nb_filter1, nb_filter2, nb_filter3 = filters
    if K.image_dim_ordering() == 'tf':
        bn_axis = 3
    else:
        bn_axis = 1

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = Convolution2D(nb_filter1, (1, 1), strides=strides, name=conv_name_base + '2a', trainable=trainable)(
        input_tensor)
    x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = Convolution2D(nb_filter2, (kernel_size, kernel_size), padding='same', name=conv_name_base + '2b',
                      trainable=trainable)(x)
    x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = Convolution2D(nb_filter3, (1, 1), name=conv_name_base + '2c', trainable=trainable)(x)
    x = BatchNormalization(axis=bn_axis, name=bn_name_base + '2c')(x)

    shortcut = Convolution2D(nb_filter3, (1, 1), strides=strides, name=conv_name_base + '1', trainable=trainable)(
        input_tensor)
    shortcut = BatchNormalization(axis=bn_axis, name=bn_name_base + '1')(shortcut)

    x = Add()([x, shortcut])
    x = Activation('relu')(x)
    return x

def conv_block_td(input_tensor, kernel_size, filters, stage, block, input_shape, strides=(2, 2), trainable=True):

    # conv block time distributed

    nb_filter1, nb_filter2, nb_filter3 = filters
    if K.image_dim_ordering() == 'tf':
        bn_axis = 3
    else:
        bn_axis = 1

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = TimeDistributed(Convolution2D(nb_filter1, (1, 1), strides=strides, trainable=trainable, kernel_initializer='normal'), input_shape=input_shape, name=conv_name_base + '2a')(input_tensor)
    x = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = TimeDistributed(Convolution2D(nb_filter2, (kernel_size, kernel_size), padding='same', trainable=trainable, kernel_initializer='normal'), name=conv_name_base + '2b')(x)
    x = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = TimeDistributed(Convolution2D(nb_filter3, (1, 1), kernel_initializer='normal'), name=conv_name_base + '2c', trainable=trainable)(x)
    x = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '2c')(x)

    shortcut = TimeDistributed(Convolution2D(nb_filter3, (1, 1), strides=strides, trainable=trainable, kernel_initializer='normal'), name=conv_name_base + '1')(input_tensor)
    shortcut = TimeDistributed(BatchNormalization(axis=bn_axis), name=bn_name_base + '1')(shortcut)

    x = Add()([x, shortcut])
    x = Activation('relu')(x)
    return x

def ResNet50(input_tensor=None,trainable=False):
    input_shape=(None,None,3)
    if input_tensor is None:
        img_input=Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            img_input=Input(tensor=input_tensor,shape=input_shape)

        else:
            img_input=input_tensor
    bn_axis=3

    x=ZeroPadding2D((3,3))(img_input)
    x=Convolution2D(64,(7,7),strides=(2,2),name='conv1',trainable=trainable)(x)
    x=BatchNormalization(axis=bn_axis,name='bn_conv1')(x)
    x=Activation('relu')(x)
    x=MaxPooling2D((3,3),strides=(2,2))(x)

    x=conv_block(x,3,[64,64,256],stage=2,
                 block='a',strides=(1,1),trainable=trainable)
    x=identity_block(x,3,[64,64,256],stage=2,block='b',
                     trainable=trainable)
    x=identity_block(x,3,[64,64,256],block='c',trainable=trainable)

    x = conv_block(x, 3, [128, 128, 512], stage=3, block='a', trainable=trainable)
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='b', trainable=trainable)
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='c', trainable=trainable)
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='d', trainable=trainable)

    x = conv_block(x, 3, [256, 256, 1024], stage=4, block='a', trainable=trainable)
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='b', trainable=trainable)
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='c', trainable=trainable)
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='d', trainable=trainable)
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='e', trainable=trainable)
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='f', trainable=trainable)

    return x

def classifier_layers(x,input_shape,trainable=False):
    #my backend is tensorflow
    x=conv_block_td(x,3,[512,512,2048],stage=5,block='a',input_shape=input_shape,strides=(2,2),
                    trainable=trainable)
    x=identity_block_td(x,3,[512,512,2048],stage=5,block='b',
                    trainable=trainable)
    x=identity_block_td(x,3,[512,512,2048],stage=5,block='c',
                        trainable=trainable)
    x=TimeDistributed(AveragePooling2D((7,7)),name='avg_pool')(x)
    return x

def rpn(x,num_anchors):
    x=Convolution2D(512,(3,3),padding='same',activation='relu',kernel_initializer='normal',name='rpn_conv1')(x)
    x_class=Convolution2D(num_anchors,(1,1),activation='sigmoid',kernel_initializer='uniform',name='rpn_out_class')(x)
    x_regr=Convolution2D(num_anchors*4,(1,1),activation='linear',kernel_initializer='zero',name='rpn_out_regress')(x)
    return [x_class,x_regr,x]

def classifier(base_layers,input_rois,num_rois,nb_classes=26,trainable=False):
    pooling_regions=14
    input_shape=(num_rois,14,14,1024)
    out_roi_pool=RoIpoolingConv(pooling_regions,num_rois=num_rois)([base_layers,input_rois])
    out=classifier_layers(out_roi_pool,input_shape=input_shape,trainable=True)
    out=TimeDistributed(Flatten())(out)
    out_class=TimeDistributed(Dense())

















