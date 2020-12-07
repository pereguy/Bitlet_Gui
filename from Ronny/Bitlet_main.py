"""
1-Aug-2020
This code was written by Ziv Ronen to help plotting Bitlet paper graphs.
This is an ad hoc code for displaying specific requested graphs
"""

import math
import re
import enum
import numbers
import itertools
import argparse
import collections
import typing

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.text as text

import numpy as np
import pandas as pd
import seaborn as sns
import scipy.interpolate

import PySimpleGUI as sg

BIG_NUMBER = 2132039


class BoundaryFit(enum.Enum):
    NONE = False
    MIN_FIT = 1
    MAX_FIT = 2


class LineInfo(typing.NamedTuple):
    label_location: typing.Tuple[float, float]
    line_locations: typing.Sequence[typing.Tuple[float, float]]


def floats_or_axis(str_value):
    str_value = str_value.lower()
    if str_value == 'x' or str_value == 'y':
        return str_value

    return [float(float_str) for float_str in str_value.split(',')]


class Caller:
    def __init__(self, function, parameters_mapping):
        self._function = function
        self._parameters_mapping = parameters_mapping

    def get_const_arguments(self):
        return {
            parameter: self._parameters_mapping[parameter]
            for parameter in self._function.__code__.co_varnames
            if isinstance(self._parameters_mapping[parameter], numbers.Number)
        }

    def get_all_arguments(self):
        return {
            parameter: self._parameters_mapping[parameter]
            for parameter in self._function.__code__.co_varnames
        }

    def __call__(self, **kwargs):
        arguments_mapping = {
            parameter: (value if value not in kwargs else kwargs[value])
            for parameter, value in self.get_all_arguments().items()
        }
        return self._function(**arguments_mapping)

    def build(self, value_function):
        if value_function is None:
            return None
        return type(self)(build_function(value_function), self.get_all_arguments())

    def get_label(self, keyword):
        for key, value in self._parameters_mapping.items():
            if value == keyword:
                return key

        raise KeyError('keyword is not mapped')


class LinesCalculator:

    @staticmethod
    def _get_forced_fit(mapping, x_key, y_key, line_value, sensitivity):
        value = mapping[x_key][y_key]
        if abs(value - line_value) / (max(abs(value), abs(line_value)) + 1) <= sensitivity:
            # The value is actually correct
            return BoundaryFit.NONE

        if y_key == min(mapping[x_key].keys()):
            return BoundaryFit.MIN_FIT

        if y_key == max(mapping[x_key].keys()):
            return BoundaryFit.MAX_FIT

        return BoundaryFit.NONE

    @classmethod
    def _find_closest_to_line(cls, mapping, line_value, base_value_function=None, is_vertical=False):
        def distance_function(x, y, base_z):
            function_value = base_z if base_value_function is None else float(base_value_function(x=x, y=y))
            return abs(function_value - float(line_value))

        if not is_vertical:
            actual_mapping = mapping
        else:
            all_y_values = set(itertools.chain.from_iterable(
                [y_key for y_key in y_values.keys()] for y_values in mapping.values()
            ))
            actual_mapping = {
                y_key: {x_key: mapping[x_key][y_key] for x_key, y_values in mapping.items() if y_key in y_values}
                for y_key in all_y_values
            }

        line_locations = []
        if not is_vertical:
            for x_key, y_values in actual_mapping.items():
                y_key, _ = min(y_values.items(), key=lambda y: distance_function(x_key, y[0], y[1]))
                line_locations.append((x_key, y_key))

        else:
            for y_key, x_values in actual_mapping.items():
                x_key, _ = min(x_values.items(), key=lambda x: distance_function(x[0], y_key, x[1]))
                line_locations.append((x_key, y_key))

        return line_locations

    @classmethod
    def _fix_line(cls, line_locations, line_value, mapping, sensitivity):
        fixed_line_locations = []
        line_location_ex = zip(line_locations, itertools.chain(line_locations[1:], [line_locations[-1]]))
        for (x_key, y_key), (_, next_y_key) in line_location_ex:
            if y_key == next_y_key:
                forced_fit_type = cls._get_forced_fit(mapping, x_key, y_key, line_value, sensitivity)
                if forced_fit_type is not BoundaryFit.NONE:
                    if len(fixed_line_locations) != 0 and not isinstance(fixed_line_locations[-1][1], BoundaryFit):
                        fixed_line_locations.append((x_key, forced_fit_type))

                    continue

            fixed_line_locations.append((x_key, y_key))

        return fixed_line_locations

    @classmethod
    def _find_label_location(cls, fixed_locations, is_vertical=False):
        if is_vertical:
            line_drawn_ys = set(y for _, y in fixed_locations)
            label_y_value = list(sorted(line_drawn_ys))[int(0.54 * len(line_drawn_ys))]
            label_x_value = next(x for x, y in fixed_locations if y == label_y_value)

        else:
            line_drawn_xs = set(x for x, _ in fixed_locations)
            label_x_value = list(sorted(line_drawn_xs))[int(0.5 * len(line_drawn_xs))]
            label_y_value = next(y for x, y in fixed_locations if x == label_x_value)

        return label_x_value, label_y_value

    @classmethod
    def run(cls, mapping, line_value, sensitivity=0.001, value_function=None, is_vertical=False):
        line_locations = cls._find_closest_to_line(mapping, line_value, value_function, is_vertical)
        fixed_locations = cls._fix_line(line_locations, line_value, mapping, sensitivity)
        if len(fixed_locations) < 2:
            return None

        label_x, label_y = cls._find_label_location(fixed_locations, is_vertical)
        return LineInfo((label_x, label_y), fixed_locations)


