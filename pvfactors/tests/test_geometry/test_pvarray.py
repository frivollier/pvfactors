import os
import numpy as np
from pvfactors.geometry import OrderedPVArray, PVGround, PVSurface
from pvfactors.geometry.utils import contains
from pvfactors.config import MAX_X_GROUND, MIN_X_GROUND
from pvfactors.tests.test_geometry.test_data import \
    vm_flat_orderedpvarray, vm_right_orderedpvarray


def test_ordered_pvarray_from_dict(params):
    """Test that can successfully create ordered pvarray from parameters dict,
    and that the axis azimuth convention works correctly (via normal vector)
    """
    pvarray = OrderedPVArray.from_dict(params)

    # Test that ground is created successfully
    assert isinstance(pvarray.ground, PVGround)
    assert pvarray.ground.length == (MAX_X_GROUND - MIN_X_GROUND)

    # Test the front and back sides
    assert len(pvarray.pvrows) == 3
    np.testing.assert_array_equal(
        pvarray.pvrows[0].front.n_vector, -pvarray.pvrows[0].back.n_vector)
    assert pvarray.pvrows[0].front.shaded_length == 0
    assert pvarray.gcr == params['gcr']
    assert pvarray.surface_tilt == params['surface_tilt']
    assert pvarray.surface_azimuth == params['surface_azimuth']
    assert pvarray.solar_zenith == params['solar_zenith']
    assert pvarray.solar_azimuth == params['solar_azimuth']
    assert pvarray.pvrows[0].front.n_vector[0] > 0

    # Orient the array the other way
    params.update({'surface_azimuth': 270.})
    pvarray = OrderedPVArray.from_dict(params)
    assert pvarray.pvrows[0].front.n_vector[0] < 0


def test_plot_ordered_pvarray():
    """Test that ordered pv array plotting works correctly"""
    is_ci = os.environ.get('CI', False)
    if not is_ci:
        import matplotlib.pyplot as plt

        # Create base params
        params = {
            'n_pvrows': 3,
            'pvrow_height': 2.5,
            'pvrow_width': 2.,
            'surface_azimuth': 90.,  # east oriented modules / point right
            'axis_azimuth': 0.,  # axis of rotation towards North
            'surface_tilt': 20.,
            'gcr': 0.4,
            'solar_zenith': 20.,
            'solar_azimuth': 90.,  # sun located in the east
            'rho_ground': 0.2,
            'rho_front_pvrow': 0.01,
            'rho_back_pvrow': 0.03
        }

        # Plot simple ordered pv array
        ordered_pvarray = OrderedPVArray.from_dict(params)
        f, ax = plt.subplots()
        ordered_pvarray.plot(ax)
        plt.show()

        # Plot discretized ordered pv array
        params.update({'cut': {0: {'front': 5}, 1: {'back': 3}},
                       'surface_azimuth': 270.})  # point left
        ordered_pvarray = OrderedPVArray.from_dict(params)
        f, ax = plt.subplots()
        ordered_pvarray.plot(ax)
        plt.show()


def test_discretization_ordered_pvarray(discr_params):
    pvarray = OrderedPVArray.from_dict(discr_params)
    pvrows = pvarray.pvrows

    assert len(pvrows[0].front.list_segments) == 5
    assert len(pvrows[0].back.list_segments) == 1
    assert len(pvrows[1].back.list_segments) == 3


def test_ordered_pvarray_gnd_shadow_casting(params):
    """Test shadow casting on ground, no inter-row shading"""

    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params)
    ordered_pvarray.cast_shadows()
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 3
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 4
    assert ordered_pvarray.ground.shaded_length == 6.385066634855475
    assert ordered_pvarray.illum_side == 'front'


def test_ordered_pvarray_gnd_pvrow_shadow_casting_right(params_direct_shading):

    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params_direct_shading)
    ordered_pvarray.cast_shadows()
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 1
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 2
    assert ordered_pvarray.ground.length == MAX_X_GROUND - MIN_X_GROUND

    assert ordered_pvarray.illum_side == 'front'
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].back.shaded_length, 0.)


