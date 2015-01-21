package edu.jhu.ece.iacl.jist.cli;

import java.io.File;

import org.apache.commons.cli.ParseException;

import java.net.URI;

import edu.jhu.ece.iacl.jist.io.ImageDataReaderWriter;
import edu.jhu.ece.iacl.jist.io.MipavController;
import edu.jhu.ece.iacl.jist.pipeline.JistPreferences;
import edu.jhu.ece.iacl.jist.pipeline.PipeLibrary;
import edu.jhu.ece.iacl.jist.pipeline.ProcessingAlgorithm;
import edu.jhu.ece.iacl.jist.pipeline.ProcessingApplication;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamCollection;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamModel;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamVolume;
import edu.jhu.ece.iacl.jist.pipeline.parameter.ParamVolumeCollection;

public class run {

	public static ProcessingAlgorithm getProcessingAlgorithmByClass(String classname) {
		try {
			try{
				PipeLibrary.getInstance().loadLibraryPath(true);
				if(!PipeLibrary.getInstance().getLibraryPath().exists())
					PipeLibrary.getInstance().setLibraryPath(new File("."));
			}catch (Exception e){
				PipeLibrary.getInstance().setLibraryPath(new File("."));
			}
			return (ProcessingAlgorithm)Class.forName(classname).getConstructor().newInstance();
		}
		catch (Exception e) {
			
			throw new RuntimeException("Invalid ProcessingAlgorithm: "+classname+"\n"+e.getMessage());
		}
	}
	static String _OutputFile;
	public static String getOutputFile(){
		return _OutputFile;
	}
	
	public static void main(String []args) {
		_OutputFile = null;
		String moduleClass = args[0];
		try { 
			ProcessingAlgorithm module = getProcessingAlgorithmByClass(moduleClass);
			JistCLI cli = new JistCLI(module);
			try {
				cli.parse(args);
		
			} catch (ParseException e) {

				System.out.println("cli"+"\t"+"####################################################################");
				System.out.println("cli"+"\t"+"Parse error: "+e.getMessage() + "success");
				System.out.println("cli"+"\t"+"####################################################################");
				if(cli.showHelp()) {
					System.out.println("cli"+"\t"+cli.getHumanReadableHelpMessage() + "help");
					if(args.length<=2)
						System.exit(0);
				}
				System.exit(-1);
			}

			if(cli.showHelp()) {
				System.out.println("cli"+"\t"+cli.getHumanReadableHelpMessage() + "showhelp");
				if(args.length<=2)
					System.exit(0);
			}

			if(cli.checkSlicerXMLoption()) {
				System.out.println(cli.getSlicerXML() + "XML");
				if(args.length<=2)
					System.exit(0);
			}

			System.out.println("cli"+"\t"+"####################################################################");
			System.out.println("cli"+"\t"+"Initializing MIPAV/JIST Framework");
			// Hide Mipav GUI
			MipavController.setQuiet(true);
			
			MipavController.init();
			// Use Default Preference
			//JistPreferences.setPreferences(new JistPreferences());
			// Load Preference(needs JIST layout to be run first to build the library) not a great choice
			//PipeLibrary.getInstance().loadPreferences(true);

			System.out.println("cli"+"\t"+"####################################################################");
			System.out.println("cli"+"\t"+"Interpretting command line arguments");
			cli.unmarshal();
			ProcessingAlgorithm algo = cli.getModule();			
			System.out.println("cli"+"\t"+"####################################################################");
			System.out.print(cli.getParseStatus());
			System.out.println("cli"+"\t"+"####################################################################");
			if(cli.encounteredParseError()) {
				System.out.println("cli"+"\t"+"Exiting with errors.");
				System.exit(-1);
			}

			ProcessingApplication plug = new ProcessingApplication(algo);
			ParamCollection plugOutputs = plug.getAlgorithm().getOutput();
			//plug.runInProcess();
			plugOutputs.setLoadAndSaveOnValidate(false);
			plug.getAlgorithm().runAlgorithm();
			


			ImageDataReaderWriter rw  = ImageDataReaderWriter.getInstance();
//			rw.getExtensionFilter().setPreferredExtension(".nrrd");
			boolean wroteOne = false;
			//check if only single outputs are called
			for(int i=0; i < plugOutputs.size(); i++){
				ParamModel outI = plugOutputs.getValue(i);
				String outITag = outI.getCliTag();
				if(outITag != null){
					String newName = cli.cliCommand.getOptionValue(outITag);
					
					System.out.println("\n\nnewName: " + newName+"\n\n");
					if(newName !=null){
						if(outI instanceof ParamVolume){
							File path = new File(newName);
							path.createNewFile();
							ParamVolume outVol = (ParamVolume)outI;
							if(path.isAbsolute()){
								rw.write(outVol.getImageData(), path);
							} else {
								System.out.format("Argument for "+outITag+" Absolute path required for output files.\n");
								//outVol.getImageData().setName(newName);
								//outVol.setLoadAndSaveOnValidate(false);
								//outVol.writeAndFreeNow(plug.getAlgorithm());
							}
							wroteOne = true;
						}else if(outI instanceof ParamVolumeCollection){
							int numvols = ((ParamVolumeCollection) outI).getParamVolumeList().size();
							String[] newNameList = newName.split(";");
							if(newNameList.length != numvols){
								System.err.format("Argument for "+outITag+" Absolute path required for output files.\n");
							}else{
								for(int k=0; k<numvols; k++){
									File path = new File(newName);
									path.createNewFile();
									ParamVolume outVol = ((ParamVolumeCollection) outI).getParamVolumeList().get(k);
									if(path.isAbsolute()){
										rw.write(outVol.getImageData(), path);
									} else {
										System.out.format("Argument for "+outITag+" Absolute path required for output files.\n");
										
									}
									wroteOne = true;
								}
							}
							
						}
					}
				}
			}	
			 /////////////////test///////////////
//			File outputfile = new File ("d:\\run");
//			outputfile.mkdir();
//			plugOutputs.getFactory().saveResources(outputfile, true);
//			_OutputFile = cli.getOutFile().getAbsolutePath() ;
					
			///////////end////////////////////////

			//write all if no output flags were called
			if(!wroteOne){
				plugOutputs.setLoadAndSaveOnValidate(true);
				plug.getAlgorithm().saveResources(true);
				plug.getAlgorithm().writeSummaryFile();
			}

			//plugOutputs.setLoadAndSaveOnValidate(true);
			//plug.getAlgorithm().saveResources(true);
			//System.out.format(JistPreferences.getPreferences().getPreferredExtension()+"\n");
			System.out.println("cli"+"\t"+"####################################################################");
			System.out.println("cli"+"\t"+"Done: "+moduleClass);
			System.out.println("cli"+"\t"+"####################################################################");

			// Shouldn't be need, but MIPAV's internal threads appear to continue to run.
			System.exit(0);  //delete exit here because runTest want to test the output file
			// 


		} catch (Exception e) {
			System.out.println("cli"+"\t"+"Usage: edu.jhu.ece.iacl.jist.cli.run [classname] -help");
			System.out.println("cli"+"\t"+"Usage: edu.jhu.ece.iacl.jist.cli.run [classname] [run options]");
			System.out.println("cli"+"\t"+"PARSE Error: "+e.getMessage());
			e.printStackTrace();
			System.exit(-1);
		}
	}


}
