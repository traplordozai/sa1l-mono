import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogClose
} from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Badge } from '../../../components/ui/badge';
import {
  Alert,
  AlertTitle,
  AlertDescription
} from '../../../components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '../../../components/ui/table';
import { ImportLog, ImportDetail } from '../types';
import { getImportDetails } from '../services/importApi';
import { useQuery } from '@tanstack/react-query';
import { formatDate } from '../../../utils/formatters';

interface ImportDetailsDialogProps {
  importLog: ImportLog;
  open: boolean;
  onClose: () => void;
}

const ImportDetailsDialog: React.FC<ImportDetailsDialogProps> = ({
  importLog,
  open,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<string>('summary');

  // Reset active tab when dialog opens
  useEffect(() => {
    if (open) {
      setActiveTab('summary');
    }
  }, [open]);

  // Fetch import details
  const {
    data: details,
    isLoading,
    isError
  } = useQuery({
    queryKey: ['importDetails', importLog.id],
    queryFn: () => getImportDetails(importLog.id),
    enabled: open,
  });

  // Filter details by status for the different tabs
  const successDetails = details?.filter(detail => detail.status === 'success') || [];
  const errorDetails = details?.filter(detail => detail.status === 'error') || [];
  const warningDetails = details?.filter(detail => detail.status === 'warning') || [];

  const renderErrorsList = () => {
    if (!importLog.errors || Object.keys(importLog.errors).length === 0) {
      return (
        <p className="text-gray-500 italic">No errors reported</p>
      );
    }

    return (
      <div className="space-y-4">
        {Object.entries(importLog.errors).map(([key, errors]) => (
          <div key={key} className="space-y-2">
            <h4 className="font-medium">{key}</h4>
            <ul className="list-disc list-inside space-y-1">
              {Array.isArray(errors) ? (
                errors.map((error, index) => (
                  <li key={index} className="text-red-600">
                    {error}
                  </li>
                ))
              ) : (
                <li className="text-red-600">{String(errors)}</li>
              )}
            </ul>
          </div>
        ))}
      </div>
    );
  };

  const renderDetailsTable = (detailsList: ImportDetail[]) => {
    if (detailsList.length === 0) {
      return (
        <p className="text-gray-500 italic">No records found</p>
      );
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Row</TableHead>
            <TableHead>Entity Type</TableHead>
            <TableHead>Entity ID</TableHead>
            <TableHead>Message</TableHead>
            <TableHead>Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {detailsList.map((detail) => (
            <TableRow key={detail.id}>
              <TableCell>{detail.row_number || '-'}</TableCell>
              <TableCell>{detail.entity_type}</TableCell>
              <TableCell>{detail.entity_id || '-'}</TableCell>
              <TableCell className="max-w-md truncate">{detail.message}</TableCell>
              <TableCell>{formatDate(detail.created_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import Details</DialogTitle>
          <DialogDescription>
            Detailed information about the import process
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 w-full">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="success">
              Success ({successDetails.length})
            </TabsTrigger>
            <TabsTrigger value="errors">
              Errors ({errorDetails.length})
            </TabsTrigger>
            <TabsTrigger value="warnings">
              Warnings ({warningDetails.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="summary" className="mt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-bold">Import Information</h3>
                  <div className="mt-2 space-y-2">
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">File Name:</span>
                      <span className="font-medium">{importLog.original_file_name}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Type:</span>
                      <span className="font-medium">{importLog.import_type_display}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Status:</span>
                      <Badge
                        variant={
                          importLog.status === 'completed' ? 'success' :
                          importLog.status === 'failed' ? 'destructive' :
                          importLog.status === 'processing' ? 'info' :
                          'warning'
                        }
                      >
                        {importLog.status_display}
                      </Badge>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Created:</span>
                      <span className="font-medium">{formatDate(importLog.created_at)}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Started:</span>
                      <span className="font-medium">
                        {importLog.started_at ? formatDate(importLog.started_at) : '-'}
                      </span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Completed:</span>
                      <span className="font-medium">
                        {importLog.completed_at ? formatDate(importLog.completed_at) : '-'}
                      </span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Duration:</span>
                      <span className="font-medium">{importLog.duration || '-'}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Imported By:</span>
                      <span className="font-medium">{importLog.imported_by_name || 'System'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-bold">Results</h3>
                  <div className="mt-2 space-y-2">
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Records Processed:</span>
                      <span className="font-medium">{importLog.processed_count}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Success:</span>
                      <span className="font-medium text-green-600">{importLog.success_count}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Errors:</span>
                      <span className="font-medium text-red-600">{importLog.error_count}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Warnings:</span>
                      <span className="font-medium text-yellow-600">{importLog.warnings_count}</span>
                    </div>
                    <div className="flex justify-between border-b pb-1">
                      <span className="text-gray-500">Success Rate:</span>
                      <span className="font-medium">
                        {importLog.success_rate ? `${importLog.success_rate}%` : '-'}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-base font-bold">Errors</h3>
                  <div className="mt-2 max-h-72 overflow-y-auto">
                    {renderErrorsList()}
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="success" className="mt-6">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : isError ? (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>Failed to load import details.</AlertDescription>
              </Alert>
            ) : (
              <div className="border rounded-md overflow-hidden">
                {renderDetailsTable(successDetails)}
              </div>
            )}
          </TabsContent>

          <TabsContent value="errors" className="mt-6">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : isError ? (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>Failed to load import details.</AlertDescription>
              </Alert>
            ) : (
              <div className="border rounded-md overflow-hidden">
                {renderDetailsTable(errorDetails)}
              </div>
            )}
          </TabsContent>

          <TabsContent value="warnings" className="mt-6">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : isError ? (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>Failed to load import details.</AlertDescription>
              </Alert>
            ) : (
              <div className="border rounded-md overflow-hidden">
                {renderDetailsTable(warningDetails)}
              </div>
            )}
          </TabsContent>
        </Tabs>

        <DialogClose asChild>
          <Button className="mt-4">Close</Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
};

export default ImportDetailsDialog;