def fix_axis(axis, unscaled_values, scaled_values, set_ticks, set_labels):
    relevant_values = [
        scaled for value, scaled in zip(unscaled_values, scaled_values)
        if value.is_integer()
    ]

    min_tick, max_tick = axis.get_ticklocs()[0], axis.get_ticklocs()[-1]
    delta_tick = (max_tick - min_tick) / (len(relevant_values) - 1)
    set_ticks([min_tick + i * delta_tick for i in range(len(relevant_values))])
    set_labels([text.Text(0, 0, format_float(scaled)) for scaled in relevant_values])


def format_float(value):
    base_value = round(float(value), 1)
    return str(int(base_value) if base_value.is_integer() else base_value)


class LocationFixer:
    def __init__(self, ax, x_mapping, y_mapping):
        x_labels_position = ax.xaxis.get_ticklocs()
        self._x_tick_min = min(x_labels_position)
        self._x_axis_size = max(x_labels_position) - self._x_tick_min

        y_labels_position = ax.yaxis.get_ticklocs()
        self._y_tick_min = min(y_labels_position)
        self._y_tick_max = max(y_labels_position)
        self._y_axis_size = self._y_tick_max - self._y_tick_min

        self._min_x_value = min(x_mapping.keys())
        self._x_value_range = max(x_mapping.keys()) - self._min_x_value
        self._min_y_value = min(y_mapping.keys())
        self._y_value_range = max(y_mapping.keys()) - self._min_y_value

        self._x_reverse_mapping = {value: key for key, value in x_mapping.items()}
        self._y_reverse_mapping = {value: key for key, value in y_mapping.items()}

    def get_location(self, scaled_x, scaled_y):
        x_location = self._x_tick_min + self.get_x(self._x_reverse_mapping[scaled_x] - self._min_x_value)

        if scaled_y is BoundaryFit.MIN_FIT:
            y_location = 0
        elif scaled_y is BoundaryFit.MAX_FIT:
            y_location = self._y_tick_max
        else:
            y_location = self._y_tick_min + self.get_y(self._y_reverse_mapping[scaled_y] - self._min_y_value)

        return x_location, self._y_tick_max - y_location

    def get_x(self, unscaled_x):
        normalized_x_location = unscaled_x / self._x_value_range
        return normalized_x_location * self._x_axis_size

    def get_y(self, unscaled_y):
        normalized_y_location = unscaled_y / self._y_value_range
        return normalized_y_location * self._y_axis_size


def iter_targets(caller, target_description):
    target = caller.build(target_description)()
    if isinstance(target, numbers.Number):
        return [(format_float(target), target)]

    if isinstance(target, typing.Mapping):
        return target.items()

    if isinstance(target, typing.Iterable):
        return ((format_float(val), val) for val in target)

    raise ValueError('target description can not be used for lines [got: {}]'.format(target_description))


def add_line(data, fixer, line_conf, target, value_function, label_text, is_vertical):
    line_info = LinesCalculator.run(data, target, value_function=value_function, is_vertical=is_vertical)
    if line_info is None:
        return

    line_x, line_y = list(zip(*(fixer.get_location(x, y) for x, y in line_info.line_locations)))
    if is_vertical:
        plt.plot(line_x, line_y, **line_conf)
    else:
        x_new = np.linspace(min(line_x), max(line_x), 300)
        smoothed_y = scipy.interpolate.make_interp_spline(line_x, line_y)(x_new)
        plt.plot(line_x, line_y, **line_conf)

    label_position_x, label_position_y = fixer.get_location(*line_info.label_location)
    plt.text(
        # TODO: the added values might required changes between the graphs for maximum readability
        label_position_x + fixer.get_x(0.01),
        label_position_y + fixer.get_y(-0.05),
        label_text,
        color=line_conf.get('color', 'black'),
    )


