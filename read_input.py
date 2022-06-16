import subprocess
import pandas as pd
import settings

class File_Manipulator:

    def unzip_file(self, file_path):
        subprocess.run(["gzip", "-d", "-k", file_path])
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
                    dtype= str,
                    on_bad_lines='skip') # peformanxe

        # rename columns for common reference
        df.columns = settings.logfile_column_format['names']
        return df