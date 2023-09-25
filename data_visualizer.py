import os
import csv
import pandas as pd
import matplotlib.pyplot as plt

class DataViewer:
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.load_data()

    def load_data(self) -> pd.DataFrame:
        data = []

        # with open(self.data_path, 'r') as file:
        #     raw_data = csv.reader(file, )
        #     for row in raw_data:
        #         # data.append(field.strip('"') for field in row[0].split(";"))
        #         data.append(row)
        # print(data)
        # headers, data = data[0], data[1:]
        # data_df = pd.DataFrame(data=data, columns=headers)
        data_df = pd.read_csv(self.data_path, delimiter=';')
        data_df['VALUE'] = data_df['VALUE'].astype(float)
        data_df['SECONDS'] = data_df['SECONDS'].astype(float)
        data_df['SECONDS'] -= data_df['SECONDS'].min()

        self.sensor_data = {sensor: data_df[data_df['PID'] == sensor] for sensor in data_df['PID'].unique()}

    def plot_data(self, output_path) -> None:
        os.makedirs(output_path, exist_ok=True)

        for sensor, df in self.sensor_data.items():
            x, y, units = df['SECONDS'], df['VALUE'], df['UNITS'].iloc[0]
            sensor_name = sensor.replace(" ", "_").replace("/", "_")

            plt.figure(figsize=(11, 8.5))
            plt.plot(x, y)
            plt.xlabel('Time (seconds)')
            plt.ylabel(f'{sensor} {units}')
            plt.savefig(f'{output_path}/{sensor_name}.png')
            plt.close()

if __name__ == "__main__":

    data_file = '2023-09-23 00-53-20.csv'
    data_file_path = f'data/{data_file}'
    plot_output_path = f'data/output/{data_file.rstrip(".csv")}'

    data_viewer = DataViewer(data_file_path)
    data_viewer.plot_data(plot_output_path)