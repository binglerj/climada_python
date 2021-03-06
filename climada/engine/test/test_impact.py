"""
This file is part of CLIMADA.

Copyright (C) 2017 ETH Zurich, CLIMADA contributors listed in AUTHORS.

CLIMADA is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, version 3.

CLIMADA is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with CLIMADA. If not, see <https://www.gnu.org/licenses/>.

---

Test Impact class.
"""
import os
import unittest
import numpy as np
from scipy import sparse

from climada.entity.tag import Tag
from climada.hazard.tag import Tag as TagHaz
from climada.entity.entity_def import Entity
from climada.hazard.base import Hazard
from climada.engine.impact import Impact
from climada.util.constants import ENT_DEMO_TODAY

HAZ_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'hazard/test/data/')
HAZ_TEST_MAT = os.path.join(HAZ_DIR, 'atl_prob_no_name.mat')

DATA_FOLDER = os.path.join(os.path.dirname(__file__) , 'data')

class TestFreqCurve(unittest.TestCase):
    '''Test exceedence frequency curve computation'''
    def test_ref_value_pass(self):
        """Test result against reference value"""
        imp = Impact()
        imp.frequency = np.ones(10) * 6.211180124223603e-04
        imp.at_event = np.zeros(10)
        imp.at_event[0] = 0
        imp.at_event[1] = 0.400665463736549e9
        imp.at_event[2] = 3.150330960044466e9
        imp.at_event[3] = 3.715826406781887e9
        imp.at_event[4] = 2.900244271902339e9
        imp.at_event[5] = 0.778570745161971e9
        imp.at_event[6] = 0.698736262566472e9
        imp.at_event[7] = 0.381063674256423e9
        imp.at_event[8] = 0.569142464157450e9
        imp.at_event[9] = 0.467572545849132e9
        imp.unit = 'USD'

        ifc = imp.calc_freq_curve()
        self.assertEqual(10, len(ifc.return_per))
        self.assertEqual(1610.0000000000000, ifc.return_per[9])
        self.assertEqual(805.00000000000000, ifc.return_per[8])
        self.assertEqual(536.66666666666663, ifc.return_per[7])
        self.assertEqual(402.500000000000, ifc.return_per[6])
        self.assertEqual(322.000000000000, ifc.return_per[5])
        self.assertEqual(268.33333333333331, ifc.return_per[4])
        self.assertEqual(230.000000000000, ifc.return_per[3])
        self.assertEqual(201.250000000000, ifc.return_per[2])
        self.assertEqual(178.88888888888889, ifc.return_per[1])
        self.assertEqual(161.000000000000, ifc.return_per[0])
        self.assertEqual(10, len(ifc.impact))
        self.assertEqual(3.715826406781887e9, ifc.impact[9])
        self.assertEqual(3.150330960044466e9, ifc.impact[8])
        self.assertEqual(2.900244271902339e9, ifc.impact[7])
        self.assertEqual(0.778570745161971e9, ifc.impact[6])
        self.assertEqual(0.698736262566472e9, ifc.impact[5])
        self.assertEqual(0.569142464157450e9, ifc.impact[4])
        self.assertEqual(0.467572545849132e9, ifc.impact[3])
        self.assertEqual(0.400665463736549e9, ifc.impact[2])
        self.assertEqual(0.381063674256423e9, ifc.impact[1])
        self.assertEqual(0, ifc.impact[0])
        self.assertEqual('Exceedance frequency curve', ifc.label)
        self.assertEqual('USD', ifc.unit)

    def test_ref_value_rp_pass(self):
        """Test result against reference value with given return periods """
        imp = Impact()
        imp.frequency = np.ones(10) * 6.211180124223603e-04
        imp.at_event = np.zeros(10)
        imp.at_event[0] = 0
        imp.at_event[1] = 0.400665463736549e9
        imp.at_event[2] = 3.150330960044466e9
        imp.at_event[3] = 3.715826406781887e9
        imp.at_event[4] = 2.900244271902339e9
        imp.at_event[5] = 0.778570745161971e9
        imp.at_event[6] = 0.698736262566472e9
        imp.at_event[7] = 0.381063674256423e9
        imp.at_event[8] = 0.569142464157450e9
        imp.at_event[9] = 0.467572545849132e9
        imp.unit = 'USD'

        ifc = imp.calc_freq_curve(np.array([100, 500, 1000]))
        self.assertEqual(3, len(ifc.return_per))
        self.assertEqual(100, ifc.return_per[0])
        self.assertEqual(500, ifc.return_per[1])
        self.assertEqual(1000, ifc.return_per[2])
        self.assertEqual(3, len(ifc.impact))
        self.assertEqual(0, ifc.impact[0])
        self.assertEqual(2320408028.5695677, ifc.impact[1])
        self.assertEqual(3287314329.129928, ifc.impact[2])
        self.assertEqual('Exceedance frequency curve', ifc.label)
        self.assertEqual('USD', ifc.unit)

