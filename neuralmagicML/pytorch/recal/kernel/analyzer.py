"""
Code related to monitory, analyzing, and reporting the kernel sparsity (model pruning) for a model's layers and params
"""

from typing import List, Union, Tuple
from torch import Tensor
from torch.nn import Module, Parameter

from neuralmagicML.pytorch.utils import tensor_sparsity


__all__ = ["ModuleKSAnalyzer"]


class ModuleKSAnalyzer(object):
    """
    Class for monitoring the kernel sparsity of a given param in a module
    """

    @staticmethod
    def analyze_layers(module: Module, layers: List[str], param_name: str = "weight"):
        """
        :param module: the module to create multiple analyzers for
        :param layers: the names of the layers to create analyzer for that are in the module
        :param param_name: the name of the param to monitor within each layer
        :return: a list of analyzers, one for each layer passed in and in the same order
        """
        analyzed = []

        for layer_name in layers:
            mod = module
            lays = layer_name.split(".")

            for lay in lays:
                mod = mod.__getattr__(lay)

            analyzed.append(ModuleKSAnalyzer(mod, layer_name, param_name))

        return analyzed

    def __init__(self, module: Module, name: str, param_name: str = "weight"):
        """
        Analyzer to get the sparsity of a given layer's parameter such activation weight

        :param module: the module containing the param to analyze the sparsity for
        :param name: name of the layer, used for tracking
        :param param_name: name of the parameter to analyze the sparsity for, defaults to weight
        """
        self._module = module
        self._name = name
        self._param_name = param_name
        self._param = self._module.__getattr__(self._param_name)  # type: Parameter

    @property
    def module(self) -> Module:
        """
        :return: the module containing the param to analyze the sparsity for
        """
        return self._module

    @property
    def name(self) -> str:
        """
        :return: name of the layer, used for tracking
        """
        return self._name

    @property
    def param_name(self) -> str:
        """
        :return: name of the parameter to analyze the sparsity for, defaults to weight
        """
        return self._param_name

    @property
    def tag(self) -> str:
        """
        :return: combines the layer name and param name in to a single string separated by a period
        """
        return "{}.{}".format(self.name, self.param_name)

    @property
    def param(self) -> Parameter:
        """
        :return: the parameter that is being monitored for kernel sparsity
        """
        return self._param

    @property
    def param_sparsity(self) -> Tensor:
        """
        :return: the sparsity of the contained parameter (how many zeros are in it)
        """
        return self.param_sparsity_dim(None)

    def param_sparsity_dim(
        self, dim: Union[None, int, Tuple[int, ...]] = None
    ) -> Tensor:
        """
        :param dim: a dimension(s) to calculate the sparsity over, ex over channels
        :return: the sparsity of the contained parameter structured according to the dim passed in
        """
        return tensor_sparsity(self._param.data, dim)