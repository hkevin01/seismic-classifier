import { AlertCircle, CheckCircle, File, Upload, X } from 'lucide-react'
import React from 'react'
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '../../store/appStore'
import { Button } from '../ui/Button'
import { Modal } from '../ui/Modal'

interface FileUploadModalProps {
  isOpen: boolean
  onClose: () => void
}

export function FileUploadModal({ isOpen, onClose }: FileUploadModalProps) {
  const { addNotification } = useAppStore()
  const [uploadedFiles, setUploadedFiles] = React.useState<Array<{
    name: string
    size: number
    status: 'uploading' | 'success' | 'error'
    progress: number
  }>>([])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/octet-stream': ['.sac', '.mseed'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'text/plain': ['.txt']
    },
    onDrop: (acceptedFiles) => {
      acceptedFiles.forEach(file => {
        const newFile = {
          name: file.name,
          size: file.size,
          status: 'uploading' as const,
          progress: 0
        }

        setUploadedFiles(prev => [...prev, newFile])

        // Simulate file upload
        const interval = setInterval(() => {
          setUploadedFiles(prev => prev.map(f =>
            f.name === file.name
              ? { ...f, progress: Math.min(f.progress + 10, 100) }
              : f
          ))
        }, 200)

        setTimeout(() => {
          clearInterval(interval)
          setUploadedFiles(prev => prev.map(f =>
            f.name === file.name
              ? { ...f, status: Math.random() > 0.2 ? 'success' : 'error', progress: 100 }
              : f
          ))

          if (Math.random() > 0.2) {
            addNotification({
              type: 'success',
              title: 'File Upload Complete',
              message: `${file.name} has been processed successfully`
            })
          } else {
            addNotification({
              type: 'error',
              title: 'File Upload Failed',
              message: `Failed to process ${file.name}`
            })
          }
        }, 2000)
      })
    }
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const removeFile = (fileName: string) => {
    setUploadedFiles(prev => prev.filter(f => f.name !== fileName))
  }

  const clearAll = () => {
    setUploadedFiles([])
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Upload Seismic Data" className="max-w-lg">
      <div className="space-y-4">
        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary/50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />

          {isDragActive ? (
            <p className="text-primary">Drop files here...</p>
          ) : (
            <div>
              <p className="text-foreground font-medium mb-2">
                Drop seismic data files here, or click to browse
              </p>
              <p className="text-sm text-muted-foreground">
                Supports .sac, .mseed, .csv, .json, .txt files
              </p>
            </div>
          )}
        </div>

        {/* File List */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Uploaded Files ({uploadedFiles.length})</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={clearAll}
              >
                Clear All
              </Button>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {uploadedFiles.map((file, index) => (
                <div key={`${file.name}-${index}`} className="flex items-center space-x-3 p-3 rounded-lg bg-secondary/30 border border-border/50">
                  <File className="w-4 h-4 text-muted-foreground flex-shrink-0" />

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)}
                    </p>

                    {file.status === 'uploading' && (
                      <div className="mt-1">
                        <div className="w-full bg-muted rounded-full h-1.5">
                          <div
                            className="bg-primary h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {file.status === 'success' && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                    {file.status === 'error' && (
                      <AlertCircle className="w-4 h-4 text-red-500" />
                    )}

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(file.name)}
                      className="flex-shrink-0"
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info */}
        <div className="text-xs text-muted-foreground p-3 rounded-lg bg-muted/30">
          <p className="font-medium mb-1">Supported formats:</p>
          <ul className="space-y-1">
            <li>• SAC files (.sac) - Standard seismic data format</li>
            <li>• MiniSEED files (.mseed) - Compressed seismic data</li>
            <li>• CSV files (.csv) - Tabular data with timestamps</li>
            <li>• JSON files (.json) - Structured event data</li>
          </ul>
        </div>
      </div>
    </Modal>
  )
}
