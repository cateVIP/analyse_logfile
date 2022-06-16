import pandas as pd
from distutils import errors

class Logfile_data_extractor:
  """Logfile_data_extractor class
    This class contains the operations to perform on the logfile.
  """
  def __init__(self, df):
      self.df = df

  def ip_frequency(self):
    """
    Computes the most and lest frequent IP addresses in the log file.
    Returns:
        tuple of two dataframes, with the most and least IP addresses together with their counts.
    """
    ip_freq = self.df['Client_IP'].value_counts().rename_axis('Client_IP').reset_index(name='counts') # drops Nas by default
    max_value = ip_freq.loc[ip_freq['counts'] == ip_freq['counts'].max()]
    min_value = ip_freq.loc[ip_freq['counts'] == ip_freq['counts'].min()]
    return max_value, min_value

  def events_per_sec(self):
    """
    Computes the events per seconds of the log file.
    Returns:
        Number of events per second
    """
    # convert the field to numeric: number of seconds
    self.df['Timestamp'] = pd.to_numeric(self.df['Timestamp'],  errors='coerce')
    # sort data as it is not time ordered
    self.df.sort_values('Timestamp', inplace = True)
    nrows1 = self.df.shape[0]
    self.df.dropna(subset=['Timestamp'], inplace =True) # once sorted, the Nas will be at the end of the dataframe (by Timestamp)
    if (nrows1 - self.df.shape[0])/nrows1*100 < 80:
        print("More than 20% of the rowns have Nas in the Timestamp column.") 
    # time span of the log file
    time_span = self.df['Timestamp'].iloc[-1] - self.df['Timestamp'].iloc[0]
    # compute the events per seconds as total number of rows divided by the time span
    return self.df.shape[0] / time_span

   
  def total_bytes(self):
    """
    Compute the total bytes exchanged
    Returns:
        number of bytes 
    """
    # convert fields to numeric
    self.df[["Response_header_size_bytes","Response_size_bytes"]] = self.df[[
        "Response_header_size_bytes","Response_size_bytes"]].apply(pd.to_numeric, errors = 'coerce')
    return self.df["Response_header_size_bytes"].sum() + self.df["Response_size_bytes"].sum() # skipna is True by default
