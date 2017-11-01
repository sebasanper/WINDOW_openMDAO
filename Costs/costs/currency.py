def Cost1(value, currency, year):
    value_year = 2016
    # Inflation and exchange rate {'Currency Code': [Average inflation rate, Exchange rate to Euro]}
    conversion = {'USD': [2.57, 0.89],
                  'GBP': [2.55, 1.27],
                  'DKK': [1.84, 0.13],
                  'SEK': [2.03, 0.11],
                  'NOK': [1.95, 0.11],
                  'Euro': [2.16, 1.0]}

    inflation_rate = conversion[currency][0]
    exchange_rate = conversion[currency][1]

    return value * ((1.0 + (inflation_rate / 100.0)) ** (value_year - year)) * exchange_rate
