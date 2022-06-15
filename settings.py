'''This file contains the settings to be able to read the log file.'''
import numpy as np

logfile_column_format = {
    'names': [
        'Timestamp',
        'Response_header_size_bytes',
        'Client_IP',
        'HTTP_response_code',
        'Response_size_bytes',
        'HTTP_request_method',
        'URL',
        'Username',
        'Type_of_access_destination_IP',
        'Response_type'
    ],
    'types': [float, 
        int, 
        str,
        str,
        int,
        str,
        str,
        str,
        str,
        str
    ],
}