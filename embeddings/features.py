"""
Factory for image feature extraction
"""
import warnings
from enum import Enum, auto

import numpy
import tensorflow
import tensorflow.keras.applications as networks
import tensorflow.keras.backend as backend
import termcolor

from embeddings import exceptions
from duplex.image import ImageIO


class Characteristics(Enum):
    """
    Describes high level characteristics
    of complex feature extractors
    """
    # MobileNetV2
    LIGHTWEIGHT_REGULAR_PRECISION = auto()
    # DenseNet169
    MEDIUMWEIGHT_GOOD_PRECISION = auto()
    # NASNetLarge
    HEAVYWEIGHT_HUGE_PRECISION = auto()


class Extractors(ImageIO):
    """
    Pretrained CNNs for embeddings generation
    """
    def __init__(
        self,
        characteristics=Characteristics.LIGHTWEIGHT_REGULAR_PRECISION
    ):
        """
        Creates embeddings generators

        Parameters
        ----------
        characteristics (optional): Enum
            Default: Characteristics.LIGHTWEIGHT_REGULAR_PRECISION

            Describing the intended characteristics to transform images
            into embeddings
        """
        super().__init__()

        self.acceleration_discovery()

        self._characteristics = characteristics

        self.converter, self.network = self._infer_network()
        self.image_input_shape = self.network.input_shape[1:3]

    def __enter__(self):
        """
        Opening Extractors context
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closing Extractors context
        """
        del exc_type, exc_val, exc_tb

        backend.clear_session()

    @staticmethod
    def acceleration_discovery():
        """
        Performs a hardware processing acceleration discovery
        for faster embeddings extraction
        """
        # If GPU(s) device(s) are found, avoid excessive VRAM consumption
        for gpu in tensorflow.config.experimental.list_physical_devices('GPU'):
            print(
                termcolor.colored(
                    'GPU found! Using it for embeddings '
                    'extraction acceleration.',
                    color='blue',
                    attrs=['bold']
                )
            )

            try:
                tensorflow.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError:
                warnings.warn(
                    termcolor.colored(
                        'Trying to define memory growth for an '
                        'already initialized GPU',
                        color='blue',
                        attrs=['bold']
                    ),
                    ResourceWarning
                )

    def _infer_network(self):
        """
        Translates a characteristic to a network
        architecture
        """
        # Networks general configurations
        weights = 'imagenet'
        pooling = 'max'
        include_top = False
        input_shape = (224, 224, 3)
        input_shape_nasnet_large = (331, 331, 3)

        if self._characteristics is \
                Characteristics.LIGHTWEIGHT_REGULAR_PRECISION:
            return networks.mobilenet_v2.preprocess_input, \
                networks.mobilenet_v2.MobileNetV2(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=input_shape
                )

        if self._characteristics is \
                Characteristics.MEDIUMWEIGHT_GOOD_PRECISION:
            return networks.densenet.preprocess_input, \
                networks.densenet.DenseNet169(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=input_shape
                )

        if self._characteristics is \
                Characteristics.HEAVYWEIGHT_HUGE_PRECISION:
            return networks.nasnet.preprocess_input, \
                networks.nasnet.NASNetLarge(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    # Specific shape for NASNetLarge
                    input_shape=input_shape_nasnet_large
                )

        raise exceptions.UnknownCharacteristics

    def preprocessor(self, uri):
        """
        Image preprocessing before network
        ingestion

        Parameters
        ----------
        image: numpy.ndarray
            Tensor which represents an image

        Returns
        -------
        numpy.ndarray
            Containing the processed image
        """
        return numpy.expand_dims(
            self.converter(self.size(uri, self.image_input_shape)),
            axis=0
        )

    def extract(self, uri):
        """
        Converts image uri to its embeddings

        Parameters
        ----------
        uri: str
            Tensor which represents an image

        Returns
        -------
        numpy.ndarray
            1D tensor with extracted features
        """
        return self.network.predict(
            self.preprocessor(uri)
        )
