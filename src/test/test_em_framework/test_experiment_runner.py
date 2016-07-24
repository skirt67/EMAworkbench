'''
Created on Aug 11, 2015

.. codeauthor:: jhkwakkel <j.h.kwakkel (at) tudelft (dot) nl>
'''
from __future__ import (absolute_import, print_function, division,
                        unicode_literals)
from ema_workbench.em_framework.util import NamedObjectMap

try:
    import unittest.mock as mock
except ImportError:
    import mock
import unittest

from ema_workbench.em_framework.experiment_runner import ExperimentRunner
from ema_workbench.em_framework.model import Model, AbstractModel
from ema_workbench.util import EMAError, CaseError
from ema_workbench.em_framework.parameters import Policy, Experiment


class MockMSI(Model):

    def run_model(self, case):
        Model.run_model(self, case)

    def model_init(self, policy, kwargs):
        Model.model_init(self, policy, kwargs)

class ExperimentRunnerTestCase(unittest.TestCase):
    
    def test_init(self):
        mockMSI = mock.Mock(spec=MockMSI)
        mockMSI.name = 'test'
        msis = {'test':mockMSI}

        runner = ExperimentRunner(msis, {})
        
        self.assertEqual(msis, runner.msis)
        self.assertEqual({}, runner.msi_initialization)
        self.assertEqual({}, runner.model_kwargs)
    
    
    def test_run_experiment(self):
        mockMSI = mock.Mock(spec=MockMSI)
        mockMSI.name = 'test'
        
        msis = NamedObjectMap(AbstractModel)
        msis['test'] = mockMSI

        runner = ExperimentRunner(msis, {})
        
        experiment = Experiment('test',
                                mockMSI.name,
                                Policy('none'),  
                                0, a=1, b=2)
        
        runner.run_experiment(experiment)

        self.assertEqual({('none', 'test'):mockMSI},runner.msi_initialization)
        
        mockMSI.run_model.assert_called_once_with({'a':1, 'b':2})
        mockMSI.model_init.assert_called_once_with(Policy('none'), {})
        mockMSI.reset_model.assert_called_once_with()
        
        # assert raises ema error
        mockMSI = mock.Mock(spec=MockMSI)
        mockMSI.name = 'test'
        mockMSI.model_init.side_effect = EMAError("message")
        
        msis = NamedObjectMap(AbstractModel)
        msis['test'] = mockMSI
        runner = ExperimentRunner(msis, {})
    
        experiment = Experiment('test',mockMSI.name,Policy('none'),  
                                0, a=1, b=2)
        self.assertRaises(EMAError, runner.run_experiment, experiment)

        # assert raises exception
        mockMSI = mock.Mock(spec=MockMSI)
        mockMSI.name = 'test'
        mockMSI.model_init.side_effect = Exception("message")
        
        msis = NamedObjectMap(AbstractModel)
        msis['test'] = mockMSI
        
        runner = ExperimentRunner(msis, {})
    
        experiment = {'a':1, 'b':2, 'policy':{'name':'none'}, 'model':'test', 
              'experiment id': 0}
        self.assertRaises(Exception, runner.run_experiment, experiment)
        
        # assert handling of case error
        mockMSI = mock.Mock(spec=MockMSI)
        mockMSI.name = 'test'
        mockMSI.run_model.side_effect = CaseError("message", {})
        msis = NamedObjectMap(AbstractModel)
        msis['test'] = mockMSI
        runner = ExperimentRunner(msis, {})
    
        experiment = Experiment('test',mockMSI.name,Policy('none'),  
                      0, a=1, b=2)

        runner.run_experiment(experiment)
        
if __name__ == "__main__":
    unittest.main()