def test_ordered_pvarray_gnd_pvrow_shadow_casting_left(params_direct_shading):

    params_direct_shading.update({'solar_azimuth': 270,
                                  'surface_azimuth': 270})
    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params_direct_shading)
    ordered_pvarray.cast_shadows()
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 1
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 2
    assert ordered_pvarray.ground.length == MAX_X_GROUND - MIN_X_GROUND

    assert ordered_pvarray.illum_side == 'front'
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].back.shaded_length, 0.)


def test_ordered_pvarray_gnd_pvrow_shadow_casting_back(params_direct_shading):

    params_direct_shading.update({'solar_azimuth': 270,
                                  'surface_tilt': 120})

    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params_direct_shading)
    ordered_pvarray.cast_shadows()
    assert ordered_pvarray.illum_side == 'back'
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 1
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 2
    assert ordered_pvarray.ground.length == MAX_X_GROUND - MIN_X_GROUND

    # Shading length should be identical as in previous test for front surface,
    # but now with back surface
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].back.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].back.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].front.shaded_length, 0.)


def test_ordered_pvarray_gnd_pvrow_shadow_casting_right_n_seg(
        params_direct_shading):

    params_direct_shading.update({'cut': {1: {'front': 7}}})
    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params_direct_shading)
    ordered_pvarray.cast_shadows()
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 1
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 2
    assert ordered_pvarray.ground.length == MAX_X_GROUND - MIN_X_GROUND

    assert ordered_pvarray.illum_side == 'front'
    # Test pvrow sides: should be the same as without segments
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].front.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].back.shaded_length, 0.)

    # Test individual segments
    center_row = ordered_pvarray.pvrows[1]
    list_pvsegments = center_row.front.list_segments
    fully_shaded_segment = list_pvsegments[-1]
    partial_shaded_segment = list_pvsegments[-2]
    assert fully_shaded_segment.illum_collection.is_empty
    np.testing.assert_almost_equal(
        fully_shaded_segment.shaded_collection.length,
        list_pvsegments[0].length)
    assert partial_shaded_segment.shaded_collection.length > 0
    assert partial_shaded_segment.illum_collection.length > 0
    sum_lengths = (partial_shaded_segment.illum_collection.length +
                   partial_shaded_segment.shaded_collection.length)
    np.testing.assert_almost_equal(sum_lengths, list_pvsegments[0].length)


def test_ordered_pvarray_gnd_pvrow_shadow_casting_back_n_seg(
        params_direct_shading):

    params_direct_shading.update({'cut': {1: {'back': 7}},
                                  'solar_azimuth': 270,
                                  'surface_tilt': 120})
    # Test front shading on right
    ordered_pvarray = OrderedPVArray.from_dict(params_direct_shading)
    ordered_pvarray.cast_shadows()
    # Check shadow casting on ground
    assert len(ordered_pvarray.ground.list_segments[0]
               .shaded_collection.list_surfaces) == 1
    assert len(ordered_pvarray.ground.list_segments[0]
               .illum_collection.list_surfaces) == 2
    assert ordered_pvarray.ground.length == MAX_X_GROUND - MIN_X_GROUND

    assert ordered_pvarray.illum_side == 'back'
    # Shading length should be identical as in previous test for front surface,
    # but now with back surface
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].back.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].back.shaded_length, 0.33333333333333254)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].back.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[2].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[1].front.shaded_length, 0.)
    np.testing.assert_almost_equal(
        ordered_pvarray.pvrows[0].front.shaded_length, 0.)

    # Test individual segments
    center_row = ordered_pvarray.pvrows[1]
    list_pvsegments = center_row.back.list_segments
    fully_shaded_segment = list_pvsegments[-1]
    partial_shaded_segment = list_pvsegments[-2]
    assert fully_shaded_segment.illum_collection.is_empty
    np.testing.assert_almost_equal(
        fully_shaded_segment.shaded_collection.length,
        list_pvsegments[0].length)
    assert partial_shaded_segment.shaded_collection.length > 0
    assert partial_shaded_segment.illum_collection.length > 0
    sum_lengths = (partial_shaded_segment.illum_collection.length +
                   partial_shaded_segment.shaded_collection.length)
    np.testing.assert_almost_equal(sum_lengths, list_pvsegments[0].length)