class TestOneExposure(unittest.TestCase):
    '''Test one_exposure function'''
    def test_ref_value_insure_pass(self):
        ''' Test result against reference value'''
        # Read demo entity values
        # Set the entity default file to the demo one
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.check()

        # Read default hazard file
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        # Create impact object
        impact = Impact()
        impact.at_event = np.zeros(hazard.intensity.shape[0])
        impact.eai_exp = np.zeros(len(ent.exposures.value))
        impact.tot_value = 0

        # Assign centroids to exposures
        ent.exposures.assign_centroids(hazard)

        # Compute impact for 6th exposure
        iexp = 5
        # Take its impact function
        imp_id = ent.exposures.if_TC[iexp]
        imp_fun = ent.impact_funcs.get_func(hazard.tag.haz_type, imp_id)
        # Compute
        insure_flag = True
        impact._exp_impact(np.array([iexp]), ent.exposures, hazard, imp_fun, insure_flag)

        self.assertEqual(impact.eai_exp.size, ent.exposures.shape[0])
        self.assertEqual(impact.at_event.size, hazard.intensity.shape[0])

        events_pos = hazard.intensity[:, ent.exposures.centr_TC[iexp]].nonzero()[0]
        res_exp = np.zeros((ent.exposures.shape[0]))
        res_exp[iexp] = np.sum(impact.at_event[events_pos] * hazard.frequency[events_pos])
        self.assertTrue(np.array_equal(res_exp, impact.eai_exp))

        self.assertEqual(0, impact.at_event[12])
        # Check first 3 values
        self.assertEqual(0, impact.at_event[12])
        self.assertEqual(0, impact.at_event[41])
        self.assertEqual(1.0626600695059455e+06, impact.at_event[44])

        # Check intermediate values
        self.assertEqual(0, impact.at_event[6281])
        self.assertEqual(0, impact.at_event[4998])
        self.assertEqual(0, impact.at_event[9527])
        self.assertEqual(1.3318063850487845e+08, impact.at_event[7192])
        self.assertEqual(4.667108555054083e+06, impact.at_event[8624])

        # Check last 3 values
        self.assertEqual(0, impact.at_event[14349])
        self.assertEqual(0, impact.at_event[14347])
        self.assertEqual(0, impact.at_event[14309])

