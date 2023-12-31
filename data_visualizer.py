import os
import csv
import glob as g
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
            if sensor == 'Vehicle speed':
                latitude = resampled_df['LATITUDE'].astype(float)
                longitude = resampled_df['LONGTITUDE'].astype(float)

        sensor_data['LATITUDE'] = latitude
        sensor_data['LONGTITUDE'] = longitude

        
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

        # for channel_name in self.column_names:
            
        #     plt.figure(figsize=(11, 8.5))

        #     for data_file_name, data_frame in self.processed_data_frames.items():  

        #         try:
        #             x, y = data_frame.index, data_frame[channel_name]
        #             plt.plot(x,y, label = data_file_name)
        #         except:
        #             pass

        #     plt.xlabel('Time (seconds)')
        #     date_format = DateFormatter('%H:%M:%S')
        #     plt.gca().xaxis.set_major_formatter(date_format)

        #     plt.ylabel(f'{channel_name}')
        #     plt.legend()
        #     plt.title(f'{channel_name}')
        #     plt.savefig(f'{output_path}/{channel_name.replace(" ", "_").replace("/", "_")}.png')
        #     plt.close()
        
            
        plt.figure(figsize=(11, 8.5))

        for data_file_name, data_frame in self.processed_data_frames.items():  

            try:
                # filtered_data=data_frame(data_frame)
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


        plt.figure(figsize=(11, 8.5))

        for data_file_name, data_frame in self.processed_data_frames.items():  

            try:
                # filtered_data=data_frame(data_frame)
                x, y = data_frame['Vehicle speed'], data_frame['Transmission Temperature (var.2)'].diff(periods=90)
                plt.scatter(x,y, label = data_file_name, s=5)
            except:
                pass

        plt.ylim(-15,15)
        plt.xlabel('Vehicle Speed (MPH)')
        plt.ylabel('Transmission Temperature Change (F) over 90 Seconds')
        # plt.legend()
        plt.title('JEEP PATRIOT 2009: Transmission Temperature Change (F) vs Speed')
        plt.savefig(f'{output_path}/Transmission_Temperature_(var.2) Diff vs Speed.png')
        plt.close()


        # Driving Coordinates

        plt.figure()
        img = plt.imread('data/38.6619-40.4595--107.600--104.5624.png')
        bounding_coordinates = [-107.4600, -104.5624, 38.6619, 40.4595]
        plt.imshow(img, zorder=0, extent=bounding_coordinates, aspect='auto')

        plt.scatter(-104.9934334445547, 40.28780699973443, label = 'Ursa Major', s=50, marker='*', zorder=123) 
        
        for data_file_name, data_frame in self.processed_data_frames.items():  

            try:
                x, y = data_frame['LONGTITUDE'], data_frame['LATITUDE']
                plt.scatter(x,y, label = data_file_name, s=2)
            except:
                pass
        plt.xlabel('LONGITUDE')
        plt.ylabel('LATITUDE')
        plt.legend(fontsize = '6')
        plt.title('JEEP PATRIOT 2009: DRIVING GPS COORDINATES')
        plt.savefig(f'{output_path}/driving_coordinates.png', dpi = 600)
        plt.close()



        # Driving Coordinates

        plt.figure()
        img = plt.imread('data/38.6619-40.4595--107.600--104.5624.png')
        bounding_coordinates = [-107.4600, -104.5624, 38.6619, 40.4595]
        plt.imshow(img, zorder=0, extent=bounding_coordinates, aspect='auto')

        plt.scatter(-104.9934334445547, 40.28780699973443, label = 'Ursa Major', s=50, marker='*', zorder=123) 
        
        colors = np.linspace(-20,260,20)

        for data_file_name, data_frame in self.processed_data_frames.items():  

            try:
                x, y = data_frame['LONGTITUDE'], data_frame['LATITUDE']
                atf_temp = data_frame['Transmission Temperature (var.2)']/266
                plt.scatter(x,y, label = data_file_name, s=2, c=atf_temp, cmap='inferno')
            except:
                pass
        plt.clim(100/266, 1)
        plt.colorbar()
        plt.xlabel('LONGITUDE')
        plt.ylabel('LATITUDE')
        plt.legend(fontsize = '6')
        plt.title('JEEP PATRIOT 2009: Transmission Temperature (F)')
        plt.savefig(f'{output_path}/Transmission Temperature Coordinates.png', dpi = 600)
        plt.close()


        # Driving Coordinates

        plt.figure()
        img = plt.imread('data/38.6619-40.4595--107.600--104.5624.png')
        bounding_coordinates = [-107.4600, -104.5624, 38.6619, 40.4595]
        plt.imshow(img, zorder=0, extent=bounding_coordinates, aspect='auto')
        plt.scatter(-104.9934334445547, 40.28780699973443, label = 'Ursa Major HQ', s=25, marker='*', zorder=123) 
        
        highlighted_channel = 'Vehicle speed'
        data_accumulator = []

        for data_file_name, data_frame in self.processed_data_frames.items():  
            data_accumulator.append(data_frame[['LONGTITUDE', 'LATITUDE', highlighted_channel]])

        concat_data= pd.concat(data_accumulator)

    
        try:
            x, y = concat_data['LONGTITUDE'], concat_data['LATITUDE']
            color_data = concat_data[highlighted_channel]
            plt.scatter(x,y, s=1, c=color_data, cmap='inferno')
        except:
            pass

        plt.colorbar()
        plt.xlabel('LONGITUDE')
        plt.ylabel('LATITUDE')
        plt.legend(fontsize = '6', loc = 'best' )
        plt.title(f'JEEP PATRIOT 2009: {highlighted_channel}')
        plt.savefig(f'{output_path}/{highlighted_channel} Coordinates.png', dpi = 600)
        plt.close()

        # Driving Coordinates

        plt.figure()
        img = plt.imread('data/38.6619-40.4595--107.600--104.5624.png')
        bounding_coordinates = [-107.4600, -104.5624, 38.6619, 40.4595]
        plt.imshow(img, zorder=0, extent=bounding_coordinates, aspect='auto')
        plt.scatter(-104.9934334445547, 40.28780699973443, label = 'Ursa Major HQ', s=25, marker='*', zorder=123) 
        
        highlighted_channel = 'Calculated instant fuel consumption'
        data_accumulator = []

        for data_file_name, data_frame in self.processed_data_frames.items():  
            data_accumulator.append(data_frame[['LONGTITUDE', 'LATITUDE', highlighted_channel]])

        concat_data= pd.concat(data_accumulator)

    
        try:
            x, y = concat_data['LONGTITUDE'], concat_data['LATITUDE']
            color_data = concat_data[highlighted_channel]
            plt.scatter(x,y, s=1, c=color_data, cmap='inferno')
        except:
            pass
        
        plt.clim(0,30)
        plt.colorbar()
        plt.xlabel('LONGITUDE')
        plt.ylabel('LATITUDE')
        plt.legend(fontsize = '6', loc = 'best' )
        plt.title(f'JEEP PATRIOT 2009: {highlighted_channel}')
        plt.savefig(f'{output_path}/{highlighted_channel} Coordinates.png', dpi = 600)
        plt.close()


        plt.figure()
        img = plt.imread('data/38.6619-40.4595--107.600--104.5624.png')
        bounding_coordinates = [-107.4600, -104.5624, 38.6619, 40.4595]
        plt.imshow(img, zorder=0, extent=bounding_coordinates, aspect='auto')
        plt.scatter(-104.9934334445547, 40.28780699973443, label = 'Ursa Major HQ', s=25, marker='*', zorder=123) 
        
        highlighted_channel = 'Vehicle speed'
        data_accumulator = []

        for data_file_name, data_frame in self.processed_data_frames.items():  
            data_accumulator.append(data_frame[['LONGTITUDE', 'LATITUDE', highlighted_channel]])

        concat_data= pd.concat(data_accumulator)

    
        try:
            x, y = concat_data['LONGTITUDE'], concat_data['LATITUDE']
            color_data = concat_data[highlighted_channel].diff()
            plt.scatter(x,y, s=1, c=color_data, cmap='inferno')
        except:
            pass
        
        plt.clim(-1,1)
        plt.colorbar()
        plt.xlabel('LONGITUDE')
        plt.ylabel('LATITUDE')
        plt.legend(fontsize = '6', loc = 'best' )
        plt.title(f'JEEP PATRIOT 2009: {highlighted_channel} Diff')
        plt.savefig(f'{output_path}/{highlighted_channel} Diff Coordinates.png', dpi = 600)
        plt.close()


if __name__ == "__main__":

    data_path = 'data'
    data_viewer = DataViewer(data_path)
    data_viewer.plot_data(output_path='output')