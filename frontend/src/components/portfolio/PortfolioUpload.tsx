import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService } from '../../services/api';
import { Portfolio, ApiError } from '../../types/portfolio';

interface PortfolioUploadProps {
  onUploadSuccess: (portfolio: Portfolio) => void;
  onUploadError: (error: string) => void;
}

const PortfolioUpload: React.FC<PortfolioUploadProps> = ({ 
  onUploadSuccess, 
  onUploadError 
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      onUploadError('Please upload a CSV file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 100);

      const response = await apiService.uploadPortfolio(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.success && response.portfolio) {
        onUploadSuccess(response.portfolio);
      } else {
        onUploadError(response.message || 'Upload failed');
      }
    } catch (error) {
      const apiError = error as ApiError;
      onUploadError(apiError.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [onUploadSuccess, onUploadError]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/csv': ['.csv']
    },
    maxFiles: 1,
    disabled: isUploading
  });

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Portfolio</h2>
        <p className="text-gray-600">
          Upload your portfolio CSV file to get started with analysis
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-primary-400 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {isUploading ? (
            <>
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-900">Uploading...</p>
                <div className="w-64 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500">{uploadProgress}% complete</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-gray-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Drop your CSV file here' : 'Drag & drop your CSV file here'}
                </p>
                <p className="text-gray-500 mt-1">or click to browse</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* File Rejections */}
      {fileRejections.length > 0 && (
        <div className="mt-4 p-4 bg-error-50 border border-error-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-error-800">File rejected</p>
              <p className="text-sm text-error-600 mt-1">
                Please upload a valid CSV file
              </p>
            </div>
          </div>
        </div>
      )}

      {/* CSV Format Requirements */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <FileText className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-blue-800 mb-2">CSV Format Requirements</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• First row should contain headers: <code className="bg-blue-100 px-1 rounded">ticker,position</code></p>
              <p>• Each row should contain a ticker symbol and position amount</p>
              <p>• Example: <code className="bg-blue-100 px-1 rounded">AAPL,10</code></p>
              <p>• Supported ticker formats: AAPL, BRK.B, etc.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sample CSV Download */}
      <div className="mt-6 text-center">
        <button
          onClick={() => {
            const csvContent = 'ticker,position\nAAPL,10\nGOOGL,5\nMSFT,8\nTSLA,2';
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sample_portfolio.csv';
            a.click();
            window.URL.revokeObjectURL(url);
          }}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium underline"
        >
          Download sample CSV file
        </button>
      </div>
    </div>
  );
};

export default PortfolioUpload;