class TestCalc(unittest.TestCase):
    ''' Test impact calc method.'''

    def test_ref_value_pass(self):
        ''' Test result against reference value'''
        # Read default entity values
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.check()

        # Read default hazard file
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        # Create impact object
        impact = Impact()

        # Assign centroids to exposures
        ent.exposures.assign_centroids(hazard)

        # Compute the impact over the whole exposures
        impact.calc(ent.exposures, ent.impact_funcs, hazard)

        # Check result
        num_events = len(hazard.event_id)
        num_exp = ent.exposures.shape[0]
        # Check relative errors as well when absolute value gt 1.0e-7
        # impact.at_event == EDS.damage in MATLAB
        self.assertEqual(num_events, len(impact.at_event))
        self.assertEqual(0, impact.at_event[0])
        self.assertEqual(0, impact.at_event[int(num_events/2)])
        self.assertAlmostEqual(1.472482938320243e+08, impact.at_event[13809])
        self.assertEqual(7.076504723057619e+10, impact.at_event[12147])
        self.assertEqual(0, impact.at_event[num_events-1])
        # impact.eai_exp == EDS.ED_at_centroid in MATLAB
        self.assertEqual(num_exp, len(impact.eai_exp))
        self.assertAlmostEqual(1.518553670803242e+08, impact.eai_exp[0])
        self.assertAlmostEqual(1.373490457046383e+08, \
                               impact.eai_exp[int(num_exp/2)], 6)
        self.assertTrue(np.isclose(1.373490457046383e+08, \
                                          impact.eai_exp[int(num_exp/2)]))
        self.assertAlmostEqual(1.066837260150042e+08, \
                               impact.eai_exp[num_exp-1], 6)
        self.assertTrue(np.isclose(1.066837260150042e+08, \
                                          impact.eai_exp[int(num_exp-1)]))
        # impact.tot_value == EDS.Value in MATLAB
        # impact.aai_agg == EDS.ED in MATLAB
        self.assertAlmostEqual(6.570532945599105e+11, impact.tot_value)
        self.assertAlmostEqual(6.512201157564421e+09, impact.aai_agg, 5)
        self.assertTrue(np.isclose(6.512201157564421e+09, impact.aai_agg))

    def test_calc_imp_mat_pass(self):
        """ Test save imp_mat """
         # Read default entity values
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.check()

        # Read default hazard file
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        # Create impact object
        impact = Impact()

        # Assign centroids to exposures
        ent.exposures.assign_centroids(hazard)

        # Compute the impact over the whole exposures
        impact.calc(ent.exposures, ent.impact_funcs, hazard, save_mat=True)
        self.assertTrue(isinstance(impact.imp_mat, sparse.csr_matrix))
        self.assertEqual(impact.imp_mat.shape, (hazard.event_id.size,
            ent.exposures.value.size))
        self.assertTrue(np.allclose(np.sum(impact.imp_mat, axis=1).reshape(-1),
            impact.at_event))
        self.assertTrue(np.allclose(np.array(np.sum(np.multiply(impact.imp_mat.todense(),
            impact.frequency.reshape(-1, 1)), axis=0)).reshape(-1), impact.eai_exp))

    def test_calc_if_pass(self):
        """ Execute when no if_HAZ present, but only if_ """
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.exposures.rename(columns={'if_TC':'if_'}, inplace=True)
        ent.check()
        
        # Read default hazard file
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        # Create impact object
        impact = Impact()
        impact.calc(ent.exposures, ent.impact_funcs, hazard)

        # Check result
        num_events = len(hazard.event_id)
        num_exp = ent.exposures.shape[0]
        # Check relative errors as well when absolute value gt 1.0e-7
        # impact.at_event == EDS.damage in MATLAB
        self.assertEqual(num_events, len(impact.at_event))
        self.assertEqual(0, impact.at_event[0])
        self.assertEqual(0, impact.at_event[int(num_events/2)])
        self.assertAlmostEqual(1.472482938320243e+08, impact.at_event[13809])
        self.assertEqual(7.076504723057619e+10, impact.at_event[12147])
        self.assertEqual(0, impact.at_event[num_events-1])
        # impact.eai_exp == EDS.ED_at_centroid in MATLAB
        self.assertEqual(num_exp, len(impact.eai_exp))
        self.assertAlmostEqual(1.518553670803242e+08, impact.eai_exp[0])
        self.assertAlmostEqual(1.373490457046383e+08, \
                               impact.eai_exp[int(num_exp/2)], 6)
        self.assertTrue(np.isclose(1.373490457046383e+08, \
                                          impact.eai_exp[int(num_exp/2)]))
        self.assertAlmostEqual(1.066837260150042e+08, \
                               impact.eai_exp[num_exp-1], 6)
        self.assertTrue(np.isclose(1.066837260150042e+08, \
                                          impact.eai_exp[int(num_exp-1)]))
        # impact.tot_value == EDS.Value in MATLAB
        # impact.aai_agg == EDS.ED in MATLAB
        self.assertAlmostEqual(6.570532945599105e+11, impact.tot_value)
        self.assertAlmostEqual(6.512201157564421e+09, impact.aai_agg, 5)
        self.assertTrue(np.isclose(6.512201157564421e+09, impact.aai_agg))

