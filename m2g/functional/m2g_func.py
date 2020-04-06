import subprocess
import yaml
from m2g.utils.gen_utils import run

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

    Data = [{
        'subject_id': sub,
        'unique_id': f'ses-{ses}',
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
    }]
    
    config_file = f'{input_dir}/data_config.yaml'
    with open(config_file,'w',encoding='utf8') as outfile:
        yaml.dump(Data, outfile, default_flow_style=False)
    
    
    #try:
    #    with open('/input/data_config.yaml', 'r') as f:
    #        config_data = yaml.load(f)
    #        return config_data
    #except IOError:
    #    print("Error! Could not find config file {0}".format(config_filename))
    #    raise
    return config_file
    

def make_script(input_dir, output_dir, subject, session, data_config, pipeline_config):
    cpac_script = '/root/.m2g/cpac_script.sh'
    with open(cpac_script,'w+',encoding='utf8') as script:
        script.write(f'''#! /bin/bash
        . /venv/bin/activate
        python /code/run.py --data_config_file {data_config} --pipeline_file {pipeline_config} --mem_gb 24 {input_dir} {output_dir} participant
        ''')
    
    run(f'chmod +x {cpac_script}')

    return cpac_script



def m2g_func_worker(input_dir, output_dir, sub, ses, anat, bold, acquisition, tr):
    """[summary]
    
    Arguments:
        input_dir {[type]} -- [description]
        output_dir {[type]} -- [description]
        sub {[type]} -- [description]
        ses {[type]} -- [description]
        anat {[type]} -- [description]
        bold {[type]} -- [description]
        acquisition {[type]} -- [description]
        tr {[type]} -- [description]
    """
    
    pipeline_config='/m2g/m2g/functional/m2g_pipeline.yaml'
    
    data_config = make_dataconfig(input_dir, sub, ses, anat, bold, acquisition, tr)
    cpac_script = make_script(input_dir, output_dir, sub, ses, data_config, pipeline_config)
    
    # Run pipeline
    subprocess.call([cpac_script], shell=True)
