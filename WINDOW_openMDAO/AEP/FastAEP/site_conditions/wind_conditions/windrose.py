from numpy import exp
from WINDOW_openMDAO.input_params import cutin_wind_speed, cutout_wind_speed


class WeibullWindBins(object):

    def __init__(self, windrose_file):
        self.windrose_file = windrose_file
        self.direction = []
        self.weibull_scale = []
        self.weibull_shape = []
        self.dir_probability = []
        self.cutin = cutin_wind_speed
        self.cutout = cutout_wind_speed

        with open(self.windrose_file, 'r') as windrose:

            for line in windrose:
                columns = line.split()
                self.direction.append(float(columns[0]))
                self.weibull_scale.append(float(columns[1]))
                self.weibull_shape.append(float(columns[2]))
                self.dir_probability.append(float(columns[3]))

    def adapt_directions(self):
        self.new_direction = []
        self.new_direction_probability = []
        self.new_weibull_scale = []
        self.new_weibull_shape = []

        for i in range(len(self.direction)):
            if self.direction[i] % self.real_angle == 0.0:
                self.new_direction_probability.append(self.dir_probability[i])
                self.new_direction.append(self.direction[i])
                self.new_weibull_scale.append(self.weibull_scale[i])
                self.new_weibull_shape.append(self.weibull_shape[i])
            else:
                self.new_direction_probability[-1] += self.dir_probability[i]
        # print sum(self.dir_probability)
        # print self.new_direction
        # print self.new_direction_probability, sum(self.new_direction_probability)

        self.new_direction2 = []
        self.new_direction_probability2 = []
        self.new_weibull_shape2 = []
        self.new_weibull_scale2 = []
        n = int(self.new_direction[1] - self.new_direction[0]) // int(self.artificial_angle)

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
        delta = (self.cutout - self.cutin) / self.nbins
        windspeeds = []
        for i in range(self.nbins + 1):

            windspeeds.append(self.cutin + i * delta)

        return windspeeds

    def speed_probabilities(self):
        self.adapt_directions()
        speed_probabilities = []
        self.windspeeds = self.get_wind_speeds()
        # print self.windspeeds
        for angle in self.new_direction2:
            place = self.new_direction2.index(angle)
            prob_cutout = (1.0 - self.cumulative_weibull(self.cutout, self.new_weibull_scale2[place], self.new_weibull_shape2[place]))
            # print prob_cutout
            length = len(self.windspeeds)
            windspeedprobabilities = [0.0 for _ in range(length)]

            for i in range(length):

                if i == 0:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i], self.new_weibull_scale2[place], self.new_weibull_shape2[place]))

                elif i < length - 1:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i], self.new_weibull_scale2[place], self.new_weibull_shape2[place]) - sum(windspeedprobabilities[:i]))

                elif i == length - 1:

                    windspeedprobabilities[i] = (self.cumulative_weibull(self.windspeeds[i], self.new_weibull_scale2[place], self.new_weibull_shape2[place]) - sum(windspeedprobabilities[:i]) + prob_cutout)

            speed_probabilities.append([item * 100.0 for item in windspeedprobabilities])
        # print [sum(i) for i in speed_probabilities]
        return [self.windspeeds for _ in range(len(self.new_direction2))], speed_probabilities
