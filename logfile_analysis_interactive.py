import file_manipulator
import operations
import json
import os

class Logfile_analyser_interactive:
    """Logfile_analyser class
    This class reads the user input to the log file(s) to be analysed, 
        lets the user select which operations to perform and writes the output to a json file.
    """

    def __init__(self):
        self.file_manipulator = file_manipulator.File_Manipulator()
        
    def read_path_from_user(self):
        """
        Reads the path of the log file(s) from the user input and unzips the file(s) if necessary.
            Then performs the operations on the file(s).
        Returns:
            A JSON file for every logfile with the performed analysis
        """
        input_path = input("Please, enter the input path: ")
        if os.path.isdir(input_path):
            onlyfiles = [f for f in os.listdir(input_path) if 
                os.path.isfile(os.path.join(input_path, f))
                and (os.path.splitext(os.path.join(input_path, f))[1][1:]== "log"
                or f[-7:] == ".log.gz"
                )]
            print("Files in the directory: ")
            print(onlyfiles)    
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
    
            while True:
                answer = input("Do you want to analyse this file? ([y]/n]): ")
                if answer == 'n':
                    print("Ok, let's look at the next file")
                    break
                elif answer in ['y','']:
                    try:
                        self.select_operation(file_path)
                    except FileNotFoundError:
                        print("Wrong input path: file not found")
                    except (ValueError, UnicodeDecodeError):
                        print("Unrecognized log file format")
                    except Exception:
                        print("An unknown error occurred while reading the file. Sorry for that!")
                    break
                print("Sorry, what's your choice?")
        print("No more file to analyse")


    def select_operation(self, file_path):
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
                    "5: Save to JSON and exit\n" \
                    "6: Exit\n"
                    ) )

            # If something else that is not the string
            # version of a number is introduced, the
            # ValueError exception will be called.
            except ValueError:
                print("Error! This is not a number. Try again.\n")

            else:
                if input_operation == 6:
                    print("Thanks, see you next time!")
                    break
                elif input_operation == 5:
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