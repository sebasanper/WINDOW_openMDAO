from WINDOW_openMDAO.src.api import AbstractOandM


class OM_model1(AbstractOandM):
    def OandM_model(self, AEP, eff):
        costs_om = 16.0 * AEP / eff / 1000000.0
        availability = 0.98
        # costs_om = 50000000.
        return costs_om, availability