def test_ordered_pvarray_cuts_for_pvrow_view(ordered_pvarray):
    """Test that pvarray ground is cut correctly"""

    ordered_pvarray.cast_shadows()
    n_surfaces_0 = ordered_pvarray.ground.n_surfaces
    len_0 = ordered_pvarray.ground.length
    ordered_pvarray.cuts_for_pvrow_view()
    n_surfaces_1 = ordered_pvarray.ground.n_surfaces
    len_1 = ordered_pvarray.ground.length

    assert n_surfaces_1 == n_surfaces_0 + 3
    assert len_1 == len_0


def test_ordered_pvarray_list_surfaces(ordered_pvarray):
    """Check that getting a correct list of surfaces"""
    ordered_pvarray.cast_shadows()
    n_surfaces = ordered_pvarray.n_surfaces
    list_surfaces = ordered_pvarray.all_surfaces

    assert isinstance(list_surfaces, list)
    assert len(list_surfaces) == n_surfaces
    assert isinstance(list_surfaces[0], PVSurface)


def test_build_surface_registry(ordered_pvarray):
    """Test that building surface registry correctly"""

    ordered_pvarray.cast_shadows()
    reg = ordered_pvarray.surface_registry

    assert reg.shape[0] == ordered_pvarray.n_surfaces
    assert reg.shape[1] == len(ordered_pvarray.registry_cols)


def test_get_all_surface_indices(ordered_pvarray):

    # Complete array
    ordered_pvarray.cast_shadows()
    ordered_pvarray.cuts_for_pvrow_view()

    # Check surface indices before indexing
    surf_indices = ordered_pvarray.surface_indices
    assert surf_indices == [None] * ordered_pvarray.n_surfaces

    # Check surface indices after indexing
    ordered_pvarray.index_all_surfaces()
    surf_indices = ordered_pvarray.surface_indices
    np.testing.assert_array_equal(surf_indices,
                                  range(ordered_pvarray.n_surfaces))


def test_view_matrix_flat(params):

    # Make flat
    params.update({'surface_tilt': 0})

    # Create pvarray
    pvarray = OrderedPVArray.from_dict(params)

    # Create shadows and pvrow cuts
    pvarray.cast_shadows()
    pvarray.cuts_for_pvrow_view()

    # Build view matrix
    vm = pvarray.view_matrix

    assert vm.shape[0] == pvarray.n_surfaces + 1
    np.testing.assert_array_equal(vm, vm_flat_orderedpvarray)


def test_view_matrix(params):

    params.update({'surface_azimuth': 270})

    # Create pvarray
    pvarray = OrderedPVArray.from_dict(params)

    # Create shadows and pvrow cuts
    pvarray.cast_shadows()
    pvarray.cuts_for_pvrow_view()

    # Build view matrix and obstruction matrix
    vm, om = pvarray._build_view_matrix()

    assert vm.shape[0] == pvarray.n_surfaces + 1
    np.testing.assert_array_equal(vm, vm_right_orderedpvarray)
    # The view matrix mask should be symmetric
    mask_vm = np.where(vm != 0, 1, 0)
    np.testing.assert_array_equal(mask_vm[:-1, :-1], mask_vm.T[:-1, :-1])
    # Removing sky row and column because didn't fill the last row

    # The obstruction matrix should be symmetric
    np.testing.assert_array_equal(om, om.T)
    # TODO: test values against saved array


def test_surface_params(params):

    surface_params = ['qinc']
    pvarray = OrderedPVArray.from_dict(params, surface_params=surface_params)
    pvarray.cast_shadows()
    pvarray.cuts_for_pvrow_view()

    # Set all surfaces parameters to 1
    pvarray.update_params({'qinc': 1})

    # Check that all surfaces of the correct surface params
    all_surfaces = pvarray.all_surfaces
    for surf in all_surfaces:
        assert surf.surface_params == surface_params
        assert surf.get_param('qinc') == 1

    # Check weighted values
    np.testing.assert_almost_equal(
        pvarray.ground.get_param_weighted('qinc'), 1)
    np.testing.assert_almost_equal(
        pvarray.ground.get_param_ww('qinc'),
        pvarray.ground.length)
    for pvrow in pvarray.pvrows:
        # Front
        np.testing.assert_almost_equal(
            pvrow.front.get_param_weighted('qinc'), 1)
        np.testing.assert_almost_equal(
            pvrow.front.get_param_ww('qinc'), pvrow.front.length)
        # Back
        np.testing.assert_almost_equal(
            pvrow.back.get_param_weighted('qinc'), 1)
        np.testing.assert_almost_equal(
            pvrow.back.get_param_ww('qinc'), pvrow.back.length)


