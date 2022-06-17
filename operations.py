import pandas as pd

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
        tuple of two pandas dataframes, with the most and least frequent IP addresses together with their counts.
    """
    # check these are IP addresses
    check_ip = self.df['Client_IP'].str.split('.').apply(len).unique()
    if len(check_ip) != 1 or check_ip != 4:
        print("Warning: These seem not to be IP addresses, please check your format with the settings")  
         
    ip_freq = self.df['Client_IP'].value_counts().rename_axis('Client_IP').reset_index(name='counts') # drops Nan by default
    # In the sample file, the most frequent ip address is the local host
    # if this is not what we are interested in, we can filter it out
    # but then the log file will shrink significantly
    most_freq_ip = ip_freq.loc[ip_freq['counts'] == ip_freq['counts'].max()]
    least_freq_ip = ip_freq.loc[ip_freq['counts'] == ip_freq['counts'].min()]
    return most_freq_ip, least_freq_ip

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
        print("Warning: More than 20% of the rows have Nan in the Timestamp column.") 
    # time span of the log file
    time_span = self.df['Timestamp'].iloc[-1] - self.df['Timestamp'].iloc[0]
    # compute the events per seconds as total number of rows divided by the time span
    return self.df.shape[0] / time_span

   
  def total_bytes(self):
    """
    Computes the total bytes exchanged
    Returns:
        number of bytes 
    """
    # convert fields to numeric
    self.df[["Response_header_size_bytes","Response_size_bytes"]] = self.df[[
        "Response_header_size_bytes","Response_size_bytes"]].apply(pd.to_numeric, errors = 'coerce')
    return self.df["Response_header_size_bytes"].sum() + self.df["Response_size_bytes"].sum() # skipna is True by default
