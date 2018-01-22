
model.add_design_var('indep2.layout', lower=np.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]), upper=np.array([[1120.0, 1120.0], [1120.0, 1120.0], [1120.0, 1120.0]]), scaler=1.0/1120.0)
print(prob['constraint_boundary.magnitude_violations'])
