/**
 * Java Image Science Toolkit (JIST)
 *
 * Image Analysis and Communications Laboratory &
 * Laboratory for Medical Image Computing &
 * The Johns Hopkins University
 * 
 * http://www.nitrc.org/projects/jist/
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or (at
 * your option) any later version.  The license is available for reading at:
 * http://www.gnu.org/copyleft/lgpl.html
 *
 */
package edu.jhu.ece.iacl.jist.pipeline;

import edu.jhu.ece.iacl.jist.io.MipavController;
import edu.jhu.ece.iacl.jist.pipeline.parameter.InvalidParameterException;
import edu.jhu.ece.iacl.jist.pipeline.parameter.JISTInternalParam;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamCollection;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamHeader;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamInformation;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamModel;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamPerformance;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamVolumeCollection;
import edu.jhu.ece.iacl.jist.pipeline.view.input.Refresher;
import edu.jhu.ece.iacl.jist.utility.JistLogger;
import gov.nih.mipav.model.algorithms.AlgorithmBase;
import gov.nih.mipav.view.MipavUtil;

import java.awt.Dimension;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;

import javax.xml.namespace.QName;

import org.apache.axis2.AxisFault;
import org.apache.axis2.addressing.EndpointReference;
import org.apache.axis2.client.Options;
import org.apache.axis2.rpc.client.RPCServiceClient;

// TODO: Auto-generated Javadoc
/**
 * Processing Algorithm for MAPS. This class should be extended for each
 * particular algorithm implementation. Methods createInputParameters(),
 * createOutputParameters() and execute() should be overridden for each
 * algorithm. createInputParameters() and createOutputParameters() are executed
 * in the default constructor for ProcessingAlgorithm. execute() is executed
 * after the user presses "OK" and all the input parameters validate.
 * 
 * @author Blake Lucas
 */
public abstract class ProcessingAlgorithm extends AlgorithmBase {
	
	/** The Constant MAPS version. */
	public static final float JIST_VERSION = JistPreferences.JIST_VERSION_ID;
	
	/** The input parameters. */
	protected ParamCollection inputParams;
	
	/** The output parameters. */
	protected ParamCollection outputParams;
	
	/** Algorithm performance information. */
	protected ParamPerformance performance;
	
	/** Preferred dimensions for the algorithm dialog. */
	private Dimension dimension;
	
	/** Necessary for accessing current CPU time. */
	private ThreadMXBean tb;
	
	/** Output directory for algorithm. */
	private File outputDir;
	
	/** Output meta file for algorithm. */
	private File outputMetaFile;
	
	/** Module definition file for algorithm. */
	private File mapFile;
	
	/** Algorithm information associated with all algorithms. */
	protected AlgorithmInformation algorithmInformation;	
	
	/** Run in separate process. */
	protected boolean runningInSeparateProcess=true;
	
	/** Hypervisor IP */
	protected String hypervisorIP;
	
	/** Default JVM Arguments --- currently only the Sun VM is supported **/  
	public String[] getDefaultJVMArgs() {
		return new String[]{};
	}
	
	/**
	 * Constructor creates input and output parameters and assigns the title of
	 * this algorithm to be the label for the input parameters.
	 */
	public ProcessingAlgorithm() {
		dimension = null;
		tb = ManagementFactory.getThreadMXBean();
		inputParams = new ParamCollection();
		// Add header to algorithm
		inputParams.add(new ParamHeader("Algorithm", this.getClass()));
		// Add information to algorithm
		inputParams.add(new ParamInformation(algorithmInformation = new AlgorithmInformation(this)));
		createInputParameters(inputParams);
		outputParams = new ParamCollection();
		outputParams.add(new ParamHeader("Algorithm", this.getClass()));
		//Create output parameters
		createOutputParameters(outputParams);
		outputParams.setLabel(inputParams.getLabel());
		outputParams.setName(inputParams.getName());
		outputParams.add(performance = new ParamPerformance("Execution Time"));
		algorithmInformation.init(this);
		
		/*in case it is not overwritten elsewhere*/
		outputMetaFile = new File(outputDir, "output.xml");
		hypervisorIP = JistPreferences.getPreferences().getHypervisorIP();
	}

	/**
	 * Create input parameters.
	 * 
	 * @param inputParams the input parameters
	 */
	protected abstract void createInputParameters(ParamCollection inputParams);

	/**
	 * Create output parameters.
	 * 
	 * @param outputParams the output parameters
	 */
	protected abstract void createOutputParameters(ParamCollection outputParams);

	/**
	 * Execute your algorithm.
	 * 
	 * @param monitor progress monitor
	 * 
	 * @throws AlgorithmRuntimeException the algorithm runtime exception
	 */
	protected abstract void execute(CalculationMonitor monitor) throws AlgorithmRuntimeException;

	/**
	 * Location of file that describes the algorithm.
	 * 
	 * @return the about file
	 */
	public File getAboutFile() {
		return new File("");/*edu/jhu/ece/iacl/docs/about.html");*/ //FIXME Remove static reference- dead link?
	}

