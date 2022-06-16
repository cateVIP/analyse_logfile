import pandas as pd
from distutils import errors


class Logfile_data_extractor:
  """Logfile class
    This class extracts few info on the logfile.
  """
  def __init__(self, df):
      self.df = df

  def ip_frequency(self):
    """
    Computes the most and lest frequent IP addresses in the log file.
    Returns:
        tuple of two dataframes, with the most and least IP addresses together with their counts.
    """
    ip_freq = self.df['Client_IP'].value_counts().rename_axis('Client_IP').reset_index(name='counts')
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
    self.df= self.df.sort_values('Timestamp')
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
    #compute total bytes
    return self.df["Response_header_size_bytes"].sum() + self.df["Response_size_bytes"].sum()