def test_orderedpvarray_neighbors(params):
    """Check that pvrow neighbors are determined correctly"""

    pvarray_right = OrderedPVArray.from_dict(params)
    params.update({'surface_azimuth': 270})
    pvarray_left = OrderedPVArray.from_dict(params)

    # Check
    l1 = [None, 0, 1]
    l2 = [1, 2, None]
    np.testing.assert_array_equal(pvarray_right.front_neighbors, l2)
    np.testing.assert_array_equal(pvarray_right.back_neighbors, l1)
    np.testing.assert_array_equal(pvarray_left.front_neighbors, l1)
    np.testing.assert_array_equal(pvarray_left.back_neighbors, l2)


def test_orderedpvarray_almost_flat():
    """Making sure that things are correct when the pvarray is almost flat
    and the sun is very low, which means that the shadows on the ground, and
    the edge points will be outside of ground range (since not infinite)"""

    params = {
        'n_pvrows': 3,
        'pvrow_height': 2.5,
        'pvrow_width': 2.,
        'surface_azimuth': 90.,  # east oriented modules
        'axis_azimuth': 0.,      # axis of rotation towards North
        'surface_tilt': 0.01,    # almost flat
        'gcr': 0.4,
        'solar_zenith': 89.9,    # sun super low
        'solar_azimuth': 90.,    # sun located in the east
    }

    pvarray = OrderedPVArray.from_dict(params)
    pvarray.cast_shadows()
    pvarray.cuts_for_pvrow_view()
    view_matrix = pvarray.view_matrix

    ground_seg = pvarray.ground.list_segments[0]
    # there should be no visible shadow on the ground
    assert len(ground_seg.shaded_collection.list_surfaces) == 0
    # all of the edge points should be outside of range of ground geometry
    for edge_pt in pvarray.edge_points:
        assert not contains(pvarray.ground.original_linestring, edge_pt)

    # Check values of view matrix mask, to make sure that front does not
    # see the ground
    vm_mask = np.where(view_matrix > 0, 1, 0)
    expected_vm_mask = [
        [0, 0, 1, 0, 1, 0, 1, 1],  # ground
        [0, 0, 0, 0, 1, 0, 0, 1],  # front
        [1, 0, 0, 0, 0, 0, 0, 1],  # back
        [0, 0, 0, 0, 0, 0, 1, 1],  # front
        [1, 1, 0, 0, 0, 0, 0, 1],  # back
        [0, 0, 0, 0, 0, 0, 0, 1],  # front
        [1, 0, 0, 1, 0, 0, 0, 1],  # back
        [0, 0, 0, 0, 0, 0, 0, 0]]
    np.testing.assert_array_equal(vm_mask, expected_vm_mask)


def test_time_ordered_pvarray(params):

    # params.update({'surface_tilt': 0})
    from pvfactors.viewfactors import VFCalculator

    import time
    n = 100
    list_elapsed = []
    for _ in range(n):
        tic = time.time()
        pvarray = OrderedPVArray.from_dict(params)
        pvarray.cast_shadows()  # time consuming in pvarray creation
        pvarray.cuts_for_pvrow_view()
        pvarray.index_all_surfaces()
        # sr = pvarray.surface_registry
        # vm = pvarray.view_matrix
        vm, om = pvarray._build_view_matrix()
        geom_dict = pvarray.dict_surfaces

        calculator = VFCalculator()
        # number 1 time consuming, triples run time
        vf_matrix = calculator.get_vf_matrix(geom_dict, vm, om,
                                             pvarray.pvrows)
        toc = time.time()
        list_elapsed.append(toc - tic)

    print("\nAvg time elapsed: {} s".format(np.mean(list_elapsed)))
