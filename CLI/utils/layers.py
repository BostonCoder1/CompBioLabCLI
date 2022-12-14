from typing import List, Any
import tensorflow as tf
from keras.layers import PReLU, ELU, LeakyReLU, Activation, Conv2DTranspose, \
    Conv1D as kConv1D, BatchNormalization, Add, Dropout, Reshape, Lambda

BATCH_NORM = 'keras'


def _activation(activation, BN: bool = True, name=None, momentum: float = 0.9, training=None, config: str = BATCH_NORM):
    """
    A more general activation function, allowing to use just string (for prelu, leakyrelu and elu) and to add BN before applying the activation
    """

    def f(x):
        if BN and activation != 'selu':
            if config == 'keras':
                h = BatchNormalization(momentum=momentum)(x, training=training)
            elif config == 'tf' or config == 'tensorflow':
                h = BatchNorm(is_training=training)(x)
            else:
                raise ValueError('config should be either `keras`, `tf` or `tensorflow`')
        else:
            h = x
        if activation is None:
            return h
        if activation in ['prelu', 'leakyrelu', 'elu', 'selu']:
            if activation == 'prelu':
                return PReLU(name=name)(h)
            if activation == 'leakyrelu':
                return LeakyReLU(name=name)(h)
            if activation == 'elu':
                return ELU(name=name)(h)
        else:
            h = Activation(activation, name=name)(h)
            return h

    return f


# BatchNorm
def BatchNorm(momentum: float = 0.99, training: bool = True):
    def batchnorm(x, momentum: float = momentum, training: bool = training):
        return tf.layers.batch_normalization(x, momentum=momentum, training=training)

    def f(x):
        return Lambda(batchnorm, output_shape=tuple([xx for xx in x._keras_shape if xx is not None]))(x)

    return f


def Conv1D(filters, kernel_size, strides: int = 1, padding: str = 'same', dilation_rate: int = 1, activation=None, momentum: float = 0.9,
           training=None, BN: bool = True, config: str = BATCH_NORM,
           use_bias: bool = False, kernel_initializer: str = 'glorot_uniform', bias_initializer: str = 'zeros', kernel_regularizer=None,
           bias_regularizer=None,
           activity_regularizer=None, kernel_constraint=None, bias_constraint=None, dropout=None, name=None, **kwargs):
    """BN after AtrousConvolution1D and BEFORE activation function"""

    def f(x):
        h = x
        if dropout is not None:
            h = Dropout(dropout)(h)
        h = kConv1D(filters,
                    kernel_size,
                    strides=strides,
                    padding=padding,
                    dilation_rate=dilation_rate,
                    activation=None,
                    use_bias=use_bias,
                    kernel_initializer=kernel_initializer,
                    bias_initializer=bias_initializer,
                    kernel_regularizer=kernel_regularizer,
                    bias_regularizer=bias_regularizer,
                    activity_regularizer=activity_regularizer,
                    kernel_constraint=kernel_constraint,
                    bias_constraint=bias_constraint,
                    **kwargs)(h)
        h = _activation(activation, BN=BN, name=name, momentum=momentum, training=training, config=config)(h)
        return h

    return f


def Deconv1D(filters, kernel_size, strides: int = 2, padding: str = 'same', dilation_rate: int = 1, activation: str = "prelu", momentum: float = 0.9,
             BN: bool = True, config: str = BATCH_NORM,
             use_bias: bool = False, training=None, kernel_initializer: str = 'glorot_uniform', bias_initializer: str = 'zeros',
             kernel_regularizer=None, bias_regularizer=None,
             activity_regularizer=None, kernel_constraint=None, bias_constraint=None, dropout=None, name=None):
    """`strides` is the upsampling factor"""

    def f(x):
        shape: List[Any] = list(x._keras_shape[1:])
        assert len(shape) == 2, "The input should have a width and a depth dimensions (plus the batch dimensions)"
        new_shape: List[int] = shape[:-1] + [1] + [shape[-1]]
        h = Reshape(new_shape)(x)

        if dropout is not None:
            h = Dropout(dropout)(h)

        h = Conv2DTranspose(filters,
                            kernel_size,
                            strides=(strides, 1),
                            padding=padding,
                            dilation_rate=dilation_rate,
                            activation=None,
                            use_bias=use_bias,
                            kernel_initializer=kernel_initializer,
                            bias_initializer=bias_initializer,
                            kernel_regularizer=kernel_regularizer,
                            bias_regularizer=bias_regularizer,
                            activity_regularizer=activity_regularizer,
                            kernel_constraint=kernel_constraint,
                            bias_constraint=bias_constraint
                            )(h)
        h = _activation(activation, BN=BN, name=name, momentum=momentum, training=training, config=config)(h)
        shape = list(h._keras_shape[1:])
        new_shape = shape[:-2] + [filters]
        h = Reshape(new_shape)(h)
        return h

    return f
