import numpy as np
from plyfile import PlyData
from base_utils import file_utils


def load_xyz(file_path):
    data = np.loadtxt(file_path).astype('float32')
    nan_lines = np.isnan(data).any(axis=1)
    num_nan_lines = np.sum(nan_lines)
    if num_nan_lines > 0:
        data = data[~nan_lines]  # filter rows with nan values
        print('Ignored {} points containing NaN coordinates in point cloud {}'.format(num_nan_lines, file_path))
    return data

def load_ply(file_path):
    plydata = PlyData.read(file_path)
    assert plydata.elements
    data = (np.vstack((plydata['vertex']['x'], plydata['vertex']['y'], plydata['vertex']['z']))).T
    return data

def write_xyz(file_path, points: np.ndarray, normals=None, colors=None):
    """
    Write point cloud file.
    :param file_path:
    :param points:
    :param normals:
    :param colors:
    :return: None
    """

    file_utils.make_dir_for_file(file_path)

    if points.shape == (3,):
        points = np.expand_dims(points, axis=0)

    if points.shape[0] == 3 and points.shape[1] != 3:
        points = points.transpose([1, 0])

    if colors is not None and colors.shape[0] == 3 and colors.shape[1] != 3:
        colors = colors.transpose([1, 0])

    if normals is not None and normals.shape[0] == 3 and normals.shape[1] != 3:
        normals = normals.transpose([1, 0])

    with open(file_path, 'w') as fp:

        # convert 2d points to 3d
        if points.shape[1] == 2:
            vertices_2p5d = np.zeros((points.shape[0], 3))
            vertices_2p5d[:, :2] = points
            vertices_2p5d[:, 2] = 0.0
            points = vertices_2p5d

        # write points
        # meshlab doesn't like colors, only using normals. try cloud compare instead.
        for vi, v in enumerate(points):
            line_vertex = str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + " "
            if normals is not None:
                line_vertex += str(normals[vi][0]) + " " + str(normals[vi][1]) + " " + str(normals[vi][2]) + " "
            if colors is not None:
                line_vertex += str(colors[vi][0]) + " " + str(colors[vi][1]) + " " + str(colors[vi][2]) + " "
            fp.write(line_vertex + "\n")


def load_pcd(file_in):
    # PCD: http://pointclouds.org/documentation/tutorials/pcd_file_format.php
    # PCD RGB: http://docs.pointclouds.org/trunk/structpcl_1_1_r_g_b.html#a4ad91ab9726a3580e6dfc734ab77cd18

    def read_header(lines_header):
        header_info = dict()

        def add_line_to_header_dict(header_dict, line, expected_field):
            line_parts = line.split(sep=' ')
            assert (line_parts[0] == expected_field), \
                ('Warning: "' + expected_field + '" expected but not found in pcd header!')
            header_dict[expected_field] = (' '.join(line_parts[1:])).replace('\n', '')

        add_line_to_header_dict(header_info, lines_header[0], '#')
        add_line_to_header_dict(header_info, lines_header[1], 'VERSION')
        add_line_to_header_dict(header_info, lines_header[2], 'FIELDS')
        add_line_to_header_dict(header_info, lines_header[3], 'SIZE')
        add_line_to_header_dict(header_info, lines_header[4], 'TYPE')
        add_line_to_header_dict(header_info, lines_header[5], 'COUNT')
        add_line_to_header_dict(header_info, lines_header[6], 'WIDTH')
        add_line_to_header_dict(header_info, lines_header[7], 'HEIGHT')
        add_line_to_header_dict(header_info, lines_header[8], 'VIEWPOINT')
        add_line_to_header_dict(header_info, lines_header[9], 'POINTS')
        add_line_to_header_dict(header_info, lines_header[10], 'DATA')

        # TODO: lift limitations
        assert header_info['VERSION'] == '0.7'
        assert header_info['FIELDS'] == 'x y z rgb label'
        assert header_info['SIZE'] == '4 4 4 4 4'
        assert header_info['TYPE'] == 'F F F F U'
        assert header_info['COUNT'] == '1 1 1 1 1'
        # assert header_info['HEIGHT'] == '1'
        assert header_info['DATA'] == 'ascii'
        # assert header_info['WIDTH'] == header_info['POINTS']

        return header_info

    f = open(file_in, "r")
    f_lines = f.readlines()
    f_lines_header = f_lines[:11]
    f_lines_points = f_lines[11:]
    header_info = read_header(f_lines_header)
    header_info['_file_'] = file_in

    num_points = int(header_info['POINTS'])
    point_data_list_str_ = [l.split(sep=' ')[:3] for l in f_lines_points]
    point_data_list = [[float(l[0]), float(l[1]), float(l[2])] for l in point_data_list_str_]

    # filter nan points that appear through the blensor kinect sensor
    point_data_list = [p for p in point_data_list if
                       (not np.isnan(p[0]) and not np.isnan(p[1]) and not np.isnan(p[2]))]

    point_data = np.array(point_data_list)

    f.close()

    return point_data, header_info