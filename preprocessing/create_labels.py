import numpy as np
import pandas as pd
import glob
import sys
import os


def find_label(file, path):
    """Find audit label relating to spectrogram file.
    
    # Arguments
    	file: spectrogram file.
	path: spectrogram directory.
	
    # Returns
    	audit label file path relating to spectrogram file.
   	If the file has multiple audit label files, 
	the first label will be returned.
    """
    label_path = os.path.dirname(os.path.dirname(path)) + '/audit/'
    label_search = ''.join(file.split('.')[0].split('_')[0]) + '_' + file.split('.')[0].split('_')[1]
    labels_list = [l for l in glob.glob(label_path + label_search + '*')]
    return labels_list[0]


def create_label_dataframe(label, begin_time, end_time, window_size, timesteps_per_second):
    """Create dataframe, reformated and containing relevant information.
    
    # Arguments
    	label: label path.
	begin_time: start time for the related spectrogram.
	end_time: end time for the related spectrogram.
	window_size: end time - start time.
	timesteps_per_second: spectrogram timesteps / spectrogram window_size.
	
    # Returns
    	Dataframe with relevant label information for 
	the spectrogram file.
    """
    labels_df = pd.read_csv(label,
                            sep='\t',
                            index_col='Selection')
    if 'Label' in labels_df.columns:
        call_labels = ['GIG', 'SQL', 'GRL', 'GRN', 'SQT', 'MOO', 'RUM', 'WHP']
        labels_df.Label = labels_df.Label.str[0:3]
        labels_df = labels_df[labels_df['Label'].isin(call_labels)]  
        labels_df['Begin Time(t)'] = ((labels_df['Begin Time (s)'] - begin_time) * timesteps_per_second).apply(np.floor)
        labels_df['End Time(t)'] = ((labels_df['End Time (s)'] - begin_time) * timesteps_per_second).apply(np.ceil)
        labels_df = labels_df[labels_df['Begin Time (s)'] >= begin_time]
        labels_df = labels_df[labels_df['End Time (s)'] <= end_time] 
    return labels_df


def create_label_matrix(dataframe, timesteps):
    """Create label matrix of shape (number of classes, timesteps).
    
    # Arguments
    	dataframe: dataframe of label information.
	timesteps: number of timesteps.
	
    # Returns
    	Matrix of 0s and 1s. Each column represents a timestep,
	Each row represents a different call type:
	Row 0 = Giggle (GIG)
	Row 1 = Squeal (SQL)
	Row 2 = Growl (GRL)
	Row 3 = Groan (GRN)
	Row 4 = Squitter (SQT)
	Row 5 = Low / Moo (MOO)
	Row 6 = Alarm rumble (RUM)
	Row 7 =  Whoop (WHP)
	
    # Example:
	[[0, 0, 0, 0, 0, 0 ....],
	[0, 0, 0, 0, 0, 0 ....],
	[0, 0, 0, 1, 1, 1 ....], This represents a Growl in timesteps 3, 4, 5.
	[0, 0, 0, 0, 0, 0 ....],
	[0, 0, 0, 0, 0, 0 ....],
	[0, 0, 0, 0, 0, 0 ....],
	[0, 0, 0, 0, 0, 0 ....],
	[1, 1, 1, 1, 0, 0 ....],] This represents a Whoop in timesteps 0, 1, 2, 3.
    """
    label = np.zeros((8, timesteps))
    if 'Label' in list(dataframe):
        # create update list
        update_list = []
        for index, row in dataframe.iterrows():
            update_list.append([row['Begin Time(t)'],
                                row['End Time(t)'],
                                row['Label']])
        # overwrite with ones in correct row based on label
        for l in update_list:
            begin_t = int(l[0])
            end_t = int(l[1])+1
            if l[2] == 'GIG':
                label[0][begin_t:end_t] = 1
            elif l[2] == 'SQL':
                label[1][begin_t:end_t] = 1
            elif l[2] == 'GRL':
                label[2][begin_t:end_t] = 1
            elif l[2] == 'GRN':
                label[3][begin_t:end_t] = 1
            elif l[2] == 'SQT':
                label[4][begin_t:end_t] = 1
            elif l[2] == 'MOO':
                label[5][begin_t:end_t] = 1
            elif l[2] == 'RUM':
                label[6][begin_t:end_t] = 1
            elif l[2] == 'WHP':
                label[7][begin_t:end_t] = 1
    return label


paths = ['cc16_352a_converted/spectro/',
	'cc16_352b_converted/spectro/',
	'cc16_354a_converted/spectro/',
	'cc16_360a_converted/spectro/',
	'cc16_366a_converted/spectro/']

timesteps = 259
window_size = 6

for path in paths:
	for f in os.listdir(path):
	    if 'LABEL' not in f:
	        label = find_label(f, path)
	        begin_time = int(f.split('_')[2].split('sto')[0])
	        end_time = int(f.split('_')[2].split('sto')[1].split('s')[0])
	        timesteps_per_second = timesteps / window_size
	        df = create_label_dataframe(label,
	                                    begin_time,
	                                    end_time,
	                                    window_size,
	                                    timesteps_per_second)
	        label_matrix = create_label_matrix(df, timesteps)
	        np.save(path+f[:-4]+'LABEL', label_matrix)
