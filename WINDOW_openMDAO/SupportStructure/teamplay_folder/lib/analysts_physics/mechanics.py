from math import pi, sqrt


class MechanicalAnalysts:
    yield_stress_steel = 200000000.0
    nu_steel = 0.3
    e_modulus_steel = 210000000000.0
    
    def __init__(self, support_team):
        self.support_team = support_team

    def get_stress_pile(self, d_outer, d_inner, fz, my):
        cross_sectional_area = (pi / 4.0) * (d_outer**2 - d_inner**2) 
        moment_of_inertia = pi * (d_outer**4 - d_inner**4) / 64.0
        stress = (abs(fz) / cross_sectional_area) + (abs(my) * d_outer) / (2.0 * moment_of_inertia)
        return [stress, self.yield_stress_steel]

    def get_min_thickness_euler(self, radius, fz, l):
        # Thickness at which the Euler force and axial force are equal:   
        t = (fz * 4.0 * l ** 2.0) / (pi ** 2.0 * self.e_modulus_steel * pi * radius ** 3.0)
        # Set minimum thickness 10% higher:
        return 1.1 * t
    
    def get_stress_tower(self, t, radius, fz, my, l):
        sigma_ad = fz / (2.0 * pi * radius * t)
        sigma_bd = my / (pi * radius**2 * t)
        epsilon_a = 0.83 / (sqrt(1.0 + 0.01 * (radius / t)))
        epsilon_b = 0.1887 + 0.8113 * epsilon_a
        epsilon = (epsilon_a * sigma_ad + epsilon_b * sigma_bd) / (sigma_ad + sigma_bd)
        
        sigma_el = self.e_modulus_steel / ((radius / t) * sqrt(3.0 * (1.0 - self.nu_steel**2)))
        lambda_a = sqrt(self.yield_stress_steel / (epsilon * sigma_el))
        if (l <= (1.42 * radius * sqrt(radius / t))) or (lambda_a <= 0.3):
            sigma_cr = self.yield_stress_steel 
        elif 0.3 < lambda_a <= 1.0:
            sigma_cr = (1.5 - 0.913 * sqrt(lambda_a)) * self.yield_stress_steel
        else:    
            sigma_cr = (1.5 - 0.913 * sqrt(lambda_a)) * self.yield_stress_steel
        
        n_el = (pi**2 * self.e_modulus_steel * pi * radius**3 * t / (4.0 * l**2))
        lambda_r = sqrt(sigma_cr / (n_el / (2.0 * pi * radius * t)))
        k = radius / 2.0
        e = max(0.34 * (lambda_r - 0.2) * k, 0.0)
        if e > (2.0 * l / 1000.0):
            e = 2.0 * e - (2.0 * l / 1000.0)
            
        stress = (fz / (2.0 * pi * radius * t)) + (n_el / (n_el - fz)) * ((my + fz * e) / (pi * radius**2 * t))
        return [stress, sigma_cr]
