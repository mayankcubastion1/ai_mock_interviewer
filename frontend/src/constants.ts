import { FocusArea, WorkbookPlatform } from "./types";

export const FOCUS_AREAS: { value: FocusArea; label: string; description: string }[] = [
  {
    value: "advanced_formulas",
    label: "Advanced Formulas",
    description: "Array formulas, lookup strategies, dynamic functions"
  },
  {
    value: "data_analysis",
    label: "Data Analysis",
    description: "Pivot tables, Power Query, cleansing large datasets"
  },
  {
    value: "automation",
    label: "Automation",
    description: "VBA, Office Scripts, process automation"
  },
  {
    value: "dashboards",
    label: "Dashboards",
    description: "Executive dashboards, data visualization, storytelling"
  },
  {
    value: "data_modeling",
    label: "Data Modeling",
    description: "Power Pivot, relationships, scenario modeling"
  }
];

export const WORKBOOK_PLATFORMS: { value: WorkbookPlatform; label: string; description: string }[] = [
  {
    value: "microsoft_excel",
    label: "Microsoft Excel",
    description: "Desktop or web Excel with Power Query, PivotTables, and VBA"
  },
  {
    value: "google_sheets",
    label: "Google Sheets",
    description: "Browser-based collaboration, ARRAYFORMULA, and Connected Sheets"
  }
];