	/**
	 * Get algorithm information for this algorithm.
	 * 
	 * @return algorithm information
	 */
	public AlgorithmInformation getAlgorithmInformation() {
		return algorithmInformation;
	}

	/**
	 * Get algorithm label from input parameters.
	 * 
	 * @return algorithm label
	 */
	public String getAlgorithmLabel() {
		return inputParams.getLabel();
	}

	/**
	 * Get algorithm name from input parameters.
	 * 
	 * @return algorithm name
	 */
	public String getAlgorithmName() {
		return inputParams.getName();
	}

	/**
	 * Get input parameters.
	 * 
	 * @return input parameters
	 */
	public ParamCollection getInput() {
		return inputParams;
	}

	/**
	 * Get module definition file.
	 * 
	 * @return module file
	 */
	public File getMapFile() {
		return mapFile;
	}

	/**
	 * Get output parameters.
	 * 
	 * @return output parameters
	 */
	public ParamCollection getOutput() {
		return outputParams;
	}
	
	public ParamCollection getOutputPluginSpecific() {
		ParamCollection out = new ParamCollection();
		for(ParamModel p : outputParams.getChildren()) {
			if(p.getClass()==ParamPerformance.class)
				continue;
			out.add(p);
		}
		return out;
	}

	/**
	 * Get output directory.
	 * 
	 * @return output directory
	 */
	public File getOutputDirectory() {
		return outputDir;
	}

	/**
	 * Get preferred size for algorithm The default is null.
	 * 
	 * @return preferred dimension
	 */
	public Dimension getPreferredSize() {
		return dimension;
	}

	/**
	 * Get cpu timestamp for this thread in msec.
	 * 
	 * @return the time stamp
	 */
	public long getTimeStamp() {
		return tb.getCurrentThreadCpuTime() / 1000000;
	}

	/**
	 * Location of file that describes how to use the algorithm.
	 * 
	 * @return the usage file
	 */
	public File getUsageFile() {
		return null;
	}

	/**
	 * Initialize parameters and algorithm.
	 * 
	 * @param pipeFile the pipe file
	 */
	public void init(File pipeFile) {
	}

	/**
	 * Initialize parameters and algorithm.
	 * 
	 * @param pipe the pipe
	 */
	public void init(PipeAlgorithm pipe) {
	}

	/**
	 * Load input parameters from file and execute algorithm.
	 * 
	 * @param f input parameter file
	 * 
	 * @return true if algorithm executed
	 */
	public boolean load(File f) {
		return inputParams.read(f);
	}

	/**
	 * Run algorithm with new calculation monitor.
	 */
	public void runAlgorithm() {
		runAlgorithm(new CalculationMonitor(this, getProgressChangeListener()));
	}

	/**
	 * Run algorithm with calculation monitor.
	 * 
	 * @param monitor calculation monitor
	 * 
	 * @return true if algorithm successful
	 */
	public boolean runAlgorithm(CalculationMonitor monitor) {
		
		setCompleted(false);
		setStartTime();
		boolean exceptionThrown=false;
		try {
			execute(monitor);
		} catch(Exception e){
			JistLogger.logError(JistLogger.SEVERE,"Module Failed in an Ungraceful Manner. Please contact the developer with the following message.");
			JistLogger.logError(JistLogger.SEVERE,getClass().getCanonicalName()+"Runtime Exception:" +e.getMessage());
			StackTraceElement []el = e.getStackTrace();
			for (StackTraceElement  m : el)
				JistLogger.logError(JistLogger.SEVERE,m.toString());
			exceptionThrown=true;
//			if (!MipavController.isQuiet()) {
//				MipavUtil.displayError("Runtime Exception:" + e.getMessage());
//			}			
		}
		monitor.stop();
		performance.setValue(monitor.getPerformance().clone());
		computeElapsedTime();
		Refresher.getInstance().stop();
		if(exceptionThrown){
			setCompleted(false);
		} else {
			// Validate the output upon completion
			try {
				outputParams.validate();
				setCompleted(true);
				if(JistPreferences.getPreferences().isUseHypervisor() 
						&& !hypervisorIP.equalsIgnoreCase("none")){
					sendSummaryToHypervisor();
				}
				return true;
			} catch (InvalidParameterException e) {
				System.err.println(getClass().getCanonicalName()+e.getMessage());
				System.err.flush();
				if (!MipavController.isQuiet()) {
					MipavUtil.displayError(e.getMessage());
				}
			}
		}
		return false;
	}

	/**
	 * Set input parameters.
	 * 
	 * @param inputParams input parameters
	 */
	public void setInput(ParamCollection inputParams) {
		this.inputParams = inputParams;
	}

	/**
	 * Set module definition file.
	 * 
	 * @param mapFile module file
	 */
	public void setMapFile(File mapFile) {
		this.mapFile = mapFile;
	}

	/**
	 * Set output parameters.
	 * 
	 * @param outputParams output parameters
	 */
	public void setOutput(ParamCollection outputParams) {
		this.outputParams = outputParams;
	}

