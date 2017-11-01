class AerodynamicAnalysts:
    rho_air = 1.225  # [kg/m^3]
    cd_cylinder = 1.2  # [-]
    
    def __init__(self, support_team):
        self.support_team = support_team
        pass

    def get_loads(self, wind_speed, wind_speed_height, alpha, height):
        base_diameter = self.support_team.design_variables.support_structure.tower.base_diameter
        top_diameter = self.support_team.design_variables.support_structure.tower.top_diameter
        base = self.support_team.properties.support_structure.platform_height 
        top = self.support_team.properties.support_structure.platform_height + self.support_team.design_variables.support_structure.tower.length
        z_from = height
        if z_from < base:
            z_from = base 

        fx = self.get_integrated_aerodynamic_force(wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from)
        my = -height * fx + self.get_integrated_aerodynamic_moment(wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from)
        
        if height < self.support_team.properties.support_structure.platform_height:
            base_diameter = self.support_team.design_variables.support_structure.transition_piece.diameter
            top_diameter = base_diameter
            base = self.support_team.properties.support_structure.base_tp 
            top = self.support_team.properties.support_structure.platform_height
            z_from = height
            if z_from < 0.0:
                z_from = 0.0
            fx_tp = self.get_integrated_aerodynamic_force(wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from)
            my_tp = -height * fx_tp + self.get_integrated_aerodynamic_moment(wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from)
            fx += fx_tp
            my += my_tp
        return [fx, 0.0, 0.0, 0.0, my, 0.0]

    def get_integrated_aerodynamic_force(self, wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from):
        a = z_from
        b = top
        l = top - base
        d_diameter = top_diameter - base_diameter
        
        return (0.5 * self.rho_air * self.cd_cylinder * wind_speed ** 2 * (1.0 / wind_speed_height) ** (2 * alpha) *
                (((base_diameter - base * d_diameter / l) * (1.0 / (2.0 * alpha + 1.0)) * b ** (2.0 * alpha + 1.0) + ((d_diameter / l) * (1.0 / (2.0 * alpha + 2.0)) * b ** (2.0 * alpha + 2.0))) -
                 ((base_diameter - base * d_diameter / l) * (1.0 / (2.0 * alpha + 1.0)) * a ** (2.0 * alpha + 1.0) + ((d_diameter / l) * (1.0 / (2.0 * alpha + 2.0)) * a ** (2.0 * alpha + 2.0)))) 
                )

    def get_integrated_aerodynamic_moment(self, wind_speed, wind_speed_height, alpha, base, top, base_diameter, top_diameter, z_from):
        a = z_from
        b = top
        l = top - base
        d_diameter = top_diameter - base_diameter
        
        return (0.5 * self.rho_air * self.cd_cylinder * wind_speed ** 2 * (1.0 / wind_speed_height) ** (2 * alpha) *
                (((base_diameter - base * d_diameter / l) * (1.0 / (2.0 * alpha + 2.0)) * b ** (2.0 * alpha + 2.0) + ((d_diameter / l) * (1.0 / (2.0 * alpha + 3.0)) * b ** (2.0 * alpha + 3.0))) -
                 ((base_diameter - base * d_diameter / l) * (1.0 / (2.0 * alpha + 2.0)) * a ** (2.0 * alpha + 2.0) + ((d_diameter / l) * (1.0 / (2.0 * alpha + 3.0)) * a ** (2.0 * alpha + 3.0)))) 
                )
