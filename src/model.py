# ASV --anti spoofing project 2018--based on papers
# that's where you implement your model's graph and execution functionality
# for feature maps 17x64 we can get up to 10 layers CNN(V.DCNN)
# we should try first the baseline CNN ?? is that implemented in the given matlab code??
# So we only design our V.D.CNN

# Bonus: ->batch normalization


from __future__ import division, print_function

import sys
import time
from datetime import datetime
import math
import tensorflow as tf
import numpy as np
from lib.model_io import save_variables
from lib.precision import _FLOATX
import read_img as rim
# ------define architecture functions--------------------------------------------------------------
# define weights


def weight_dict(shape):
    init = tf.truncated_normal(shape, stddev=0.1)
    return(tf.Variable(init))
# define bias--optional


def bias_dict(shape):
    init = tf.constant(0.1, shape=shape)
    return(tf.Variable(init))

# return convolution result --optional add bias


def conv2d(x, W, stride=1):
    return(tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='SAME'))
# define convolution layer


def conv_layer(inp, shape):
    W = weight_dict(shape)
    b = bias_dict([shape[3]])
    return(tf.nn.relu(conv2d(inp, W) + b))
# define max pooling function


def max_pool(x, stride, k):
    return (tf.nn.max_pool(x, strides=[1, 2, stride, 1], ksize=[1, 2, k, 1], padding='VALID'))

# define dense layers--last block of layers


# def full_layer(input, size,l2_loss):
#     in_size=int(input.get_shape()[1])
#     W=weight_variable([in_size,size])
#     b=bias_variable([size])
#     l2_loss += tf.nn.l2_loss(W)+tf.nn.l2_loss(b)
#     return tf.matmul(input,W)+b,l2_loss
#
#  # flat = tf.reshape(inp, [-1, 7 * 7 * 64])
#
#  #Fully-Connected Layer 1
#         full_1,l2_loss=full_layer(reshaped,2048,l2_loss)
#         full_1=tf.nn.relu(full_1)
#         full_drop_1=tf.nn.dropout(full_1,keep_prob=self.dropout_keep_prob)    #Perform dropout on fully connected layer
#
# --------------------------------------------------------------------------------------------
    # in_s = int(inp.getshape()[1])  # flatten layer
    # W = weight_dict([in_s, size])
    # b = bias_dict(shape)
    # # loss+=
    # return (tf.matmul(inp, W), loss)
    # return (tf.nn.softmax(tf.matmul(in_s,W)))
# --------------------------------------------------------------------------------------------

# dense 1st try
def dense_layer(inp, size):

    dense = tf.layers.dense(inputs=inp, units=size, activation=tf.nn.relu)
    dropout = tf.layers.dropout(
        inputs=dense, rate=0.2, training=tf.estimator.ModeKeys.TRAIN)

    # tf.nn.softmax(logits,axis=-1,name="GenOrSpoof",dim=2)

    return dropout

# batch normalization


def batch_n(convl):
    return (tf.nn.relu(tf.contrib.layers.batch_norm(convl)))
# -------------------------------------------------------------------------------------------------------