class TestImpactYearSet(unittest.TestCase):
    '''Test calc_impact_year_set method'''

    def test_impact_year_set_sum(self):
        """Test result against reference value with given events """
        imp = Impact()
        imp.frequency = np.ones(10) * 6.211180124223603e-04
        imp.at_event = np.zeros(10)
        imp.at_event[0] = 0
        imp.at_event[1] = 0.400665463736549e9
        imp.at_event[2] = 3.150330960044466e9
        imp.at_event[3] = 3.715826406781887e9
        imp.at_event[4] = 2.900244271902339e9
        imp.at_event[5] = 0.778570745161971e9
        imp.at_event[6] = 0.698736262566472e9
        imp.at_event[7] = 0.381063674256423e9
        imp.at_event[8] = 0.569142464157450e9
        imp.at_event[9] = 0.467572545849132e9
        imp.unit = 'USD'   
        imp.date = np.array([732801, 716160, 718313, 712468, 732802, \
                             729285, 732931, 715419, 722404, 718351])

        iys_all = imp.calc_impact_year_set()
        iys = imp.calc_impact_year_set(all_years=False)
        self.assertEqual(np.around(sum([iys[year] for year in iys])), \
                         np.around(sum(imp.at_event)))
        self.assertEqual(sum([iys[year] for year in iys]), \
                         sum([iys_all[year] for year in iys_all]))
        self.assertEqual(len(iys), 7)
        self.assertEqual(len(iys_all), 57)
        self.assertIn(1951 and 1959 and 2007, iys_all)
        self.assertTrue(iys_all[1959]>0)
        self.assertAlmostEqual(3598980534.468811, iys_all[2007])
        self.assertEqual(iys[1978], iys_all[1978])
        self.assertAlmostEqual(iys[1951], imp.at_event[3])

