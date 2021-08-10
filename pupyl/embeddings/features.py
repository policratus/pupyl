"""Factory for image feature extraction."""

import warnings
from enum import Enum, auto

import termcolor
import numpy

from pupyl.verbosity import quiet_tf
quiet_tf()

import tensorflow
import tensorflow.keras.backend as backend
import tensorflow.keras.applications as networks

from pupyl.duplex.image import ImageIO
from pupyl.embeddings import exceptions


class Characteristics(Enum):
    """Describes high level characteristics of complex feature extractors.

    Notes
    -----
    The actual supported characteristics are:

    ``LIGHTWEIGHT_REGULAR_PRECISION # MobileNetV2``

    ``MEDIUMWEIGHT_GOOD_PRECISION # DenseNet169``

    ``HEAVYWEIGHT_HUGE_PRECISION # EfficientNetB7``
    """
    # MobileNetV2
    LIGHTWEIGHT_REGULAR_PRECISION = auto()
    # DenseNet169
    MEDIUMWEIGHT_GOOD_PRECISION = auto()
    # EfficientNetB7
    HEAVYWEIGHT_HUGE_PRECISION = auto()

    @staticmethod
    def by_name(name):
        """Returns a characteristic by its name.

        Parameters
        ----------
        name: str
            String representation of enumerator

        Raises
        ------
        KeyError:
            If ``name`` is unknown.

        Returns
        -------
        enum:
            The corresponding characteristic.
        """
        return Characteristics[name]


class Extractors(ImageIO):
    """Pretrained CNNs for embedding generation."""

    def __init__(self, characteristics, extreme_mode=True):
        """
        Creates embedding extractors.

        Parameters
        ----------
        characteristics: Enum
            Describing the intended characteristics to transform images
            into its underlying embeddings.

        extreme_mode: bool
            Should the extreme mode (faster execution but not gentle with
            memory) be enabled or disabled?
        """
        self._characteristics = characteristics
        self._extreme_mode = extreme_mode

        self.acceleration_discovery()

        self.converter, self.network = self._infer_network()
        self.image_input_shape = self.network.input_shape[1:3]
        self._features_output_shape = self.network.output_shape[1]

    def __enter__(self):
        """Opens Extractors context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close Extractors context."""
        del exc_type, exc_val, exc_tb

        backend.clear_session()

    @property
    def output_shape(self):
        """Getter for property output_shape.

        Describes the output shape of extracted features.

        Returns
        -------
        int:
            The output shape for the picked characteristics.
        """
        return self._features_output_shape

    def acceleration_discovery(self):
        """Performs a hardware processing acceleration discovery.

        Most NVIDIA® GPUs supported (through ``CUDA``), which results on
        faster embeddings extraction.
        """
        # If GPU(s) device(s) are found, avoid excessive VRAM consumption
        for gpu in tensorflow.config.list_physical_devices('GPU'):
            print(
                termcolor.colored(
                    'GPU found! Using it for embeddings '
                    'extraction acceleration.',
                    color='blue',
                    attrs=['bold']
                )
            )

            if not self._extreme_mode:
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
        """Translates a characteristic to a network architecture.

        Raises
        ------
        UnknownCharacteristics:
            If the characteristics passed through are unknown.

        Returns
        -------
        tuple:
            With preprocessors and complete CNN architecture.
        """
        # Networks general configurations
        weights = 'imagenet'
        pooling = 'max'
        include_top = False
        input_shape = (224, 224, 3)

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
            return networks.efficientnet.preprocess_input, \
                networks.efficientnet.EfficientNetB7(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=input_shape
                )

        raise exceptions.UnknownCharacteristics(
            f'Characteristic {self._characteristics}'
            ' is invalid.'
        )

    def preprocessor(self, uri):
        """Image preprocessing methods, suitable for posterior network
        ingestion. It may include image resizing, normalization, among others.

        Parameters
        ----------
        uri: str
            Location of the image to be preprocessed.

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
        """Converts image uri to its embeddings.

        Parameters
        ----------
        uri: str
            Location of the image to be converted to a embedding.

        Returns
        -------
        numpy.ndarray
            1D tensor with extracted features.
        """
        return tensorflow.squeeze(self.network.predict(self.preprocessor(uri)))
