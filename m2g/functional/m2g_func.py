import subprocess
import yaml

def make_dataconfig(input_dir, sub, ses, anat, func, acquisition='alt+z', tr=2.0):
    """Generates the data_config file needed by cpac
    
    Arguments:
        input_dir {str} -- Path of directory containing input files
        sub {int} -- subject number
        ses {int} -- session number
        anat {str} -- Path of anatomical nifti file
        func {str} -- Path of functional nifti file
        acquisition {str} -- acquisition method for funcitonal scan
        tr {float} -- TR (seconds) of functional scan
    
    Returns:
        None
    """

    Data = {
        '-': {
            'subject_id': sub,
            'unique_id': ses,
            'anat': anat,
            'func': {
                'rest_run-1': {
			        'scan': func,
			        'scan_parameters': {
				    	'acquisition': acquisition,
				    	'tr': tr
				    }
			    }
		    }
	    }
    }
    

    with open('/input/data_config.yaml','w',encoding='utf8') as outfile:
        yaml.dump(Data, outfile, default_flow_style=False)
    
    
    #try:
    #    with open('/input/data_config.yaml', 'r') as f:
    #        config_data = yaml.load(f)
    #        return config_data
    #except IOError:
    #    print("Error! Could not find config file {0}".format(config_filename))
    #    raise
    
make_dataconfig('/input/', 111, 1, 'alt+z', '2.0')

def update_pipeline():
    print('test')

def make_script(input_dir, output_dir):
    #with open('/.m2g/cpac_script.sh','w',encoding='utf8') as script:
        #script.write(f'''
        #    #! /bin/bash
        #    . /venv/bin/activate
        #    python /code/run.py --data_config_file {input_dir}/data_config.yaml --pipeline_file {} {input_dir} {output_dir} participant
        #    ''')
    print('whatever')

def run_cpac():
    subprocess.call(['/.m2g/cpac_script.sh'])


def m2g_func_worker(input_dir, output_dir, sub, ses, anat, bold, acquisition, tr):
    make_dataconfig()
    update_pipeline()
    make_script()
    run_cpac()
