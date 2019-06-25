import pytest
pytest.importorskip('accuracy_checker.launcher.onnx_launcher')

import cv2
import numpy as np

from accuracy_checker.launcher.launcher import create_launcher
from accuracy_checker.config import ConfigError


def get_onnx_test_model(models_dir):
    config = {
        "framework": "onnx_runtime",
        "model": str(models_dir / "samplenet.onnx"),
        "adapter": "classification",
        "device": "cpu",
    }
    return create_launcher(config)


class TestONNXRuntimeLauncher:
    def test_launcher_creates(self, models_dir):
        launcher = get_onnx_test_model(models_dir)
        assert launcher.inputs['data'] == [1, 3, 32, 32]
        assert launcher.output_blob == 'fc3'

    def test_infer(self, data_dir, models_dir):
        mx_test_model = get_onnx_test_model(models_dir)
        _, _, h, w = mx_test_model.inputs['data']
        img_raw = cv2.imread(str(data_dir / '1.jpg'))
        img_rgb = cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (w, h))
        input_blob = np.transpose([img_resized], (0, 3, 1, 2))
        res = mx_test_model.predict([{'data': input_blob.astype(np.float32)}], [{}])

        assert np.argmax(res[0]['fc3']) == 7


@pytest.mark.usefixtures('mock_path_exists')
class TestONNXRuntimeLauncherConfig:
    def test_missed_model_in_create_onnx_launcher_raises_config_error_exception(self):
        config = {'framework': 'onnx_runtime'}

        with pytest.raises(ConfigError):
            create_launcher(config)

    def test_unsupported_device_in_create_onnx_launcher_raises_config_error_exception(self):
        config = {'framework': 'onnx_runtime', 'model': 'model.onnx', 'device': 'UNSUPPORTED'}

        with pytest.raises(ConfigError):
            create_launcher(config)