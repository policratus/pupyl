"""Factory for image feature extraction."""

import os
import warnings
from enum import Enum, auto

import termcolor

from pupyl.verbosity import quiet_tf
quiet_tf()

import numpy
import tensorflow
import keras.backend as backend
import keras.applications as networks

from pupyl.duplex.image import ImageIO
from pupyl.embeddings import exceptions


class Characteristics(Enum):
    """Describes high level characteristics of complex feature extractors.

    Notes
    -----
    The currently supported characteristics are:

    ``MINIMUMWEIGHT_FAST_SMALL_PRECISION # MobileNet``

    ``LIGHTWEIGHT_FAST_SMALL_PRECISION # ResNet50V2``

    ``LIGHTWEIGHT_FAST_SHORT_PRECISION # ResNet101V2``

    ``LIGHTWEIGHT_QUICK_SHORT_PRECISION # DenseNet169``

    ``MEDIUMWEIGHT_QUICK_GOOD_PRECISION # DenseNet201``

    ``MIDDLEWEIGHT_QUICK_GOOD_PRECISION # InceptionV3``

    ``MIDDLEWEIGHT_SLOW_GOOD_PRECISION # Xception``

    ``HEAVYWEIGHT_SLOW_GOOD_PRECISION # EfficientNetV2M``

    ``HEAVYWEIGHT_SLOW_HUGE_PRECISION # EfficientNetV2L``
    """
    # MobileNet
    MINIMUMWEIGHT_FAST_SMALL_PRECISION = auto()
    # ResNet50V2
    LIGHTWEIGHT_FAST_SMALL_PRECISION = auto()
    # ResNet101V2
    LIGHTWEIGHT_FAST_SHORT_PRECISION = auto()
    # DenseNet169
    LIGHTWEIGHT_QUICK_SHORT_PRECISION = auto()
    # DenseNet201
    MEDIUMWEIGHT_QUICK_GOOD_PRECISION = auto()
    # InceptionV3
    MIDDLEWEIGHT_QUICK_GOOD_PRECISION = auto()
    # Xception
    MIDDLEWEIGHT_SLOW_GOOD_PRECISION = auto()
    # EfficientNetV2M
    HEAVYWEIGHT_SLOW_GOOD_PRECISION = auto()
    # EfficientNetV2L
    HEAVYWEIGHT_SLOW_HUGE_PRECISION = auto()

    @staticmethod
    def by_name(name):
        """Returns a characteristic by its name.

        Parameters
        ----------
        name: str
            String representation of enumerator

        Raises
        ------
        UnknownCharacteristicsName:
            If ``name`` is unknown.

        Returns
        -------
        enum:
            The corresponding characteristic.
        """
        try:
            return Characteristics[name]
        except KeyError as key_error:
            raise exceptions.UnknownCharacteristicsName(
                f'Characteristic with name {name} is unknown.'
            ) from key_error

    @staticmethod
    def by_value(value):
        """Returns a characteristic by its value.

        Parameters
        ----------
        value: int
            Integer representing a characteristic

        Raises
        ------
        UnknownCharacteristicsValue:
            If ``value`` is unknown.

        Returns
        -------
        enum:
            The corresponding characteristic.
        """
        try:
            return Characteristics(value)
        except ValueError as value_error:
            raise exceptions.UnknownCharacteristicsValue(
                f'Characteristic with value {value} is unknown.'
            ) from value_error


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
        small_input_shape = (224, 224, 3)
        middle_input_shape = (299, 299, 3)
        large_input_shape = (480, 480, 3)

        if self._characteristics is \
                Characteristics.MINIMUMWEIGHT_FAST_SMALL_PRECISION:
            return networks.mobilenet.preprocess_input, \
                networks.mobilenet.MobileNet(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=small_input_shape
                )

        if self._characteristics is \
                Characteristics.LIGHTWEIGHT_FAST_SMALL_PRECISION:
            return networks.resnet_v2.preprocess_input, \
                networks.resnet_v2.ResNet50V2(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=small_input_shape
                )

        if self._characteristics is \
                Characteristics.LIGHTWEIGHT_FAST_SHORT_PRECISION:
            return networks.resnet_v2.preprocess_input, \
                networks.resnet_v2.ResNet101V2(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=small_input_shape
                )

        if self._characteristics is \
                Characteristics.LIGHTWEIGHT_QUICK_SHORT_PRECISION:
            return networks.densenet.preprocess_input, \
                networks.densenet.DenseNet169(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=small_input_shape
                )

        if self._characteristics is \
                Characteristics.MEDIUMWEIGHT_QUICK_GOOD_PRECISION:
            return networks.densenet.preprocess_input, \
                networks.densenet.DenseNet201(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=small_input_shape
                )

        if self._characteristics is \
                Characteristics.MIDDLEWEIGHT_QUICK_GOOD_PRECISION:
            return networks.inception_v3.preprocess_input, \
                networks.inception_v3.InceptionV3(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=middle_input_shape
                )

        if self._characteristics is \
                Characteristics.MIDDLEWEIGHT_SLOW_GOOD_PRECISION:
            return networks.xception.preprocess_input, \
                networks.xception.Xception(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=middle_input_shape
                )

        if self._characteristics is \
                Characteristics.HEAVYWEIGHT_SLOW_GOOD_PRECISION:
            return networks.efficientnet_v2.preprocess_input, \
                networks.efficientnet_v2.EfficientNetV2M(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=large_input_shape,
                    include_preprocessing=True
                )

        if self._characteristics is \
                Characteristics.HEAVYWEIGHT_SLOW_HUGE_PRECISION:
            return networks.efficientnet_v2.preprocess_input, \
                networks.efficientnet_v2.EfficientNetV2L(
                    weights=weights,
                    pooling=pooling,
                    include_top=include_top,
                    input_shape=large_input_shape,
                    include_preprocessing=True
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
        if self.is_animated_gif(uri):
            tensor = self.resize_tensor(
                self.mean_gif(uri), self.image_input_shape
            )
        else:
            tensor = self.size(uri, self.image_input_shape)

        return tensorflow.expand_dims(self.converter(tensor), axis=0)

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
        return tensorflow.squeeze(
            self.network.predict(self.preprocessor(uri), verbose=0)
        )

    def extract_save(self, path, uri):
        """Extracts features from an image, saving to disk after all.

        Parameters
        ----------
        path: str
            Where to store the tensor.

        uri: str
            Location of the image to be converted to a embedding.
        """
        if not os.path.exists(path):
            self.save(path, self.extract(uri))

    @staticmethod
    def save(path, tensor):
        """Writes down a ``tensor`` referencing ``index``.

        Parameters
        ----------
        path: str
            Where to store the tensor.

        tensor: Tensor
            The tensor itself, to be saved.
        """
        numpy.save(path, tensor.numpy(), allow_pickle=False, fix_imports=False)

    @staticmethod
    def load(path):
        """Loads up a ``tensor`` referencing ``index``.

        Parameters
        ----------
        path: str
            Where to load from the tensor.

        Returns
        -------
        numpy.ndarray
            Tensor loaded back again.
        """
        return numpy.load(path, mmap_mode=None, allow_pickle=False)
