from distutils import errors
import pandas as pd
pd.set_option("display.max_columns", None) 
# from settings import logfile_column_format
import settings
import json
import zipfile
import gzip
from tempfile import mkdtemp
import os
# from os import listdir
# from os.path import isfile, join, split ,splitext
import subprocess


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

class File_Manipulator:

    def unzip_file(self, file_path):
        subprocess.run("gzip", "-d", "-k", "-c", file_path)
        return file_path[:-4]

    def import_csv_logfile(self, file_path):
        """
        Reads the log file and renames columns.
        Arguments: 
            file_path: string containing the path and name of the log file
        Returns:
            A pandas Dataframe
        """
        df = pd.read_csv(file_path, 
                    delim_whitespace=True, 
                    keep_default_na=False,
                    dtype= str,
                    on_bad_lines='skip') # peformanxe

        # rename columns for common reference
        df.columns = settings.logfile_column_format['names']
        return df

class Logfile_analyzer:

    def __init__(self):
        self.file_manipulator = File_Manipulator()
        
    def read_path_from_user(self):
        """
        Unzips and defines paths of the log files to be analysed.
        Returns:
            A JSON file for every logfile with the operation performed
        """
        # get the path of the log file to analyse
        input_file_path = input("Please, enter the input path: ")
        if input_file_path.split(".")[-1] == "gz":
            input_file_path = self.file_manipulator.unzip_file(input_file_path)
            
        if os.path.splitext(input_file_path)[1][1:]== "log":
            self.select_operation(input_file_path)
        else:
            onlyfiles = [f for f in os.listdir(input_file_path) if 
                os.path.isfile(os.path.join(input_file_path, f))
                and os.path.splitext(os.path.join(input_file_path, f))== "log"]
            for f in onlyfiles:
                file_path = os.path.join(input_file_path, f)
                while True:
                    question = input("Do you want to analyse this file? ([y]/n]), ", file_path)
                    if question == 'n':
                        print("Ok, let's look at the next file")
                        break
                    elif question in ['y','']:
                        self.select_operation(file_path)
                        break
                    print("Sorry, what's your choice?")


    def select_operation(self, file_path):
        """
        Communicates with the user to select input/output paths and the operations to apply on the log file
        Returns:
            A JSON file with the operations performed
        """

        # read and prepare the log file
        df = self.file_manipulator.import_csv_logfile(file_path)
        # create class for the log file
        log_info = Logfile_data_extractor(df)
        # prepare output structure as a dictionary
        my_dict = {"Most_Frequent_IP":[],
            "Least_Frequent_IP":[],
            "Events_per_second":[],
            "Total_bytes_Exchanged":[]
            }
        # possible operations the user can choose
        def cases(i):
            """
            Updates the dictionary with the output of the operation selected
            Arguments:
                i : number selecting the operation
            Returns:
                the function to be applied on the logfile
            """
            switcher={
                    1: lambda : my_dict["Most_Frequent_IP"].extend(log_info.ip_frequency()[0]['Client_IP'].tolist()),
                    2: lambda : my_dict["Least_Frequent_IP"].extend(log_info.ip_frequency()[1]['Client_IP'].tolist()),
                    3: lambda : my_dict["Events_per_second"].append(log_info.events_per_sec()),
                    4: lambda : my_dict["Total_bytes_Exchanged"].append(int(log_info.total_bytes())) # need conversion to int for JSON
                    }
            func=switcher.get(i,lambda :'Invalid')
            return func()
        
        # loop keeps executing until the user selects the "Exit" value
        counter = []
        while True: 
            try:
                input_operation = int(input(
                    "Which operation would you like to do?\n Type one of the following numbers:\n"\
                    "1: Most Frequent IP\n" \
                    "2: Least frequent IP\n" \
                    "3: Events per second\n" \
                    "4: Total amounts of bytes exchanged\n" \
                    "5: Exit\n"
                    ) )

            # If something else that is not the string
            # version of a number is introduced, the
            # ValueError exception will be called.
            except ValueError:
                # The cycle will go on until validation
                print("Error! This is not a number. Try again.\n")

            else:
                if input_operation == 5:
                    output_path = input("Thanks! Please, enter the output path for the JSON file: ")
                    # remove empty keys
                    empty_keys = {k: v for k, v in my_dict.items() if not v}
                    for k in empty_keys:
                        del my_dict[k]
                    json_object = json.dumps(my_dict, indent= 4)
                    with open(output_path, mode='w') as outfile:
                        outfile.write(json_object)
                    break
                elif input_operation < 5:
                    if input_operation not in counter:
                        counter.append(input_operation)
                        print("Ok, we will add this to the JSON file!\n")
                        cases(input_operation)
                        print(my_dict)
                    else:
                        print("You have already selected this operation. Please try another one. \n")
                else: 
                    print("There is no operation available with this number! Try again.\n")


if __name__ == '__main__':
    logfile = Logfile_analyzer()
    logfile.read_path_from_user()

