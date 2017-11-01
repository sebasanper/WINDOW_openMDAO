from src.api import AbstractOandM


class OM_model1(AbstractOandM):
    def OandM_model(self, AEP):
        costs_om = 16.0 * AEP / 1000000.0
        availability = 0.98
        return costs_om, availability
