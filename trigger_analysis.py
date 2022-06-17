import logfile_analysis


import sys, getopt

def main(argv):
    inputfile = ''
    outputfile = ''

    def fail():
        print('This tool must be run with options.\n' \
        'Commad line options are: -i <inputfile> -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        fail()
    if args or len(opts) != 2:
        fail()
    for opt, arg in opts:
        if opt == '-h':
            print('my_python_script.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    return inputfile, outputfile

if __name__ == "__main__":
    inputfile, outputfile = main(sys.argv[1:])
    log_analyser = logfile_analysis.Logfile_analyser()
    log_analyser.analyse_folder(inputfile)
    log_analyser.export_data_to_json(outputfile)


    