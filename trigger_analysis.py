import logfile_analysis


import sys, getopt

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('Please run as my_python_script.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('my_python_script.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    return(inputfile, outputfile)

if __name__ == "__main__":
    io_paths = main(sys.argv[1:])
    log_analyser = logfile_analysis.Logfile_analyser()
    log_analyser.analyse_folder(io_paths[0])
    log_analyser.export_data_to_json(io_paths[1])


    