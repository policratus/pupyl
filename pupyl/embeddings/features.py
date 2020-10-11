"""Factory for image feature extraction."""
from enum import Enum, auto
import warnings
import os

from pupyl.verbosity import quiet_tf
quiet_tf()

import tensorflow.keras.backend as backend
import tensorflow.keras.applications as networks
import tensorflow
import numpy
import termcolor

from pupyl.duplex.image import ImageIO
from pupyl.embeddings import exceptions


class Characteristics(Enum):
    """Describes high level characteristics of complex feature extractors."""

    # MobileNetV2
    LIGHTWEIGHT_REGULAR_PRECISION = auto()
    # DenseNet169
    MEDIUMWEIGHT_GOOD_PRECISION = auto()
    # NASNetLarge
    HEAVYWEIGHT_HUGE_PRECISION = auto()

    @staticmethod
    def by_name(name):
        """
        Return a characteristic by name.

        Parameters
        ----------
        name: str
            String representation of enumerator
        """
        return Characteristics[name]


class Extractors(ImageIO):
    """Pretrained CNNs for embeddings generation."""

    def __init__(self, characteristics):
        """
        Create embedding extractors.

        Parameters
        ----------
        characteristics: Enum
            Describing the intended characteristics to transform images
            into embeddings
        """
        self.acceleration_discovery()

        self._characteristics = characteristics

        self.converter, self.network = self._infer_network()
        self.image_input_shape = self.network.input_shape[1:3]
        self._features_output_shape = self.network.output_shape[1]

    def __enter__(self):
        """Open Extractors context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close Extractors context."""
        del exc_type, exc_val, exc_tb

        backend.clear_session()

    @property
    def output_shape(self):
        """
        Getter for property output_shape.

        Describes the output shape of extracted features.
        """
        return self._features_output_shape

    @staticmethod
    def acceleration_discovery():
        """
        Perform a hardware processing acceleration discovery.

        Most GPUs supported (through CUDA), which results on
        faster embeddings extraction.
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
        """Translate a characteristic to a network architecture."""
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
        Image preprocessing methods, suitable for posterior network ingestion.

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
        Convert image uri to its embeddings.

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
        ).ravel()

    @staticmethod
    def save_tensor(func_gen, uri, file_name):
        """
        Saves an arbitrary tensor to file.

        Parameters
        ----------
        func_gen: function
            The generator function of the tensor.

        uri: str
            Location of image to generate tensor.

        file_name: str
            Path with file name.
        """
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        numpy.save(
            file_name,
            func_gen(uri),
            allow_pickle=False,
            fix_imports=False
        )

    @staticmethod
    def load_tensor(file_name):
        """
        Saves an arbitrary tensor to file.

        Parameters
        ----------
        file_name: str
            The file name inside features database.
        """
        return numpy.load(
            file_name,
            mmap_mode='r',
            allow_pickle=False,
            fix_imports=False
        )