	/**
	 * Set output directory.
	 * 
	 * @param outputDir output directory
	 */
	public void setOutputDirectory(File outputDir) {
		this.outputDir = outputDir;
	}

	/**
	 * Get preferred size for algorithm The default is null.
	 * 
	 * @param d the dimension
	 * 
	 * @return preferred dimension
	 */
	public void setPreferredSize(Dimension d) {
		this.dimension = d;
	}

	/**
	 * Checks if is running in separate process.
	 * 
	 * @return the runninInSeperateProcess
	 */
	public boolean isRunningInSeparateProcess() {
		return runningInSeparateProcess;
	}

	/**
	 * Sets the running in separate process.
	 * 
	 * @param runningInSeperateProcess the runInSeperateProcess to set
	 */
	public void setRunningInSeparateProcess(boolean runningInSeperateProcess) {
		this.runningInSeparateProcess = runningInSeperateProcess;
	}

	public void setOutputMetaFile(File file) {
		outputMetaFile = file;
		
	}

	public void saveResources(boolean overrideSubdirectories) {
		outputParams.saveResources(getOutputDirectory(),overrideSubdirectories);		
	}
	
	public void sendSummaryToHypervisor() {
		String hypervisorIP = JistPreferences.getPreferences().getHypervisorIP();
		boolean useHypervisor = JistPreferences.getPreferences().isUseHypervisor();
		try {
			writeSummaryFile();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		if(useHypervisor && !hypervisorIP.equalsIgnoreCase("none")){
			RPCServiceClient serviceClient;
			try {
				saveResources(true);
				
				String output = "";
				BufferedReader read = new BufferedReader(new InputStreamReader(new FileInputStream(outputMetaFile)));
				while (true)
	            {
					String line = read.readLine();
	                if (line == null)
	                {
	                    break;
	                }
	                output = output.concat(line);
	            }
				
				output = output.substring(output.indexOf("<"), output.lastIndexOf(">")+1);
				System.out.println(output);
				
				serviceClient = new RPCServiceClient();
				Options options = serviceClient.getOptions();
				
				EndpointReference targetEPR = new EndpointReference("http://" + hypervisorIP + "/axis2/services/Hyperadvisor");	
		        options.setTo(targetEPR);   
		        
				QName opDiscover = new QName("http://ws.apache.org/axis2", "aggregator");	
		        Object[] opGetDiscoverArgs = new Object[] {outputParams.getChildren().get(0).toString(), output};
		        Class[] returnTypes = new Class[] { Boolean.class};	            
		        Object [] response =  serviceClient.invokeBlocking(opDiscover, opGetDiscoverArgs, returnTypes);
			} catch (AxisFault e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	
	public void writeSummaryFile() throws IOException {

		FileWriter outFp =new FileWriter(outputMetaFile); 
		for(int i=0;i<outputParams.size();i++) 
		{
			ParamModel output = outputParams.getValue(i);
			if(!output.isHidden() && !(output instanceof JISTInternalParam)) {
				
				String tag = output.getCliTag();
				try {
					if(output instanceof ParamVolumeCollection){
						output.writeAndFreeNow(this);
					}
					outFp.append(tag + "=" + output.getXMLValue()+"\n");
				} catch(Exception e) {
					e.printStackTrace();
					
					outFp.append(tag + "=" +
							"UNABLE TO REALIZE VARIABLE"+
							output.getLabel()+"\n");
					
					
				}
			}
		}
		outFp.close();
	}

	public String reconcileAndMerge(ParamCollection inputParams2,
			ParamCollection outputParams2) throws InvalidJistMergeException{
		String message="";
		message = message+reconcileParameters(inputParams,inputParams2);
		message = message+reconcileParameters(outputParams,outputParams2);
		return message;
	}
	
	public String  reconcileParameters(ParamCollection paramDest,
			ParamCollection paramSource) {
		String msg = "";
		for(ParamModel p_src : paramSource.getChildren()) {
			if(p_src==null)
				continue;
			for(ParamModel p_dest : paramDest.getChildren()) {
				if(p_dest==null)
					continue;	
				if(p_src.getLabel().equals(p_dest.getLabel())) { // these parameters match!
					if(p_src instanceof ParamHeader) { 
						if(p_dest instanceof ParamHeader) {														
							((ParamHeader) p_dest).setUUID(((ParamHeader) p_src).getUUID());
						} else {
							msg+="Incompatible parameter types for matched parameters: "+p_src.getLabel()+"\n";
						}
					}
					else if(p_src instanceof ParamCollection) {
						if(p_dest instanceof ParamCollection) {	
							msg+=reconcileParameters((ParamCollection)p_dest,(ParamCollection)p_src);
						} else {
							msg+="Incompatible parameter types for matched parameters: "+p_src.getLabel()+"\n";
						}
					} else try { 
//						msg+="Matched: "+p_src.getLabel()+"\n";
						p_dest.setValue(p_src.getValue());
					} catch(Exception e) {
						msg+="Incompatible parameter values for matched parameters: "+p_src.getLabel()+"\n";
					}
				}
			}		
		}
		return msg;
	}
	
}