def add_lines(ax, caller, data, lines, x_mapping, y_mapping):
    fixer = LocationFixer(ax, x_mapping, y_mapping)
    for line_conf, value_function_description, is_vertical, targets in lines:
        value_function = caller.build(value_function_description)
        for target_description in targets:
            for label_text, target in iter_targets(caller, target_description):
                add_line(data, fixer, line_conf, target, value_function, label_text, is_vertical)


def plot(x_values, y_values, caller, lines, scale_x=2, scale_y=2):
    x_mapping = {x: scale_x ** x for x in x_values}
    y_mapping = {y: scale_y ** y for y in reversed(y_values)}

    data = collections.OrderedDict(
        (x, collections.OrderedDict((y, caller(x=x, y=y)) for y in y_mapping.values()))
        for x in x_mapping.values()
    )

    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(12, 7))

    title_consts_str = ', '.join(
        '{}={}'.format(key, format_float(value))
        for key, value in caller.get_const_arguments().items()
    )

    windows_consts_str = '__'.join(
        '{}_{}'.format(key.lower(), format_float(value))
        for key, value in caller.get_const_arguments().items()
    )

    label_x = caller.get_label('x')
    label_y = caller.get_label('y')
    fig.canvas.set_window_title('z__{}_x__{}_y__{}'.format(label_x, label_y, windows_consts_str))
    plt.title('{}'.format(title_consts_str), fontsize=18)

    norm = colors.LogNorm()
    sns.heatmap(df, cmap=plt.get_cmap('RdYlGn'), linewidths=0, ax=ax, norm=norm)

    fix_axis(ax.xaxis, x_mapping.keys(), x_mapping.values(), ax.set_xticks, ax.set_xticklabels)
    fix_axis(ax.yaxis, y_mapping.keys(), y_mapping.values(), ax.set_yticks, ax.set_yticklabels)

    plt.xlabel(label_x)
    plt.ylabel(label_y)
    # Add lines
    add_lines(ax, caller, data, lines, x_mapping, y_mapping)


def build_function(function_expression):
    variables_pattern = r'<([A-Za-z]\w*)>'
    parameters_names = ', '.join(set(re.findall(variables_pattern, function_expression)))
    function_expression_fixed = re.sub(variables_pattern, r'\1', function_expression)
    lambda_expression = 'lambda {}: {}'.format(parameters_names, function_expression_fixed)
    return eval(lambda_expression)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('function', help='The function to parse')

    parser.add_argument('x_max', type=int, help='max x value')
    parser.add_argument('y_max', type=int, help='max y value')
    parser.add_argument('--x-min', type=int, default=0, help='min x value')
    parser.add_argument('--y-min', type=int, default=0, help='min y value')
    parser.add_argument(
        '--lines', nargs='+', action='append', type=str, default=[],
        help='Lines, each should be given as: --lines <conf> <y values>'
    )
    parser.add_argument(
        '--function-lines', nargs='+', action='append', type=str, default=[],
        help='Lines, each should be given as: --function-lines <function> <conf> <y values>'
    )
    parser.add_argument(
        '--function-vlines', nargs='+', action='append', type=str, default=[],
        help='Lines (vertical), each should be given as: --function-vlines <function> <conf> <y values>'
    )
    parser.add_argument('--samples', nargs=2, type=int, default=(20, 20),
                        help='samples between each exponent: <X> <Y>')

    z_function_args = parser.parse_known_args(argv)
    # Need to fix help values if function is not given, but I don't really care.
    z_function = build_function(z_function_args[0].function)

    for parameter in z_function.__code__.co_varnames:
        parser.add_argument(
            '--{}'.format(parameter.lower()),
            required=True,
            dest=parameter,
            type=floats_or_axis,
            help='value for {}'.format(parameter)
        )

    args = parser.parse_args(argv)
    func_arguments = [getattr(args, parameter) for parameter in z_function.__code__.co_varnames]
    if func_arguments.count('x') != 1 or func_arguments.count('y') != 1:
        raise ValueError('Precisely one argument should be X and one should be Y')

    args.all_lines = []
    for line_from_type in args.lines:
        line_from_type.insert(0, 'None')

    for is_vertical, lines in [(False, itertools.chain(args.function_lines, args.lines)), (True, args.function_vlines)]:
        for line_from_type in lines:
            line_conf = dict(type_arguments.split('=') for type_arguments in line_from_type if '=' in type_arguments)
            line_values = (line for line in line_from_type if '=' not in line)
            line_function = next(line_values)
            if line_function == 'None':
                line_function = None
            args.all_lines.append((line_conf, line_function, is_vertical, list(line_values)))

    args.function = z_function
    return args


