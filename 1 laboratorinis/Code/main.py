# Python3.8
# Jokubas Akramas IFF-8/12
# 1 laboratorinis darbas
# P176B101 Intelektikos pagrindai 2021
from functools import reduce
import numpy as np
import constants as c
import matplotlib.pyplot as plt
import handler


def append_element_to_headers(headers, values):
    element = {}
    for i in range(len(values)):
        element[headers[i]] = values[i]
    return element


def analyse_continuous_data(data, values):
    csv_list = []
    for i in values.keys():
        sublist = list(map(lambda x: int(x[i]) if x[i] != '' else '', data))
        average = np.average(list(filter(lambda x: x != '', sublist)))
        sublist = list(map(lambda x: average if x == '' else x, sublist))
        for u in data:  # Tuščios reikšmės užpildomos vidurkiais
            if u[i] == '':
                u[i] = average
        sublist.sort()
        values[i][2] = values[i][2] * 100
        values[i].append(min(sublist))  # Minimali reikšmė
        values[i].append(max(sublist))  # Maksimali reikšmė
        values[i].append(np.quantile(sublist, .25))  # 1-asis kvartilis
        values[i].append(np.quantile(sublist, .75))  # 3-asis kvartilis
        values[i].append(average)  # Vidurkis
        values[i].append(np.round(np.median(sublist)))  # Mediana
        values[i].append(np.std(sublist))  # Standartinis nuokrypis
        csv_list.append(append_element_to_headers(c.CONTINUOUS_ANALYSIS_OUTPUT_HEADERS, values[i]))
    return csv_list


def all_modas(data, values_list):
    unique_values = list(set(data))
    value_counts = list(map(lambda x: len(list(filter(lambda y: y == x, data))), unique_values))
    counts_copy = value_counts.copy()
    counts_copy.sort()
    moda_index = value_counts.index(counts_copy.pop()), value_counts.index(counts_copy.pop())
    for index in moda_index:
        values_list.append(unique_values[index])
        values_list.append(value_counts[index])
        values_list.append(100 * value_counts[index] / len(data))
    return unique_values[moda_index[0]]


def analyse_categorical_data(data, values):
    csv_list = []
    for i in values.keys():
        sublist = list(map(lambda x: x[i], data))
        temp = []
        moda = all_modas(list(filter(lambda x: x != '', sublist)), temp)
        sublist = list(map(lambda x: x if x != '' else moda, sublist))
        for u in data:  # Tuščios reikšmės užpildomos vidurkiais
            if u[i] == '':
                u[i] = moda
        values[i][2] = values[i][2] * 100
        all_modas(sublist, values[i])  # 1-oji ir 2-oji modos su charakteristikomis
        csv_list.append(append_element_to_headers(c.CATEGORICAL_ANALYSIS_OUTPUT_HEADERS, values[i]))
    return csv_list


def analyze_initial_values(data, headers):
    values = {}
    for i in headers:
        sublist = list(map(lambda x: x[i], data))
        values[i] = [
            i,  # Atributo pavadinimas

            len(sublist),  # Eilučių kiekis
            len(list(filter(lambda x: x == '', sublist))) / len(sublist),  # Trūkstamos reikšmės
        ]
        cardinality = list(set(sublist))
        cardinality.remove('')
        values[i].append(len(cardinality))  # Kardinalumas
    return values


def horizontal_removal(data, remove_step):
    print('---------------------------------------Horizontalus šalinimas---------------------------------------')
    for row in data:
        empty_values = len(list(filter(lambda x: x == '', row.values()))) / len(row)
        if empty_values >= remove_step:
            data.remove(row)
            print('Eilutės: ', row, '\ntuščiosios reikšmės viršija nustatytą limitą (',
                  100 * remove_step, '%), todėl eilutė PAŠALINAMA.')


def vertical_removal(data, continuous, continuous_headers, categorical, categorical_headers, remove_step):
    print('---------------------------------------Vertikalus šalinimas---------------------------------------')
    for cont in continuous_headers:
        if float(continuous[cont][2]) >= remove_step:
            for i in data:
                del i[cont]
            print('Tolydinio atributo: ', continuous[cont][0], 'tuščiosios reikšmės viršija nustatytą limitą (',
                  100 * remove_step, '%), todėl atributas PAŠALINAMAS.')
            del continuous[cont]
    for cont in categorical_headers:
        if float(categorical[cont][2]) >= remove_step:
            for i in data:
                del i[cont]
            print('Kategorinio atributo: ', categorical[cont][0], 'tuščiosios reikšmės viršija nustatytą limitą (',
                  100 * remove_step, '%), todėl atributas PAŠALINAMAS.')
            del categorical[cont]


def handle_missing_values(data, continuous, continuous_headers, categorical, categorical_headers):
    horizontal_removal(data, 0.6)  # Horizontalus šalinimas (jei 60% eilutės tuščia)
    vertical_removal(data, continuous, continuous_headers, categorical, categorical_headers,
                     0.6)  # Vertikalus šalinimas (jei 60% stulpelio tuščia)


def draw_histograms(data, headers):
    n = round(1 + 3.22 * np.log(len(data)))
    for head in headers:
        sublist = list(map(lambda x: x[head], data))
        plt.title(head)
        plt.hist(sublist, bins=n)
        plt.show()


# Nuskaitomas duomenų failas
dataset, fields = handler.csv_to_dict_list(c.DATASET_TRAIN_FILE)
# Sukuriamas išvedimo folderis
handler.create_package_if_no_exist(c.OUTPUT_FOLDER_NAME)
# Apdorojamos pradinės tolydžiųjų charakteristikos
continuous = analyze_initial_values(dataset, c.CONTINUOUS_DATA_HEADERS)
# Apdorojamos pradinės kategorinių charakteristikos
categorical = analyze_initial_values(dataset, c.CATEGORICAL_DATA_HEADERS)
# Tuščių reikšmių apdorojimas šalinant horizontaliai ir vertikaliai
handle_missing_values(dataset, continuous, c.CONTINUOUS_DATA_HEADERS,
                      categorical, c.CATEGORICAL_DATA_HEADERS)
# Apdorojamos likusios tolydžiųjų charakteristikos
continuous_dict_list = analyse_continuous_data(dataset, continuous)
# Apdorojamos likusios kategorinių charakteristikos
categorical_dict_list = analyse_categorical_data(dataset, categorical)
# Išvedama tolydžiųjų duomenų charakteristikų lentelė
handler.write_to_csv(c.CONTINUOUS_OUTPUT_PATH, continuous_dict_list,
                     c.CONTINUOUS_ANALYSIS_OUTPUT_HEADERS)
# Išvedama kategorinių duomenų charakteristikų lentelė
handler.write_to_csv(c.CATEGORICAL_OUTPUT_PATH, categorical_dict_list,
                     c.CATEGORICAL_ANALYSIS_OUTPUT_HEADERS)

final_headers = []
for i in categorical.keys():
    final_headers.append(i)
for i in continuous.keys():
    final_headers.append(i)
final_headers.append('MALICIOUS_OFFENSE')

# Išvedami pertvarkyti duomenys .csv formatu
handler.write_to_csv(c.PROCESSED_OUTPUT_PATH, dataset, final_headers)

draw_histograms(dataset, final_headers)
