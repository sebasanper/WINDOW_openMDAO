from WINDOW_openMDAO.src.api import AbstractWakeAddedTurbulence
from WINDOW_openMDAO.input_params import max_n_turbines
import numpy as np
from numpy import sqrt


class Frandsen2(AbstractWakeAddedTurbulence):

    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing):
        return sqrt(1.2 * ct / spacing ** 2.0 + ambient_turbulence ** 2.0)


class DanishRecommendation(AbstractWakeAddedTurbulence):

    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing):

        def beta_v(u):
            if u < 12.0:
                beta = 1.0
            elif u < 20.0:
                beta = 1.747 - 0.0625 * u
            else:
                beta = 0.5
            return beta

        # Beta_l, x is turbine spacing

        def beta_l(d, cluster=True):
            if cluster:
                if d < 2.9838:
                    beta = 1.0
                elif d < 5.9856:
                    beta = 1.333 - 0.1116 * d
                else:
                    beta = 0.665

            else:
                if d < 5.0:
                    beta = 1.0
                elif d < 10.0:
                    beta = 1.333 - 0.067 * d
                else:
                    beta = 0.665

            return beta

        Iw = 0.15 * beta_v(wind_speed) * beta_l(spacing)
        Ia = ambient_turbulence
        Id = sqrt(Ia ** 2.0 + Iw ** 2.0)

        return Id


class Larsen(AbstractWakeAddedTurbulence):

    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing):

        # Wind Resource Assessment and Micro-siting: Science and Engineering
        # By Matthew Huaiquan Zhangaiquan Zhang
        # for spacings larger than 2D
        s = spacing
        Iw = 0.29 * s ** (- 1.0 / 3.0) * (1.0 - (1.0 - ct) ** 0.5) ** 0.5
        Ia = ambient_turbulence
        Id = sqrt(Ia ** 2.0 + Iw ** 2.0)
        return Id


class Frandsen(AbstractWakeAddedTurbulence):
    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing, large=False):
        #  For spacings smaller than 10D
        Ia = ambient_turbulence
        s = spacing
        # 0.8 sometimes 0.3 double check
        # u = 10.0  # wind speed
        Iw = 1.0 / (1.5 + 0.8 * s / ct ** 0.5)
        It = (Iw ** 2.0 + Ia ** 2.0) ** 0.5

        if large:
            #  More than 5 turbines between turbine under consideration and edge of park, OR turbines spaces less than 3D
            # in the direction perpendicular to wind. For regular layouts.

            sd = 7.0
            sc = 7.0
            Iw = 0.36 / (1.0 + 0.2 * (sd * sc / ct) ** 0.5)
            Ia = 0.5 * (Ia + (Iw ** 2.0 + Ia ** 2.0) ** 0.5)
            It = (Iw ** 2.0 + Ia ** 2.0) ** 0.5

        return It


class Quarton(AbstractWakeAddedTurbulence):

    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing, tsr=7.6):
        D = 40.0 * 2.0
        spacing *= D
        x = spacing
        Ia = ambient_turbulence
        K1 = 5.7#4.8
        a1 = 0.7
        a2 = 0.68
        a3 = - 0.96#- 0.57
        m = sqrt(1.0 / (1.0 - ct))
        r0 = D / 2.0 * sqrt((m + 1.0) / 2.0)

        if Ia >= 0.02:
            da = 2.5 * Ia + 0.05
        else:
            da = 5.0 * Ia

        B = 3  # Number of blades
        L = tsr  # Tip speed ratio
        dl = 0.012 * B * L
        dm = (1.0 - m) * sqrt(1.49 + m) / (9.76 * (1.0 + m))

        xh = r0 * (da + dl + dm) ** (- 0.5)
        xn = xh * sqrt(0.212 + 0.145 * m) * (1.0 - sqrt(0.134 + 0.124 * m)) / (1.0 - sqrt(0.212 + 0.145 * m)) / sqrt(0.134 + 0.124 * m)
        Iw = K1 * (ct ** a1) * (Ia ** a2) * (x / xn) ** a3
        return sqrt(Iw ** 2.0 + Ia ** 2.0)


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class AddedTurbModel1(AbstractWakeAddedTurbulence):

        def compute(self, inputs, outputs):
            TI_amb = inputs['TI_amb']
            ct = inputs['ct']
            u_inf = inputs['u_inf']
            d = inputs['d']

            outputs['TI_eff'] = TI_amb * ct + u_inf / d

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('TI_amb', 0.12)
    ivc.add_output('ct', 0.6)
    ivc.add_output('u_inf', 8.0)
    ivc.add_output('d', 460.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('added1', AddedTurbModel1())

    model.connect('indep.TI_amb', 'added1.TI_amb')
    model.connect('indep.ct', 'added1.ct')
    model.connect('indep.u_inf', 'added1.u_inf')
    model.connect('indep.d', 'added1.d')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['added1.TI_eff'])
