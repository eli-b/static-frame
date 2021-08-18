

import unittest

import frame_fixtures as ff

from static_frame.test.test_case import TestCase
from static_frame.core.bus import Bus
# from static_frame.core.exception import ErrorInitQuilt
# from static_frame.core.exception import AxisInvalid
# from static_frame.core.exception import ErrorInitYarn

# from static_frame.core.axis_map import AxisMap
# from static_frame.core.index import Index
# from static_frame.core.axis_map import IndexMap

from static_frame.core.yarn import Yarn
from static_frame.core.frame import Frame
from static_frame.test.test_case import temp_file


class TestUnit(TestCase):

    #---------------------------------------------------------------------------
    def test_yarn_from_buses_a(self) -> None:

        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')


        y1 = Yarn.from_buses((b1, b2), retain_labels=True)
        self.assertEqual(len(y1), 5)
        self.assertEqual(y1.index.shape, (5, 2))
        self.assertEqual(y1.shape, (5,))
        self.assertEqual(y1.size, 5)
        self.assertEqual(y1.dtype, object)
        self.assertEqual(y1.ndim, 1)

        y3 = y1[('a', 'f2'):] #type: ignore
        self.assertEqual(y3.shape, (4,))

        y2 = Yarn.from_buses((b1, b2), retain_labels=False)
        self.assertEqual(len(y2), 5)
        self.assertEqual(y2.index.shape, (5,))
        self.assertEqual(y1.shape, (5,))
        self.assertEqual(y1.size, 5)
        self.assertEqual(y1.dtype, object)
        self.assertEqual(y1.ndim, 1)


    def test_yarn_from_buses_b(self) -> None:

        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=True)
        self.assertEqual(y1.shape, (7,))
        self.assertEqual(len(y1), 7)

    #---------------------------------------------------------------------------
    def test_yarn_max_persist(self) -> None:
        f1 = ff.parse('s(4,2)').rename('f1')
        f2 = ff.parse('s(4,5)').rename('f2')
        f3 = ff.parse('s(2,2)').rename('f3')
        f4 = ff.parse('s(2,8)').rename('f4')
        f5 = ff.parse('s(4,4)').rename('f5')
        f6 = ff.parse('s(6,4)').rename('f6')

        b1 = Bus.from_frames((f1, f2, f3))
        b2 = Bus.from_frames((f4, f5, f6))

        with temp_file('.zip') as fp1, temp_file('.zip') as fp2:
            b1.to_zip_pickle(fp1)
            b2.to_zip_pickle(fp2)


            bus_a = Bus.from_zip_pickle(fp1, max_persist=1).rename('a')
            bus_b = Bus.from_zip_pickle(fp2, max_persist=1).rename('b')

            y1 = Yarn.from_buses((bus_a, bus_b), retain_labels=False)
            self.assertEqual(y1.nbytes, 0)
            self.assertEqual(y1.status['loaded'].sum(), 0)

            self.assertEqual(y1['f2'].shape, (4, 5))
            self.assertEqual(y1['f6'].shape, (6, 4))
            self.assertEqual(y1.nbytes, 352)
            self.assertEqual(y1.status['loaded'].sum(), 2)

            self.assertEqual(y1.shapes.to_pairs(),
                    (('f1', None), ('f2', (4, 5)), ('f3', None), ('f4', None), ('f5', None), ('f6', (6, 4)))
                    )
            self.assertEqual(y1.mloc.isna().sum(), 4)
            self.assertEqual((y1.dtypes == float).sum().sum(), 9)

    #---------------------------------------------------------------------------
    def test_yarn_from_concat_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_concat((b1, b2, b3), retain_labels=False)
        self.assertEqual(y1.shape, (7,))

    def test_yarn_from_concat_b(self) -> None:
        f1 = ff.parse('s(4,2)').rename('f1')
        f2 = ff.parse('s(4,5)').rename('f2')
        f3 = ff.parse('s(2,2)').rename('f3')
        f4 = ff.parse('s(2,8)').rename('f4')
        f5 = ff.parse('s(4,4)').rename('f5')
        f6 = ff.parse('s(6,4)').rename('f6')

        b1 = Bus.from_frames((f1, f2, f3))
        b2 = Bus.from_frames((f4, f5, f6))

        with temp_file('.zip') as fp1, temp_file('.zip') as fp2:
            b1.to_zip_pickle(fp1)
            b2.to_zip_pickle(fp2)

            bus_a = Bus.from_zip_pickle(fp1, max_persist=1).rename('a')
            bus_b = Bus.from_zip_pickle(fp2, max_persist=1).rename('b')

            y1 = Yarn.from_concat((bus_a, bus_b), retain_labels=False)
            self.assertEqual(y1.shape, (6,))
            self.assertEqual(y1.status['loaded'].sum(), 0)

            # from static_frame import IndexAutoFactory
            # y2 = Yarn.from_concat((y1, y1), retain_labels=True, index=IndexAutoFactory)

    #---------------------------------------------------------------------------
    def test_yarn_reversed_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False)
        self.assertEqual(tuple(reversed(y1)), ('f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1'))

        # import ipdb; ipdb.set_trace()

    #---------------------------------------------------------------------------
    def test_yarn_rename_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(y1.name, 'foo')
        y2 = y1.rename('bar')
        self.assertEqual(y2.name, 'bar')

    #---------------------------------------------------------------------------
    def test_yarn_loc_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(y1.loc['f4'].shape, (4, 4))
        self.assertEqual(y1.loc['f4':].shape, (4,))
        self.assertEqual(y1.loc[['f2', 'f7']].shape, (2,))
        self.assertEqual(y1.loc[y1.index.via_str.startswith('f3')].shape, (1,))

    #---------------------------------------------------------------------------
    def test_yarn_iloc_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(y1.iloc[3].shape, (4, 4))
        self.assertEqual(y1.iloc[3:].shape, (4,))
        self.assertEqual(y1.iloc[[1, 6]].shape, (2,))
        self.assertEqual(y1.iloc[y1.index.via_str.startswith('f3')].shape, (1,))


    #---------------------------------------------------------------------------
    def test_yarn_keys_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(tuple(y1.keys()), ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7'))


    #---------------------------------------------------------------------------
    def test_yarn_iter_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(next(iter(y1)), 'f1')


    #---------------------------------------------------------------------------
    def test_yarn_contains_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertTrue('f6' in y1)


    #---------------------------------------------------------------------------
    def test_yarn_get_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertTrue(y1.get('f2').equals(f2))
        self.assertEqual(y1.get('f99'), None)


    # TODO: equals


    #---------------------------------------------------------------------------
    def test_yarn_head_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(y1.head(2).shape, (2,))
        self.assertEqual(tuple(y1.head(2).keys()), ('f1', 'f2'))


    #---------------------------------------------------------------------------
    def test_yarn_tail_a(self):
        f1 = ff.parse('s(4,4)|v(int,float)').rename('f1')
        f2 = ff.parse('s(4,4)|v(str)').rename('f2')
        f3 = ff.parse('s(4,4)|v(bool)').rename('f3')
        b1 = Bus.from_frames((f1, f2, f3), name='a')

        f4 = ff.parse('s(4,4)|v(int,float)').rename('f4')
        f5 = ff.parse('s(4,4)|v(str)').rename('f5')
        b2 = Bus.from_frames((f4, f5), name='b')

        f6 = ff.parse('s(2,4)|v(int,float)').rename('f6')
        f7 = ff.parse('s(4,2)|v(str)').rename('f7')
        b3 = Bus.from_frames((f6, f7), name='c')

        y1 = Yarn.from_buses((b1, b2, b3), retain_labels=False, name='foo')
        self.assertEqual(y1.tail(2).shape, (2,))
        self.assertEqual(tuple(y1.tail(2).keys()), ('f6', 'f7'))

    #---------------------------------------------------------------------------
    def test_yarn_items_a(self) -> None:
        f1 = ff.parse('s(4,2)').rename('f1')
        f2 = ff.parse('s(4,5)').rename('f2')
        f3 = ff.parse('s(2,2)').rename('f3')
        f4 = ff.parse('s(2,8)').rename('f4')
        f5 = ff.parse('s(4,4)').rename('f5')
        f6 = ff.parse('s(6,4)').rename('f6')

        b1 = Bus.from_frames((f1, f2, f3))
        b2 = Bus.from_frames((f4, f5, f6))

        with temp_file('.zip') as fp1, temp_file('.zip') as fp2:
            b1.to_zip_pickle(fp1)
            b2.to_zip_pickle(fp2)

            bus_a = Bus.from_zip_pickle(fp1, max_persist=1).rename('a')
            bus_b = Bus.from_zip_pickle(fp2, max_persist=1).rename('b')

            y1 = Yarn.from_buses((bus_a, bus_b), retain_labels=False)

            labels = []
            for label, frame in y1.items():
                self.assertTrue(frame.__class__ is Frame)
                labels.append(label)

            self.assertEqual(labels, list(y1.index))
            self.assertEqual(y1.status['loaded'].sum(), 2)
            self.assertEqual(y1.status.loc[y1.status['loaded']].index.values.tolist(),
                ['f3', 'f6'])


if __name__ == '__main__':
    unittest.main()
