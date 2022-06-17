import file_manipulator
import operations
import json
import os

class Logfile_analyser:
    """Logfile_analyser class
    This class reads the user input to the log file(s) to be analysed, 
        lets the user select which operations to perform and writes the output to a json file.
    """

    def __init__(self):
        self.file_manipulator = file_manipulator.File_Manipulator()
        self.info_data_dict = {}
        
    def analyse_folder(self, input_path):
        """
        Reads the path of the log file(s) from the user input and unzips the file(s) if necessary.
            Then performs the operations on the file(s).
        Returns:
            A JSON file for all logfiles with the performed analysis
        """
        if os.path.isdir(input_path):
            onlyfiles = [f for f in os.listdir(input_path) if 
                os.path.isfile(os.path.join(input_path, f))
                and (os.path.splitext(os.path.join(input_path, f))[1][1:]== "log"
                or f[-7:] == ".log.gz"
                )]
            file_paths = [os.path.join(input_path, f) for f in onlyfiles]
        else:
            file_paths = [input_path]   

        for file_path in file_paths:
            print(f"File selected: '{file_path}'")
            if file_path.split(".")[-1] == "gz":
                try:
                    file_path = self.file_manipulator.unzip_file(file_path)
                except FileNotFoundError:
                    print(f"The file '{file_path}' is not in gzip format. Skipping.")
                    continue
            try:
                file_dict = self.execute_operations(file_path)
            except FileNotFoundError:
                print("Wrong input path: file not found")
            except (ValueError, UnicodeDecodeError):
                print("Unrecognized log file format")
            except Exception:
                print("An unknown error occurred while reading the file. Sorry for that!")
            else:
                self.info_data_dict.update(file_dict)
        print("No more files to analyse")
        
       

    def execute_operations(self, file_path):
        """
        Selects the operations to apply on the log file and writes the output file
        Arguments:
            file_path: path to the log file to be analysed
        Returns:
            A JSON file with the performed operations
        """
        df = self.file_manipulator.import_csv_logfile(file_path)
        log_info = operations.Logfile_data_extractor(df)
        # prepare output structure as a dictionary
        file_dict = {"Most_Frequent_IP": log_info.ip_frequency()[0]['Client_IP'].tolist(),
            "Least_Frequent_IP": log_info.ip_frequency()[1]['Client_IP'].tolist(),
            "Events_per_second":[log_info.events_per_sec()],
            "Total_bytes_Exchanged":[int(log_info.total_bytes())]# need conversion to int for JSON
            }
        return {file_path : file_dict}
        
    def export_data_to_json(self, output_path):
        """
        Exports the dictionary with logfile info to a JSON file.
        Arguments:
            output_path: path to the JSON file
        """
        json_object = json.dumps(self.info_data_dict, indent= len(self.info_data_dict))
        with open(output_path, mode='w') as outfile:
            outfile.write(json_object)
