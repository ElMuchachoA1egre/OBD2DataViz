import os
import csv
import glob as g
import pandas as pd
import matplotlib.pyplot as plt

class DataViewer:
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.cwd = os.getcwd()
        self.load_data()

    def load_data(self) -> pd.DataFrame:

        def get_delimiter(file_path, bytes = 4096):
            sniffer = csv.Sniffer()
            data = open(file_path, "r").read(bytes)
            delimiter = sniffer.sniff(data).delimiter
            return delimiter
        
        self.data = {}
        self.channel_data = {}

        for csv_file in g.glob(os.path.join(self.cwd, data_path, '*.csv')):
            file_name = os.path.basename(csv_file)
            data_df = pd.read_csv(csv_file, delimiter=get_delimiter(csv_file))
            data_df['VALUE'] = data_df['VALUE'].astype(float)
            data_df['SECONDS'] = data_df['SECONDS'].astype(float)
            data_df['SECONDS'] -= data_df['SECONDS'].min()
            sensor_data = {sensor: data_df[data_df['PID'] == sensor] for sensor in data_df['PID'].unique()}
            self.data[file_name] = sensor_data

            for sensor, df in sensor_data.items():

                if sensor not in self.channel_data.keys():
                    self.channel_data[sensor] = {
                        'data_file' : [],
                        'data' : []
                    }

                self.channel_data[sensor]['data_file'].append(file_name)
                self.channel_data[sensor]['data'].append(df)
 

        
    def plot_data(self, output_path) -> None:
        
        os.makedirs(output_path, exist_ok=True)

        channels = {}

        # for data_file_name, sensor_data in self.data.items():
        #     full_output_path = os.path.join(output_path, data_file_name)
        #     os.makedirs(full_output_path, exist_ok=True)
        #     for sensor, df in sensor_data.items():
        #         x, y, units = df['SECONDS'], df['VALUE'], df['UNITS'].iloc[0]
        #         sensor_name = sensor.replace(" ", "_").replace("/", "_")
                
        #         plt.figure(figsize=(11, 8.5))
        #         plt.plot(x, y)
        #         plt.xlabel('Time (seconds)')
        #         plt.ylabel(f'{sensor} {units}')
        #         plt.savefig(f'{full_output_path}/{sensor_name}.png')
        #         plt.close()
        
        for channel_name, data in self.channel_data.items():
            data_files, data_dfs = data['data_file'], data['data']
            plt.figure(figsize=(11, 8.5))
        
            for data_file, data_df in zip(data_files, data_dfs):
                x, y, units = data_df['SECONDS'], data_df['VALUE'], data_df['UNITS'].iloc[0]
                channel_name = channel_name.replace(" ", "_").replace("/", "_")
                plt.plot(x,y, label = data_file)
            
            plt.xlabel('Time (seconds)')
            plt.ylabel(f'{channel_name} {units}')
            plt.legend()
            plt.title(f'{channel_name}')
            plt.savefig(f'{output_path}/{channel_name}.png')
            plt.close()


if __name__ == "__main__":

    data_path = 'data'
    data_viewer = DataViewer(data_path)
    data_viewer.plot_data(output_path='output')