def main(argv=None):
    args = parse_arguments(argv)

    consts_pair = []
    variables = []
    for param in args.function.__code__.co_varnames:
        const_values = getattr(args, param)
        if const_values not in ('x', 'y'):
            consts_pair.append([(param, value) for value in const_values])
        else:
            variables.append((param, const_values))

    for consts_parameters in itertools.product(*consts_pair):
        plot(
            np.linspace(args.x_min, args.x_max, num=(args.x_max - args.x_min) * args.samples[0] + 1),
            np.linspace(args.y_min, args.y_max, num=(args.y_max - args.y_min) * args.samples[1] + 1),
            Caller(args.function, dict(itertools.chain(variables, consts_parameters))),
            lines=args.all_lines
        )


def run():
    PIM_ENERGY_BITS = '0.1 * (10 ** -12)'
    CPU_ENERGY_BITS = '15 * (10 ** -12)'
    TRUE_BW = '(<BW> * (10 ** 9))'
    TRUE_CT = '(<CT> * (10 ** -9))'
    P_PIM = f'{PIM_ENERGY_BITS} * ((<MATs> * <ROWs>) / {TRUE_CT})'
    P_CPU = f'{CPU_ENERGY_BITS} * {TRUE_BW}'

    BASE_TP = f'1 / ((<DIO> / {TRUE_BW}) + ((<CC> * {TRUE_CT}) / (<ROWs> * <MATs>)))'

    TP = f'(10 ** -9) * {BASE_TP}'
    LINE_FUNCTION = f'({P_CPU} * (<DIO> / {TRUE_BW}) + ({P_PIM} * (<CC> * {TRUE_CT}) / (<ROWs> * <MATs>))) * {BASE_TP}'

    values = [
        TP,
        '14', '10',
        '--cc', 'x', '--dio', 'y',
        '--bw', '1000', '--rows', '1024', '--mats', '1024', '--ct', '10',
        '--samples', '10', '10',
        '--x-min', '-1', '--y-min', '-3',
        '--lines', 'linewidth=0.5', 'color=blue', 'linestyle=--', '[(1024 / i) for i in [48, 96]]',
        '--function-lines', 'color=red', LINE_FUNCTION, '10.7', '11.0', '12.0', '13.0', '14.0', '{" ": 14.9}',
        '--lines', 'linewidth=0.5', 'color=black', '[2 ** line for line in range(1, 20)]',
        '--function-vlines', 'linewidth=0.3', 'color=blue', '<CC>', '{" " * i: j for i, j in enumerate([32, 144, 1600, 6400])}',
        '--function-lines', 'linewidth=0.3', 'color=blue', '<DIO>', '{" " * i: j for i, j in enumerate([16, 32, 48, 96])}'

    ]
    main(values)

    values1 = [
        TP,
        '15', '15',
        '--cc', '6400', '--dio', '16',
        '--bw', 'y', '--rows', '1024', '--mats', 'x', '--ct', '10',
        '--samples', '30', '30',
        '--x-min', '10', '--y-min', '9',
        '--lines', 'linewidth=0.5', 'color=black', '[2 ** line for line in range(1, 20)]',

        '--function-lines', 'color=red', LINE_FUNCTION, '40.0', '160.0',
        '--function-lines', 'color=blue', '<BW>', '{16 * (2 ** i): 768 * (2 ** i) for i in range(6)}',
        '--function-lines', 'color=magenta', '<BW>', '{40: 2667}', '{160: 10667}',
        '--function-vlines', 'linewidth=0.5', 'color=blue', '<MATs>', '{16 * (2 ** i): 1000 * (2 ** i) for i in range(6)}',
        '--function-vlines', 'linewidth=0.5', 'color=pink', '<MATs>', '{" " * i: 3906 * (2 ** i) for i in [0, 2]}',
    ]
    main(values1)
    plt.show()


if __name__ == '__main__':
    run()