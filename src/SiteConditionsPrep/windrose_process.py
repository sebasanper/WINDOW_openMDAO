from openmdao.api import ExplicitComponent
from numpy import exp
import numpy as np
from time import clock



class WindrosePreprocessor(ExplicitComponent):
    def __init__(self, real_angle, artificial_angle, n_windspeedbins):
        super(WindrosePreprocessor, self).__init__()
        self.real_angle = real_angle
        self.n_directions = int(360.0 / real_angle)
        self.artificial_angle = artificial_angle
        self.n_artificials = int(360.0 / self.artificial_angle)
        self.n_windspeedbins = n_windspeedbins
        self.n_cases = int(self.n_artificials * (self.n_windspeedbins + 1))

    def setup(self):
        self.add_input('cut_in', val=4.0)
        self.add_input('cut_out', val=25.0)
        self.add_input('weibull_shapes', shape=self.n_directions)
        self.add_input('weibull_scales', shape=self.n_directions)
        self.add_input('dir_probabilities', shape=self.n_directions)
        self.add_input('wind_directions', shape=self.n_directions)

        self.add_output('cases', shape=(self.n_cases, 2))
        self.add_output('probabilities', shape=self.n_cases)

    def compute(self, inputs, outputs):
        # print clock(), "1st line compute Windrose"
        # print "WINDROSE OUTPUT"
        cut_in = inputs['cut_in']
        cut_out = inputs['cut_out']
        weibull_shapes = inputs['weibull_shapes']
        weibull_scales = inputs['weibull_scales']
        dir_probabilities = inputs['dir_probabilities']
        wind_directions = inputs['wind_directions']

        getdata = WeibullWindBins(weibull_shapes, weibull_scales, dir_probabilities, wind_directions, self.real_angle,
                                  self.artificial_angle, self.n_windspeedbins)
        getdata.cutin = cut_in
        getdata.cutout = cut_out
        wind_directions2, direction_probabilities2 = getdata.adapt_directions()
        wind_speeds2, wind_speeds_probabilities2 = getdata.speed_probabilities()

        cases = np.array([])
        probs = np.array([])

        for wdir, prob1, prob2 in zip(wind_directions2, direction_probabilities2, wind_speeds_probabilities2):
            for ws, prob3 in zip(wind_speeds2, prob2):
                cases = np.append(cases, [wdir, ws])
                probs = np.append(probs, prob1 / 100.0 * prob3 / 100.0)
        cases = cases.reshape(self.n_cases, 2)
        probs = probs.reshape(self.n_cases)
        outputs['probabilities'] = probs
        outputs['cases'] = np.array(cases)


class WeibullWindBins(object):

    def __init__(self, weibull_shapes, weibull_scales, dir_probabilities, direction, real_directions,
                 artificial_directions, n_windspeedbins):
        self.weibull_scale = weibull_scales
        self.weibull_shape = weibull_shapes
        self.direction = direction
        self.dir_probability = dir_probabilities
        self.cutin = 0.0
        self.cutout = 0.0
        self.n_directions = real_directions

        self.nbins = n_windspeedbins
        self.artificial_angle = artificial_directions
        self.real_angle = real_directions
        self.new_direction = []
        self.new_direction_probability = []
        self.new_weibull_scale = []
        self.new_weibull_shape = []
        self.new_direction2 = []
        self.new_direction_probability2 = []
        self.new_weibull_shape2 = []
        self.new_weibull_scale2 = []
        self.windspeeds = []

    def adapt_directions(self):
        self.new_direction = []
        self.new_direction_probability = []
        self.new_weibull_scale = []
        self.new_weibull_shape = []
        self.new_direction2 = []
        self.new_direction_probability2 = []
        self.new_weibull_shape2 = []
        self.new_weibull_scale2 = []
        if len(self.direction) > 1:
            for i in range(len(self.direction)):
                if self.direction[i] % self.real_angle == 0.0:
                    self.new_direction_probability.append(self.dir_probability[i])
                    self.new_direction.append(self.direction[i])
                    self.new_weibull_scale.append(self.weibull_scale[i])
                    self.new_weibull_shape.append(self.weibull_shape[i])
                else:
                    self.new_direction_probability[-1] += self.dir_probability[i]
        else:
            self.new_direction_probability.append(100.0)
            self.new_direction.append(self.direction)
            self.new_weibull_scale.append(0)
            self.new_weibull_shape.append(0)

        if len(self.new_direction) > 1:
            n = int(self.new_direction[1] - self.new_direction[0]) / int(self.artificial_angle)
        else:
            n = 1
        for i in range(len(self.new_direction)):
            for j in range(n):
                self.new_direction2.append(self.new_direction[i] + self.artificial_angle * j)
                self.new_direction_probability2.append(self.new_direction_probability[i] / n)
                self.new_weibull_scale2.append(self.new_weibull_scale[i])
                self.new_weibull_shape2.append(self.new_weibull_shape[i])

        return self.new_direction2, self.new_direction_probability2

        # print self.new_direction2
        # print self.new_direction_probability2
        # print self.dir_probability

    def cumulative_weibull(self, wind_speed, weibull_scale_dir, weibull_shape_dir):

        return 1.0 - exp(-(wind_speed / weibull_scale_dir) ** weibull_shape_dir)

    def get_wind_speeds(self):
        if self.nbins > 0:
            delta = (self.cutout - self.cutin) / self.nbins
        else:
            delta = 0
        windspeeds = []
        for i in range(self.nbins + 1):

            windspeeds.append(self.cutin + i * delta)

        return windspeeds

    def speed_probabilities(self):
        self.adapt_directions()
        speed_probabilities = []
        self.windspeeds = self.get_wind_speeds()

        for angle in self.new_direction2:
            place = self.new_direction2.index(angle)
            prob_cutout = (1.0 - self.cumulative_weibull(self.cutout, self.new_weibull_scale2[place],
                                                         self.new_weibull_shape2[place]))
            length = len(self.windspeeds)
            windspeedprobabilities = [0.0 for _ in range(length)]

            for i in range(length):

                if i == 0:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i],
                                                                         self.new_weibull_scale2[place],
                                                                         self.new_weibull_shape2[place]))

                elif i < length - 1:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i],
                                                                         self.new_weibull_scale2[place],
                                                                         self.new_weibull_shape2[place]) -
                                                 sum(windspeedprobabilities[:i]))

                elif i == length - 1:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i],
                                                                         self.new_weibull_scale2[place],
                                                                         self.new_weibull_shape2[place]) -
                                                 sum(windspeedprobabilities[:i]) + prob_cutout)

            speed_probabilities.append([item * 100.0 for item in windspeedprobabilities])

        return self.windspeeds, speed_probabilities


if __name__ == '__main__':

    getdata = WeibullWindBins([1.0, 1.0], [8.5, 8.5], [50.0, 50.0], [0.0, 180.0], 180., 1., 16)
    getdata.cutin = 4.0
    getdata.cutout = 25.0

    wind_directions2, direction_probabilities2 = getdata.adapt_directions()
    wind_speeds2, wind_speeds_probabilities2 = getdata.speed_probabilities()
    cases = []

    cases = []
    probs = []

    for wdir, prob1, prob2 in zip(wind_directions2, direction_probabilities2, wind_speeds_probabilities2):
        for ws, prob3 in zip(wind_speeds2, prob2):
            cases.append([wdir, ws])
            probs.append(prob1 / 100.0 * prob3 / 100.0)

    cases = np.array(cases)

    print cases
    print probs

