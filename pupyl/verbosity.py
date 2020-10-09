"""Controls verbosity of some modules"""
import os
import logging


def quiet_tf():
    """Suppress some messages from tensorflow"""
    logging.getLogger('tensorflow').setLevel(
        logging.ERROR
    )
    os.environ['KMP_AFFINITY'] = 'noverbose'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    import tensorflow

    tensorflow.get_logger().setLevel(logging.ERROR)
    tensorflow.autograph.set_verbosity(3)
