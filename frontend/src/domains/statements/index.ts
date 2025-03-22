// frontend/src/domains/statements/index.ts

// Export public components and pages
export { StatementsPage } from './pages/StatementsPage';
export { StatementDetailPage } from './pages/StatementDetailPage';
export { GradeStatementPage } from './pages/GradeStatementPage';
export { GradingDashboardPage } from './pages/GradingDashboardPage';
export { CreateStatementPage } from './pages/CreateStatementPage';

// Export reusable components
export { StatementsList } from './components/StatementsList';
export { StatementDetail } from './components/StatementDetail';
export { GradingStatisticsCard } from './components/GradingStatisticsCard';

// Export types
export type {
  Statement,
  AreaOfLaw,
  GradingRubric,
  RubricCriterion,
  GradeImport,
  GradingStatistics,
  CreateStatementRequest,
  UpdateStatementRequest,
  GradeStatementRequest
} from './types';