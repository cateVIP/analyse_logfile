import subprocess
import pandas as pd
import settings

class File_Manipulator:
    """File_Manipulator class
    This class prepares the logfiles to be analysed, first unzipping the files if necessary, then converting thme to a pandas Dataframe.
    """
    def unzip_file(self, file_path):
        """
        Unzip gz files.
        Arguments:
            file_path: path of the .gz file
        Returns:
            the path of the unzipped file
        """
        subprocess.run(["gzip", "-d", "-k",file_path])
        return file_path[:-3]

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
                    dtype= str,            # to avoid issues with IP addresses   
                    on_bad_lines='skip')   # only 2 lines over more than 1M got skipped in the example case (less than 1e-4%) and the integrity of the other rows is preserved

        # rename columns for common reference
        df.columns = settings.logfile_column_format['names']
        return df