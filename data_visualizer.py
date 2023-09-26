import os
import csv
import glob as g
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


class OBD2Dataframe:

    def __init__(self, raw_data_frame: pd.DataFrame) -> None:
        self.raw_data = raw_data_frame
        self.column_dtypes = {
            'VALUE' : float,
            'SECONDS': float
        }
        self.processed_data = self.parse_raw_data()

    def parse_raw_data(self) -> pd.DataFrame:

        self.raw_data = self.raw_data.astype(self.column_dtypes)
        self.raw_data['SECONDS'] -= self.raw_data['SECONDS'].min()
        self.raw_data['SECONDS'] = pd.to_datetime(self.raw_data['SECONDS'], unit='s')

        sensor_channels = self.raw_data['PID'].unique()
        sensor_data = {sensor:  self.raw_data[ self.raw_data['PID'] == sensor] for sensor in  sensor_channels}

        for sensor, df in sensor_data.items():
            df = df.drop_duplicates(subset=['SECONDS'])
            df = df.set_index('SECONDS')
            resampled_df = df.resample('1S').ffill()
            resampled_df = resampled_df.rename(columns={'VALUE': sensor})
            sensor_data[sensor] = resampled_df[sensor]

        
        processed_data = pd.concat(sensor_data.values(), axis='columns')

        return processed_data

class DataViewer:
    def __init__(self, data_path) -> None:
        self.data_path = data_path
        self.cwd = os.getcwd()
        self.processed_data_frames = {}
        self.column_names = []
        self.load_data()

    def load_data(self) -> pd.DataFrame:

        def get_delimiter(file_path, bytes = 4096):
            sniffer = csv.Sniffer()
            data = open(file_path, "r").read(bytes)
            delimiter = sniffer.sniff(data).delimiter
            return delimiter

        for csv_file in g.glob(os.path.join(self.cwd, data_path, '*.csv')):
            data_file_name = os.path.basename(csv_file)
            data_df = pd.read_csv(csv_file, delimiter=get_delimiter(csv_file))
            processed_data_frame = OBD2Dataframe(raw_data_frame=data_df).processed_data
            self.column_names.extend(processed_data_frame.columns.tolist())
            self.processed_data_frames[data_file_name] = processed_data_frame

        self.column_names = list(set(self.column_names))

    def plot_data(self, output_path) -> None:
        
        os.makedirs(output_path, exist_ok=True)

        for channel_name in self.column_names:
            
            plt.figure(figsize=(11, 8.5))

            for data_file_name, data_frame in self.processed_data_frames.items():  

                try:
                    x, y = data_frame.index, data_frame[channel_name]
                    plt.plot(x,y, label = data_file_name)
                except:
                    pass

            plt.xlabel('Time (seconds)')
            date_format = DateFormatter('%H:%M:%S')
            plt.gca().xaxis.set_major_formatter(date_format)

            plt.ylabel(f'{channel_name}')
            plt.legend()
            plt.title(f'{channel_name}')
            plt.savefig(f'{output_path}/{channel_name.replace(" ", "_").replace("/", "_")}.png')
            plt.close()
        
            
        plt.figure(figsize=(11, 8.5))

        for data_file_name, data_frame in self.processed_data_frames.items():  

            try:
                x, y = data_frame['Vehicle speed'], data_frame['Calculated instant fuel consumption']
                plt.scatter(x,y, label = data_file_name, s=5)
            except:
                pass

        plt.xlabel('Vehicle Speed (MPH)')
        plt.ylabel('Calculated Instant Fuel Consumption (MPG)')
        plt.legend()
        plt.title('MPG vs Speed')
        plt.savefig(f'{output_path}/MPG vs Speed.png')
        plt.close()

if __name__ == "__main__":

    data_path = 'data'
    data_viewer = DataViewer(data_path)
    data_viewer.plot_data(output_path='output')