# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
from test.unit_test.utils import (
    get_accuracy_metric,
    get_custom_eval,
    get_custom_metric_no_eval,
    get_latency_metric,
    get_mock_openvino_model,
    get_mock_snpe_model,
    get_onnx_model,
    get_pytorch_model,
)
from unittest.mock import patch

import pytest

from olive.evaluator.metric import AccuracySubType, LatencySubType
from olive.evaluator.olive_evaluator import OnnxEvaluator, OpenVINOEvaluator, PyTorchEvaluator, SNPEEvaluator
from olive.systems.local import LocalSystem


class TestOliveEvaluator:

    ACCURACY_TEST_CASE = [
        (
            PyTorchEvaluator(),
            get_pytorch_model(),
            get_accuracy_metric(AccuracySubType.ACCURACY_SCORE),
            "olive.evaluator.accuracy.AccuracyScore",
            0.99,
        ),
        (
            PyTorchEvaluator(),
            get_pytorch_model(),
            get_accuracy_metric(AccuracySubType.F1_SCORE),
            "olive.evaluator.accuracy.F1Score",
            0.99,
        ),
        (
            PyTorchEvaluator(),
            get_pytorch_model(),
            get_accuracy_metric(AccuracySubType.PRECISION),
            "olive.evaluator.accuracy.Precision",
            0.99,
        ),
        (
            PyTorchEvaluator(),
            get_pytorch_model(),
            get_accuracy_metric(AccuracySubType.RECALL),
            "olive.evaluator.accuracy.Recall",
            0.99,
        ),
        (
            PyTorchEvaluator(),
            get_pytorch_model(),
            get_accuracy_metric(AccuracySubType.AUC),
            "olive.evaluator.accuracy.AUC",
            0.99,
        ),
        (
            OnnxEvaluator(),
            get_onnx_model(),
            get_accuracy_metric(AccuracySubType.ACCURACY_SCORE),
            "olive.evaluator.accuracy.AccuracyScore",
            0.99,
        ),
        (
            OnnxEvaluator(),
            get_onnx_model(),
            get_accuracy_metric(AccuracySubType.F1_SCORE),
            "olive.evaluator.accuracy.F1Score",
            0.99,
        ),
        (
            OnnxEvaluator(),
            get_onnx_model(),
            get_accuracy_metric(AccuracySubType.PRECISION),
            "olive.evaluator.accuracy.Precision",
            0.99,
        ),
        (
            OnnxEvaluator(),
            get_onnx_model(),
            get_accuracy_metric(AccuracySubType.RECALL),
            "olive.evaluator.accuracy.Recall",
            0.99,
        ),
        (
            OnnxEvaluator(),
            get_onnx_model(),
            get_accuracy_metric(AccuracySubType.AUC),
            "olive.evaluator.accuracy.AUC",
            0.99,
        ),
    ]

    @pytest.mark.parametrize(
        "evaluator, olive_model,metric,acc_subtype,expected_res",
        ACCURACY_TEST_CASE,
    )
    def test_evaluate_accuracy(self, evaluator, olive_model, metric, acc_subtype, expected_res):
        # setup
        with patch(f"{acc_subtype}.measure") as mock_acc:
            mock_acc.return_value = expected_res

            # execute
            actual_res = evaluator.evaluate(olive_model, [metric])

            # assert
            mock_acc.assert_called_once()
            for sub_type in metric.sub_types:
                assert expected_res == actual_res.get_value(metric.name, sub_type.name)

    LATENCY_TEST_CASE = [
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.AVG, LatencySubType.MAX), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.MAX), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.MIN), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P50), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P75), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P90), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P95), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P99), 1),
        (PyTorchEvaluator(), get_pytorch_model(), get_latency_metric(LatencySubType.P999), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.AVG), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.MAX), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.MIN), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P50), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P75), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P90), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P95), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P99), 1),
        (OnnxEvaluator(), get_onnx_model(), get_latency_metric(LatencySubType.P999), 1),
    ]

    @pytest.mark.parametrize(
        "evaluator,olive_model,metric,expected_res",
        LATENCY_TEST_CASE,
    )
    def test_evaluate_latency(self, evaluator, olive_model, metric, expected_res):
        # execute
        actual_res = evaluator.evaluate(olive_model, [metric])

        # assert
        for sub_type in metric.sub_types:
            assert expected_res > actual_res.get_value(metric.name, sub_type.name)

    CUSTOM_TEST_CASE = [
        (PyTorchEvaluator(), get_pytorch_model(), get_custom_eval(), 0.382715310),
        (OnnxEvaluator(), get_onnx_model(), get_custom_eval(), 0.382715310),
        (SNPEEvaluator(), get_mock_snpe_model(), get_custom_eval(), 0.382715310),
        (OpenVINOEvaluator(), get_mock_openvino_model(), get_custom_eval(), 0.382715310),
    ]

    @pytest.mark.parametrize(
        "evaluator,olive_model,metric,expected_res",
        CUSTOM_TEST_CASE,
    )
    def test_evaluate_custom(self, evaluator, olive_model, metric, expected_res):
        # execute
        actual_res = evaluator.evaluate(olive_model, [metric])

        # assert
        for sub_type in metric.sub_types:
            assert actual_res.get_value(metric.name, sub_type.name) == expected_res

    def test_evaluate_custom_no_eval(self):
        evaluator = PyTorchEvaluator()
        olive_model = get_pytorch_model()
        metric = get_custom_metric_no_eval()
        with pytest.raises(ValueError, match="evaluate_func or metric_func is not specified in the metric config"):
            evaluator.evaluate(olive_model, [metric])


@pytest.mark.skip(reason="Requires custom onnxruntime build with mpi enabled")
class TestDistributedOnnxEvaluator:
    def test_evaluate(self):
        from olive.model import DistributedOnnxModel

        filepaths = ["examples/switch/model_4n_2l_8e_00.onnx", "examples/switch/model_4n_2l_8e_01.onnx"]
        model = DistributedOnnxModel(filepaths, name="model_4n_2l_8e")

        user_config = {
            "user_script": "examples/switch/user_script.py",
            "dataloader_func": "create_dataloader",
            "batch_size": 1,
        }
        # accuracy_metric = get_accuracy_metric(AccuracySubType.ACCURACY_SCORE, user_config=user_config)
        latency_metric = get_latency_metric(LatencySubType.AVG, user_config=user_config)
        # metrics = [accuracy_metric, latency_metric]
        metrics = [latency_metric]

        target = LocalSystem()

        # execute
        actual_res = target.evaluate_model(model, metrics)

        # assert
        for sub_type in latency_metric.sub_types:
            assert actual_res.get_value(latency_metric.name, sub_type.name) > 1
