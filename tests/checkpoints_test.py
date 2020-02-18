# Lint as: python3

# Copyright 2020 The Flax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for flax.examples.utils.checkpoints."""

import contextlib
import copy
import os
import shutil

from absl.testing import absltest
from flax.utils import checkpoints
from jax import test_util as jtu
import numpy as np


def shuffle(l):
  """Functional shuffle."""
  l = copy.copy(l)
  np.random.shuffle(l)
  return l


@contextlib.contextmanager
def tempdir():
  """Temporary directory context."""
  tmpdir = absltest.get_default_test_tmpdir()
  try:
    yield tmpdir
  finally:
    shutil.rmtree(tmpdir)


class CheckpointsTest(absltest.TestCase):

  def test_naturalsort(self):
    np.random.seed(0)
    tests = [
        ['file_1', 'file_2', 'file_10', 'file_11', 'file_21'],
        ['file_0.001', 'file_0.01', 'file_0.1', 'file_1'],
        ['file_-3.0', 'file_-2', 'file_-1', 'file_0.0'],
        ['file_1e1', 'file_1.0e2', 'file_1e3', 'file_1.0e4'],
        ['file_1', 'file_2', 'file_9', 'file_1.0e1', 'file_11'],
    ]
    for test in tests:
      self.assertEqual(test, checkpoints.natural_sort(shuffle(test)))

  def test_save_restore_checkpoints(self):
    with tempdir() as tmp_dir:
      test_object0 = {'a': np.array([0, 0, 0], np.int32),
                      'b': np.array([0, 0, 0], np.int32)}
      test_object1 = {'a': np.array([1, 2, 3], np.int32),
                      'b': np.array([1, 1, 1], np.int32)}
      test_object2 = {'a': np.array([4, 5, 6], np.int32),
                      'b': np.array([2, 2, 2], np.int32)}
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object0)
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, 0, prefix='test', keep=1)
      self.assertIn('test_0', os.listdir(tmp_dir))
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object1)
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, 1, prefix='test', keep=1)
      checkpoints.save_checkpoint(
          tmp_dir, test_object2, 2, prefix='test', keep=1)
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object2)
      checkpoints.save_checkpoint(
          tmp_dir, test_object2, 3, prefix='test', keep=2)
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, 4, prefix='test', keep=2)
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object1)

  def test_save_restore_checkpoints_w_float_steps(self):
    with tempdir() as tmp_dir:
      test_object0 = {'a': np.array([0, 0, 0], np.int32),
                      'b': np.array([0, 0, 0], np.int32)}
      test_object1 = {'a': np.array([1, 2, 3], np.int32),
                      'b': np.array([1, 1, 1], np.int32)}
      test_object2 = {'a': np.array([4, 5, 6], np.int32),
                      'b': np.array([2, 2, 2], np.int32)}
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, 0.0, prefix='test', keep=1)
      self.assertIn('test_0.0', os.listdir(tmp_dir))
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object1)
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, 2.0, prefix='test', keep=1)
      checkpoints.save_checkpoint(
          tmp_dir, test_object2, 1.0, prefix='test', keep=1)
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      jtu.check_eq(new_object, test_object1)
      checkpoints.save_checkpoint(
          tmp_dir, test_object2, 3.0, prefix='test', keep=2)
      checkpoints.save_checkpoint(
          tmp_dir, test_object1, -1.0, prefix='test', keep=2)
      new_object = checkpoints.restore_checkpoint(
          tmp_dir, test_object0, prefix='test')
      self.assertIn('test_3.0', os.listdir(tmp_dir))
      self.assertIn('test_2.0', os.listdir(tmp_dir))
      jtu.check_eq(new_object, test_object2)


if __name__ == '__main__':
  absltest.main()