class CNN(object):

    def __init__(self, model_id=None):
        self.model_id = model_id
        self.Xtrain_in = np.empty(0)
        self.Ytrain_in = np.empty(0)
        self.Xvalid_in = np.empty(0)
        self.Yvalid_in = np.empty(0)
        # index of X_train data for shuffling the input batches
        self.tindx = np.empty(0)
        # index of valid data for shuffling the input batches
        self.vindx = np.empty(0)
        # __________________________________________________
        self.height = 64
        self.width = 17
        self.chan = 1           # channel of image 1 or 3 if rgb
        self.n_classes = 2      # genuine or spoof --number of classes
        self.batch_size = 256   # 64 || 128 || 256

        self.train_size = 0  # 1587420  # number of frames (train)
        self.dev_size = 0  # 1029721  # number of frames (valid)
        self.eval_size = 0  # 8522944 #number of frames (eval)

    # normalize input data
    def normalize(self, X):
        col_max = np.max(X, axis=0)
        col_min = np.min(X, axis=0)
        normX = np.divide(X - col_min, col_max - col_min)

    # read input data
    def input(self):
        self.Xtrain_in, self.Ytrain_in, self.train_size = rim.read_Data(
            "ASVspoof2017_V2_train_fbank", "train_info.txt")  # Read Train data
        # Normalize input train set data
        self.Xtrain_in = self.normalize(self.Xtrain_in)
        # create an numpy array with ints matching the #of train data
        self.tindx = np.arange(self.train_size)

        self.Xvalid_in, self.Yvalid_in, self.dev_size = rim.read_Data(
            "ASVspoof2017_V2_train_dev", "dev_info.txt")  # Read validation data
        # Normalize input validation set data
        self.Xvalid = self.normalize(self.Xvalid)
        self.vindx = np.arange(self.dev_size)
    # shuffle index so to get with random order the data

    def shuffling(self, indx):
        np.random.shuffle(indx)

    def inference(self, X, reuse=True, is_training=True):
        with tf.variable_scope("inference", reuse=reuse):
            # Implement your network here
            # equation or predefiend fuctions --convolution operation
            # we define set of layers according to the max_pooling ksize
            # each set has more than one convolution and max_poolin layers
            # totaly we have 2 sets and 5 blocks
            # init phase
            # [filter_h,filter_w,in_channel,out_channel]
            shape1 = [3, 3, 1, 4]
            w = weight_dict(shape1)
            b = bias_dict([shape1[3]])  # out_channel== n_hidden
            conv1 = conv2d(X, w) + b    # init_convolution

    # -----------1st set--------{2 blocks}---------------------------------------
            # -------1st block
            shape1 = [3, 3, 1, 8]
            conv_l1 = conv_layer(conv1, shape1)
            batch_norm1 = batch_n(conv_l1)  # batch normalization
            conv_l2 = conv_layer(batch_norm1, shape1)
            batch_norm2 = batch_n(conv_l2)           # batch normalization

            mpool_1 = max_pool(batch_norm2, 1, 1)   # stride =1 , k=1
            # ------2nd block
            shape2 = [3, 3, 1, 8]
            conv_l3 = conv_layer(mpool_1, shape2)
            batch_norm3 = batch_n(conv_l3)  # batch normalization
            conv_l4 = conv_layer(batch_norm3, shape2)
            batch_norm4 = batch_n(conv_l4)  # batch normalization

            mpool_2 = max_pool(batch_norm4, 1, 1)   # stride =1 , k=1

    # --------2nd set------{3 blocks}--------------------------------------------
            # -------3d block
            shape3 = [3, 3, 1, 16]
            conv_l5 = conv_layer(mpool_2, shape3)
            batch_norm5 = batch_n(conv_l5)      # normalization
            conv_l6 = conv_layer(batch_norm1, shape3)
            batch_norm6 = batch_n(conv_l6)      # normalization batch

            mpool_3 = max_pool(batch_norm6, 1, 1)   # stride =1 , k=1
            # --------4th block
            shape4 = [3, 3, 1, 32]
            conv_l7 = conv_layer(mpool_3, shape4)
            batch_norm7 = batch_n(conv_l7)
            conv_l8 = conv_layer(batch_norm7, shape4)
            batch_norm8 = batch_n(conv_l8)

            mpool_4 = max_pool(batch_norm8, 2, 2)   # stride=2, k=2
            # --------5th blocks
            shape5 = [3, 3, 1, 64]
            conv_l9 = conv_layer(mpool_4, shape5)
            batch_norm9 = batch_n(conv_l9)
            conv_l10 = conv_layer(batch_norm9, shape5)
            batch_norm10 = batch_n(conv_l10)

            mpool_5 = max_pool(batch_norm10, 2, 2)      # stride=2, k=2

    # ------------add dense layers {4 layers}-------------------------------------

            flat = tf.reshape(mpool_5, [-1, 7 * 7 * 64])
            loss = tf.constant(0.0)
            size = 1024
            # ---------------dense layer 1-------------------------
            dense1 = dense_layer(flat, size)
            # ---------------dense layer 2-------------------------
            dense2 = dense_layer(dense1, size)

            logits = tf.layers.dense(
                inputs=dense2, units=2, activation=tf.nn.softmax)
            # tf.nn.softmax(logits,axis=-1,name="GenOrSpoof",dim=2)

        return logits

    def define_train_operations(self):
        # # read data?
        # self.train_list = rim.read_Data(
        #     "../../ASV/DATA/ASVspoof2017_V2_train_fbank", "train_info.txt")  # define this properly
        # self.valid_list = rim.read_Data(
        #     "../../ASV/DATA/ASVspoof2017_V2_train_dev", "dev_info.txt")

        # --- Train computations
        # self.trainDataReader = trainDataReader

        X_data_train = tf.placeholder(tf.float32, shape=(
            None, self.height, self.width, self.chan))  # Define this

        Y_data_train = tf.placeholder(
            tf.int32, shape=(None, self.n_classes))  # Define this

        # Network prediction
        Y_net_train = self.inference(
            X_data_train, reuse=False)

        # Loss of train data
        self.train_loss = tf.reduce_mean(tf.nn.sparce_softmax_cross_entropy_with_logits(
            labels=Y_data_train, logits=Y_net_train, name='train_loss'))

        # define learning rate decay method
        global_step = tf.Variable(0, trainable=False, name='global_step')
        # Define it--play with this
        learning_rate = 0.001

        # define the optimization algorithm
        # Define it --shall we try different type of optimizers
        optimizer = tf.train.AdamOptimizer(learning_rate)

        trainable = tf.trainable_variables()  # may be the weights??
        self.update_ops = optimizer.minimize(
            self.train_loss, var_list=trainable, global_step=global_step)

        # --- Validation computations
        X_data_valid = tf.placeholder(tf.float32, shape=(
            None, self.height, self.width, self.chan))  # Define this
        Y_data_valid = tf.placeholder(
            tf.int32, shape=(None, self.n_classes))  # Define this

        # Network prediction
        Y_net_valid = self.inference(
            X_data_valid, reuse=True)

        # Loss of validation data
        self.valid_loss = tf.reduce_mean(tf.nn.sparce_softmax_cross_entropy_with_logits(
            labels=Y_data_valid, logits=Y_net_valid, name='valid_loss'))

    # def read_nxt_batch(self):

    def train_epoch(self, sess):
        train_loss = 0
        total_batches = 0
        n_batches = self.train_size / self.batch_size  # ??
        self.shuffling(self.tindx)  # shuffle
        while (total_batches < n_batches):     # loop through train batches:
            mean_loss, _ = sess.run([self.train_loss, self.update_ops], feed_dict={X_train: self.Xtrain_in[self.tindx[(total_batches * self.batch_size):(
                total_batches + 1) * (self.batch_size - 1)]], Y_train: Ytrain_in[self.tindx[(total_batches * self.batch_size):(total_batches + 1) * (self.batch_size - 1)]]})
            if math.isnan(mean_loss):
                print('train cost is NaN')
                break
            train_loss += mean_loss
            total_batches += 1

        if total_batches > 0:
            train_loss /= total_batches

        return train_loss

    def valid_epoch(self, sess):
        valid_loss = 0
        total_batches = 0
        n_batches = self.dev_size / self.batch_size  # number of elements
        self.shuffling(self.vindx)  # shuffle
        # Loop through valid batches:
        while (total_batches < n_batches):
            mean_loss = sess.run(self.valid_loss, feed_dict={X_val: self.Xvalid_in[self.vindx[total_batches * self.batch_size: (total_batches + 1) * (self.batch_size - 1)]], Y_val: Ytrain_in[total_batches * self.batch_size: (total_batches + 1) * (self.batch_size - 1)]]})
            if math.isnan(mean_loss):
                print('valid cost is NaN')
                break
            valid_loss += mean_loss
            total_batches += 1

        if total_batches > 0:
            valid_loss /= total_batches

        return valid_loss

    def train(self, sess):
        start_time = time.clock()

        n_early_stop_epochs = 100  # Define it
        n_epochs = 100  # Define it

        saver = tf.train.Saver(
            var_list = tf.trainable_variables(), max_to_keep = 4)

        early_stop_counter=0

        init_op=tf.group(tf.global_variables_initializer())

        sess.run(init_op)

        min_valid_loss=sys.float_info.max
        epoch=0
        while (epoch < n_epochs):
            epoch += 1
            epoch_start_time=time.clock()

            train_loss=self.train_epoch(sess)
            valid_loss=self.valid_epoch(sess)

            epoch_end_time=time.clock()

            info_str='Epoch=' +
                str(epoch) + ', Train: ' + str(train_loss) + ', Valid: '
            info_str += str(valid_loss) + ', Time=' +
                str(epoch_end_time - epoch_start_time)
            print(info_str)

            if valid_loss < min_valid_loss:
                print('Best epoch=' + str(epoch))
                save_variables(sess, saver, epoch, self.model_id)
                min_valid_loss=valid_loss
                early_stop_counter=0
            else:
                early_stop_counter += 1

            if early_stop_counter > n_early_stop_epochs:
                # too many consecutive epochs without surpassing the best model
                print('stopping early')
                break

        end_time=time.clock()
        print('Total time = ' + str(end_time - start_time))

    def define_predict_operations(self):
        self.X_data_test_placeholder=tf.placeholder(
            tf.float32, shape = (None, self.height, self.width, self.chan))  # ??

        self.Y_net_test=self.inference(
            self.X_data_test_placeholder, reuse = False)

    def predict_utterance(self, sess, Xeval, Yeval):

        Yhat=self.Y_net_test  # variables of functions are the visible with self.??

        Ypredict=tf.argmax(Yhat, axis = 1, output_type = tf.int32)
        Ycorrect=tf.argmax(Y, axis = 1, output_type = tf.int32)

        # CAst boolean tensor to float
        corrrect=tf.cast(tf.equal(Ypredict, Ycorrect), tf.float32)
        accuracy_graph=tf.reduce_mean(correct)
        accuracy=sess.run(accuracy_graph, feed_dict = {X: Xeval, Y: Yeval})

        return accuracy
