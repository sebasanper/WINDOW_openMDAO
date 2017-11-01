from math import pi, tanh, sinh, cosh, sqrt


class HydrodynamicAnalysts:
    cm = 2.0
    cd = 1.0
    g = 9.81  # [m/s^2]
    
    def __init__(self, support_team):
        self.support_team = support_team
        pass

    def get_loads(self, wave_height, wave_number, height):
        if height >= 0.0:
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        diameter = self.support_team.design_variables.support_structure.transition_piece.diameter
        base = max(height, self.support_team.properties.support_structure.base_tp)
        top = 0.0
        inertia_force = self.get_integrated_inertia_force(wave_height, wave_number, base, top, diameter)
        drag_force = self.get_integrated_drag_force(wave_height, wave_number, base, top, diameter)
        inertia_moment = -height * inertia_force + self.get_integrated_inertia_moment(wave_height, wave_number, base, top, diameter)
        drag_moment = -height * drag_force + self.get_integrated_drag_moment(wave_height, wave_number, base, top, diameter) 
        
        fx = sqrt(inertia_force ** 2.0 + drag_force ** 2.0)
        my = sqrt(inertia_moment ** 2.0 + drag_moment ** 2.0)

        if height < self.support_team.properties.support_structure.base_tp:
            diameter = self.support_team.design_variables.support_structure.monopile.diameter
            base = height
            top = self.support_team.properties.support_structure.base_tp
            inertia_force = self.get_integrated_inertia_force(wave_height, wave_number, base, top, diameter)
            drag_force = self.get_integrated_drag_force(wave_height, wave_number, base, top, diameter)
            inertia_moment = -height * inertia_force + self.get_integrated_inertia_moment(wave_height, wave_number, base, top, diameter)
            drag_moment = -height * drag_force + self.get_integrated_drag_moment(wave_height, wave_number, base, top, diameter)

            fx += sqrt(inertia_force ** 2 + drag_force ** 2)
            my += sqrt(inertia_moment ** 2 + drag_moment ** 2)
        return [fx, 0.0, 0.0, 0.0, my, 0.0]

    def get_integrated_inertia_force(self, wave_height, wave_number, base, top, diameter):
        zeta = wave_height / 2
        k = wave_number
        a = base
        b = top
        d = self.support_team.physical_environment.site.water_depth
        
        return self.cm * (self.support_team.physical_environment.site.water_density * pi * diameter ** 2.0 / 4.0) * zeta * self.g * (tanh(k * d) / sinh(k * d)) * (sinh(k * (b + d))-sinh(k * (a + d)))

    def get_integrated_drag_force(self, wave_height, wave_number, base, top, diameter):
        zeta = wave_height / 2.0
        k = wave_number
        a = base
        b = top
        d = self.support_team.physical_environment.site.water_depth
        
        return self.cd * 0.5 * self.support_team.physical_environment.site.water_density * diameter * zeta ** 2.0 * self.g * (2.0 / sinh(2.0 * k * d)) * ((sinh(2.0 * k * (b + d)) / 4.0 + k * (b + d) / 2.0) - (sinh(2.0 * k * (a + d)) / 4.0 + k * (a + d) / 2.0))

    def get_integrated_inertia_moment(self, wave_height, wave_number, base, top, diameter):
        zeta = wave_height / 2.0
        k = wave_number
        a = base
        b = top
        d = self.support_team.physical_environment.site.water_depth

        return self.cm * (self.support_team.physical_environment.site.water_density * pi * diameter ** 2.0 / 4.0) * zeta * self.g * (tanh(k * d) / sinh(k * d)) * ((b * sinh(k * (b + d)) - cosh(k * (b + d))/k) - (a * sinh(k * (a + d)) - cosh(k * (a + d))/k))

    def get_integrated_drag_moment(self, wave_height, wave_number, base, top, diameter):
        zeta = wave_height / 2.0
        k = wave_number
        a = base
        b = top
        d = self.support_team.physical_environment.site.water_depth

        return (self.cd * 0.5 * self.support_team.physical_environment.site.water_density * diameter * zeta ** 2.0 * self.g * (2.0 / sinh(2 * k * d)) * ((b * (sinh(2.0 * k * (b + d)) / 4.0 + k * (b + d) / 2.0) - (cosh(2.0 * k * (b + d)) / (8.0 * k) + (k * (b + d)) ** 2.0 / (4.0 * k))) -
                   (a * (sinh(2.0 * k * (a + d)) / 4.0 + k * (a + d) / 2.0) - (cosh(2.0 * k * (a + d)) / (8.0 * k) + (k * (a + d))**2 / (4.0 * k)))))
