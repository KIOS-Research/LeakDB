function [filepaths,file_charpaths, zipFile, streamCopier] = getPathsZip(zipFilename)

    zipJavaFile = java.io.File(zipFilename);
    zipFile=org.apache.tools.zip.ZipFile(zipJavaFile);
    entries=zipFile.getEntries;
    streamCopier = com.mathworks.mlwidgets.io.InterruptibleStreamCopier.getInterruptibleStreamCopier;

    i=1;
    filepaths = {};
    file_charpaths ={};
    while entries.hasMoreElements
        disp(['Get paths from zip ', num2str(i)])
        tempObj=entries.nextElement;
        try
            filepaths{i}=tempObj;
            file_charpaths{i}=tempObj.getName.toCharArray';
        catch 
            continue
        end
        i=i+1;
    end
    
end