class TestIO(unittest.TestCase):
    ''' Test impact input/output methods.'''

    def test_write_read_ev_test(self):
        ''' Test result against reference value'''
        # Create impact object
        num_ev = 10
        num_exp = 5
        imp_write = Impact()
        imp_write.tag = {'exp': Tag('file_exp.p', 'descr exp'),
                         'haz': TagHaz('TC', 'file_haz.p', 'descr haz'),
                         'if_set': Tag()}
        imp_write.event_id = np.arange(num_ev)
        imp_write.event_name = ['event_'+str(num) for num in imp_write.event_id]
        imp_write.date = np.ones(num_ev)
        imp_write.coord_exp = np.zeros((num_exp, 2))
        imp_write.coord_exp[:, 0] = 1.5
        imp_write.coord_exp[:, 1] = 2.5
        imp_write.eai_exp = np.arange(num_exp) * 100
        imp_write.at_event = np.arange(num_ev) * 50
        imp_write.frequency = np.ones(num_ev) * 0.1
        imp_write.tot_value = 1000
        imp_write.aai_agg = 1001
        imp_write.unit = 'USD'

        file_name = os.path.join(DATA_FOLDER, 'test.csv')
        imp_write.write_csv(file_name)

        imp_read = Impact()
        imp_read.read_csv(file_name)
        self.assertTrue(np.array_equal(imp_write.event_id, imp_read.event_id))
        self.assertTrue(np.array_equal(imp_write.date, imp_read.date))
        self.assertTrue(np.array_equal(imp_write.coord_exp, imp_read.coord_exp))
        self.assertTrue(np.array_equal(imp_write.eai_exp, imp_read.eai_exp))
        self.assertTrue(np.array_equal(imp_write.at_event, imp_read.at_event))
        self.assertTrue(np.array_equal(imp_write.frequency, imp_read.frequency))
        self.assertEqual(imp_write.tot_value, imp_read.tot_value)
        self.assertEqual(imp_write.aai_agg, imp_read.aai_agg)
        self.assertEqual(imp_write.unit, imp_read.unit)
        self.assertEqual(0, len([i for i, j in
            zip(imp_write.event_name, imp_read.event_name) if i != j]))

    def test_write_read_exp_test(self):
        ''' Test result against reference value'''
        # Create impact object
        num_ev = 5
        num_exp = 10
        imp_write = Impact()
        imp_write.tag = {'exp': Tag('file_exp.p', 'descr exp'),
                         'haz': TagHaz('TC', 'file_haz.p', 'descr haz'),
                         'if_set': Tag()}
        imp_write.event_id = np.arange(num_ev)
        imp_write.event_name = ['event_'+str(num) for num in imp_write.event_id]
        imp_write.date = np.ones(num_ev)
        imp_write.coord_exp = np.zeros((num_exp, 2))
        imp_write.coord_exp[:, 0] = 1.5
        imp_write.coord_exp[:, 1] = 2.5
        imp_write.eai_exp = np.arange(num_exp) * 100
        imp_write.at_event = np.arange(num_ev) * 50
        imp_write.frequency = np.ones(num_ev) * 0.1
        imp_write.tot_value = 1000
        imp_write.aai_agg = 1001
        imp_write.unit = 'USD'

        file_name = os.path.join(DATA_FOLDER, 'test.csv')
        imp_write.write_csv(file_name)

        imp_read = Impact()
        imp_read.read_csv(file_name)
        self.assertTrue(np.array_equal(imp_write.event_id, imp_read.event_id))
        self.assertTrue(np.array_equal(imp_write.date, imp_read.date))
        self.assertTrue(np.array_equal(imp_write.coord_exp, imp_read.coord_exp))
        self.assertTrue(np.array_equal(imp_write.eai_exp, imp_read.eai_exp))
        self.assertTrue(np.array_equal(imp_write.at_event, imp_read.at_event))
        self.assertTrue(np.array_equal(imp_write.frequency, imp_read.frequency))
        self.assertEqual(imp_write.tot_value, imp_read.tot_value)
        self.assertEqual(imp_write.aai_agg, imp_read.aai_agg)
        self.assertEqual(imp_write.unit, imp_read.unit)
        self.assertEqual(0, len([i for i, j in
            zip(imp_write.event_name, imp_read.event_name) if i != j]))
        self.assertIsInstance(imp_read.crs, dict)

    def test_write_read_excel_pass(self):
        """ Test write and read in excel """
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.check()

        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        imp_write = Impact()
        ent.exposures.assign_centroids(hazard)
        imp_write.calc(ent.exposures, ent.impact_funcs, hazard)
        file_name = os.path.join(DATA_FOLDER, 'test.xlsx')
        imp_write.write_excel(file_name)

        imp_read = Impact()
        imp_read.read_excel(file_name)

        self.assertTrue(np.array_equal(imp_write.event_id, imp_read.event_id))
        self.assertTrue(np.array_equal(imp_write.date, imp_read.date))
        self.assertTrue(np.array_equal(imp_write.coord_exp, imp_read.coord_exp))
        self.assertTrue(np.allclose(imp_write.eai_exp, imp_read.eai_exp))
        self.assertTrue(np.allclose(imp_write.at_event, imp_read.at_event))
        self.assertTrue(np.array_equal(imp_write.frequency, imp_read.frequency))
        self.assertEqual(imp_write.tot_value, imp_read.tot_value)
        self.assertEqual(imp_write.aai_agg, imp_read.aai_agg)
        self.assertEqual(imp_write.unit, imp_read.unit)
        self.assertEqual(0, len([i for i, j in
            zip(imp_write.event_name, imp_read.event_name) if i != j]))
        self.assertIsInstance(imp_read.crs, dict)

    def test_write_imp_mat(self):
        """ Test write_excel_imp_mat function """
        impact = Impact()
        impact.imp_mat = sparse.lil_matrix(np.zeros((5, 4)))
        impact.imp_mat[0, :] = np.arange(4)
        impact.imp_mat[1, :] = np.arange(4)*2
        impact.imp_mat[2, :] = np.arange(4)*3
        impact.imp_mat[3, :] = np.arange(4)*4
        impact.imp_mat[4, :] = np.arange(4)*5
        impact.imp_mat = impact.imp_mat.tocsr()

        file_name = os.path.join(DATA_FOLDER, 'test_imp_mat')
        impact.write_sparse_csr(file_name)
        read_imp_mat = Impact().read_sparse_csr(file_name+'.npz')
        for irow in range(5):
            self.assertTrue(np.array_equal(np.array(read_imp_mat[irow, :].todense()).reshape(-1),
                np.array(impact.imp_mat[irow, :].todense()).reshape(-1)))


# Execute Tests
if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestOneExposure)
    TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCalc))
    TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFreqCurve))
    TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestImpactYearSet))
    TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIO))
    unittest.TextTestRunner(verbosity=2).run(TESTS)
