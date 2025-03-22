import React, { useState } from 'react';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../../../components/ui/table';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import {
  ArrowPathIcon,
  ArrowDownTrayIcon,
  ChevronDownIcon,
  DocumentTextIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '../../../components/ui/dropdown-menu';
import { ImportLog, ImportStatus } from '../types';
import { formatDate, formatDuration } from '../../../utils/formatters';
import ImportDetailsDialog from './ImportDetailsDialog';

interface ImportHistoryTableProps {
  importLogs: ImportLog[];
  onRefresh: () => void;
}

const ImportHistoryTable: React.FC<ImportHistoryTableProps> = ({ importLogs, onRefresh }) => {
  const [selectedImportLog, setSelectedImportLog] = useState<ImportLog | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case ImportStatus.COMPLETED:
        return <Badge variant="success">Completed</Badge>;
      case ImportStatus.PROCESSING:
        return <Badge variant="info">Processing</Badge>;
      case ImportStatus.PENDING:
        return <Badge variant="warning">Pending</Badge>;
      case ImportStatus.FAILED:
        return <Badge variant="destructive">Failed</Badge>;
      case ImportStatus.PARTIALLY_COMPLETED:
        return <Badge variant="warning">Partially Completed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getImportTypeName = (importType: string) => {
    switch (importType) {
      case 'student_csv':
        return 'Student CSV';
      case 'organization_csv':
        return 'Organization CSV';
      case 'grades_pdf':
        return 'Grades PDF';
      case 'statement_csv':
        return 'Statement CSV';
      default:
        return importType;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case ImportStatus.COMPLETED:
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case ImportStatus.PROCESSING:
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case ImportStatus.PENDING:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case ImportStatus.FAILED:
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      case ImportStatus.PARTIALLY_COMPLETED:
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const handleViewDetails = (importLog: ImportLog) => {
    setSelectedImportLog(importLog);
    setShowDetails(true);
  };

  return (
    <div>
      <div className="flex justify-end mb-4">
        <Button variant="outline" onClick={onRefresh} className="flex items-center gap-2">
          <ArrowPathIcon className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50px]">Status</TableHead>
              <TableHead>File Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Results</TableHead>
              <TableHead className="text-right">Duration</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {importLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-6 text-gray-500">
                  No import history found
                </TableCell>
              </TableRow>
            ) : (
              importLogs.map((importLog) => (
                <TableRow key={importLog.id}>
                  <TableCell>
                    <div className="flex items-center">
                      {getStatusIcon(importLog.status)}
                    </div>
                  </TableCell>
                  <TableCell className="font-medium">
                    {importLog.original_file_name}
                  </TableCell>
                  <TableCell>{getImportTypeName(importLog.import_type)}</TableCell>
                  <TableCell>{formatDate(importLog.created_at)}</TableCell>
                  <TableCell className="text-right">
                    {importLog.processed_count > 0 ? (
                      <div>
                        <span className="text-green-600 font-medium">{importLog.success_count}</span>
                        {' / '}
                        <span>{importLog.processed_count}</span>
                        {importLog.error_count > 0 && (
                          <span className="text-red-600 ml-2">
                            ({importLog.error_count} errors)
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-500">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    {importLog.duration || '-'}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <span className="sr-only">Open menu</span>
                          <ChevronDownIcon className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleViewDetails(importLog)}>
                          View Details
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {selectedImportLog && (
        <ImportDetailsDialog
          importLog={selectedImportLog}
          open={showDetails}
          onClose={() => setShowDetails(false)}
        />
      )}
    </div>
  );
};

export default ImportHistoryTable;