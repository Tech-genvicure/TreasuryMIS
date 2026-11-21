
"use client";

import { useEffect, useMemo, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  AllCommunityModule,
  ModuleRegistry,
} from "ag-grid-community";
import {
  Plus,
  Trash2,
  RefreshCw,
  Download,
  Search,
  Wallet,
  FileText,
  Landmark,
  Receipt,
  Database,
  ChevronRight,
  Rows3,
  Pencil,
} from "lucide-react";

import api from "@/lib/api";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

ModuleRegistry.registerModules([AllCommunityModule]);

type SheetName =
  | "Funds Position"
  | "Payables"
  | "Borrowing"
  | "Receivables";

type RowData = Record<string, any>;

const endpointMap: Record<SheetName, string> = {
  "Funds Position": "/treasury/fund-positions",
  Payables: "/treasury/payables",
  Borrowing: "/treasury/borrowings",
  Receivables: "/treasury/receivables",
};

const sheets: {
  name: SheetName;
  icon: typeof Wallet;
  description: string;
}[] = [
  {
    name: "Funds Position",
    icon: Wallet,
    description: "Bank balances and investments",
  },
  {
    name: "Payables",
    icon: FileText,
    description: "Vendor payments and obligations",
  },
  {
    name: "Borrowing",
    icon: Landmark,
    description: "Borrowing facilities",
  },
  {
    name: "Receivables",
    icon: Receipt,
    description: "Expected receipts and income",
  },
];

function formatNumber(value: any): string {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(number);
}

const baseColumn = {
  sortable: true,
  filter: true,
  resizable: true,
  editable: true,
  minWidth: 120,
};

const amountColumn = (field: string, headerName: string, minWidth = 160) => ({
  field,
  headerName,
  minWidth,
  flex: 1,
  cellClass: "ag-right-aligned-cell",
  valueFormatter: (params: any) => formatNumber(params.value),
});

export default function Spreadsheet() {
  const [activeSheet, setActiveSheet] =
    useState<SheetName>("Funds Position");

  const [rowData, setRowData] = useState<RowData[]>([]);
  const [searchText, setSearchText] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedRowId, setSelectedRowId] =
    useState<number | null>(null);

  // LOAD DATA
  const loadData = async () => {
    setLoading(true);

    try {
      const response = await api.get(endpointMap[activeSheet]);
      setRowData(response.data || []);
      setSelectedRowId(null);
    } catch (error) {
      console.error("Failed to load spreadsheet data:", error);
      window.alert("Failed to load spreadsheet data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeSheet]);

  // ADD ROW
  const handleAddRow = async () => {
    setSaving(true);

    try {
      const response = await api.post(endpointMap[activeSheet], {});
      const newRow = response.data;

      setRowData((current) => [...current, newRow]);

      if (newRow?.id) {
        setSelectedRowId(Number(newRow.id));
      }
    } catch (error) {
      console.error("Failed to add row:", error);
      window.alert("Failed to add row.");
    } finally {
      setSaving(false);
    }
  };

  // DELETE ROW
  const handleDeleteRow = async () => {
    if (selectedRowId === null) {
      window.alert("Please select a row first.");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete the selected row?"
    );

    if (!confirmed) return;

    setSaving(true);

    try {
      await api.delete(
        `${endpointMap[activeSheet]}/${selectedRowId}`
      );

      setRowData((current) =>
        current.filter((row) => Number(row.id) !== selectedRowId)
      );

      setSelectedRowId(null);
    } catch (error) {
      console.error("Failed to delete row:", error);
      window.alert("Failed to delete row.");
    } finally {
      setSaving(false);
    }
  };

  // SAVE CELL CHANGES
  const handleCellChange = async (event: any) => {
    const rowId = event.data?.id;
    const field = event.colDef?.field;

    if (!rowId || !field) return;

    let value = event.newValue;

    if (value === "") value = null;

    try {
      await api.put(
        `${endpointMap[activeSheet]}/${rowId}`,
        { [field]: value }
      );
    } catch (error) {
      console.error("Failed to save cell:", error);
      window.alert("Failed to save this change.");
      await loadData();
    }
  };

  // COLUMN DEFINITIONS
  const columnDefs = useMemo(() => {
    if (activeSheet === "Funds Position") {
      return [
        {
          field: "company_name",
          headerName: "Company",
          minWidth: 230,
          flex: 1.5,
        },
        {
          field: "bank_name",
          headerName: "Bank / Investment",
          minWidth: 240,
          flex: 1.6,
        },
        {
          field: "account_no",
          headerName: "Account No.",
          minWidth: 170,
          flex: 1,
        },
        amountColumn("balance_inr", "Balance INR", 150),
        amountColumn("balance_usd", "Balance USD", 150),
        amountColumn("inr_equivalent", "INR Equivalent", 160),
        {
          field: "entity_type",
          headerName: "Type",
          minWidth: 130,
          flex: 0.8,
        },
      ];
    }

    if (activeSheet === "Payables") {
      return [
        {
          field: "tracker_serial_no",
          headerName: "Sr. No.",
          minWidth: 100,
          width: 110,
        },
        {
          field: "cost_for_project",
          headerName: "Cost for Project",
          minWidth: 160,
          flex: 1,
        },
        {
          field: "payment_processed",
          headerName: "Payment Processed",
          minWidth: 150,
          flex: 1,
        },
        {
          field: "payment_cycle",
          headerName: "Payment Cycle",
          minWidth: 140,
          flex: 1,
        },
        {
          field: "payer_company",
          headerName: "Payer Company",
          minWidth: 180,
          flex: 1.2,
        },
        {
          field: "branch",
          headerName: "Branch",
          minWidth: 120,
          flex: 0.8,
        },
        {
          field: "approved_in_vendor_management",
          headerName: "Approved in Vendor Management",
          minWidth: 190,
          flex: 1.3,
        },
        {
          field: "approval_date",
          headerName: "Approval Date",
          minWidth: 130,
          flex: 1,
        },
        {
          field: "vendor_name_expense_name",
          headerName: "Vendor / Expense",
          minWidth: 210,
          flex: 1.5,
        },
        {
          field: "product_service",
          headerName: "Product / Service",
          minWidth: 190,
          flex: 1.3,
        },
        {
          field: "pass_through_bill",
          headerName: "Pass Through Bill",
          minWidth: 150,
          flex: 1,
        },
        {
          field: "invoice_ref",
          headerName: "Invoice Ref.",
          minWidth: 150,
          flex: 1,
        },
        {
          field: "invoice_date",
          headerName: "Invoice Date",
          minWidth: 130,
          flex: 1,
        },
        {
          field: "due_date",
          headerName: "Due Date",
          minWidth: 130,
          flex: 1,
        },
        {
          field: "transaction_posting_date",
          headerName: "Transaction Posting Date",
          minWidth: 180,
          flex: 1.2,
        },
        amountColumn("amount_payable", "Amount Payable"),
        {
          field: "due_date_2",
          headerName: "Due Date 2",
          minWidth: 130,
          flex: 1,
        },
        {
          field: "payment_status",
          headerName: "Payment Status",
          minWidth: 150,
          flex: 1,
        },
        {
          field: "bank_account_number",
          headerName: "Bank Account",
          minWidth: 170,
          flex: 1,
        },
        {
          field: "ifsc_code",
          headerName: "IFSC",
          minWidth: 130,
          flex: 1,
        },
        {
          field: "bank_branch",
          headerName: "Bank Branch",
          minWidth: 160,
          flex: 1,
        },
        {
          field: "remarks",
          headerName: "Remarks",
          minWidth: 200,
          flex: 1.4,
        },
        {
          field: "timeline_bucket",
          headerName: "Timeline",
          minWidth: 150,
          flex: 1,
          editable: true,
          cellEditor: "agSelectCellEditor",
          cellEditorParams: {
            values: ["0-7 days", "8-15 days", "16-30 days"],
          },
        },
      ];
    }

    if (activeSheet === "Borrowing") {
      return [
        amountColumn("sanctioned", "Sanctioned", 180),
        amountColumn("disbursed", "Disbursed", 180),
        amountColumn("outstanding", "Outstanding", 180),
        {
          field: "updated_at",
          headerName: "Last Updated",
          minWidth: 180,
          flex: 1,
          editable: false,
        },
      ];
    }

    return [
      {
        field: "cost_for_project",
        headerName: "Cost for Project",
        minWidth: 160,
        flex: 1,
      },
      {
        field: "payment_processed",
        headerName: "Payment Processed",
        minWidth: 150,
        flex: 1,
      },
      {
        field: "receipt_cycle",
        headerName: "Receipt Cycle",
        minWidth: 140,
        flex: 1,
      },
      {
        field: "receiver_company",
        headerName: "Receiver Company",
        minWidth: 180,
        flex: 1.2,
      },
      {
        field: "branch",
        headerName: "Branch",
        minWidth: 120,
        flex: 0.8,
      },
      {
        field: "approved_in_vendor_management",
        headerName: "Approved in Vendor Management",
        minWidth: 190,
        flex: 1.3,
      },
      {
        field: "approval_date",
        headerName: "Approval Date",
        minWidth: 130,
        flex: 1,
      },
      {
        field: "vendor_name_income_name",
        headerName: "Vendor / Income",
        minWidth: 210,
        flex: 1.5,
      },
      {
        field: "product_service",
        headerName: "Product / Service",
        minWidth: 190,
        flex: 1.3,
      },
      {
        field: "pass_through_bill",
        headerName: "Pass Through Bill",
        minWidth: 150,
        flex: 1,
      },
      {
        field: "invoice_ref",
        headerName: "Invoice Ref.",
        minWidth: 150,
        flex: 1,
      },
      {
        field: "invoice_date",
        headerName: "Invoice Date",
        minWidth: 130,
        flex: 1,
      },
      {
        field: "due_date",
        headerName: "Due Date",
        minWidth: 130,
        flex: 1,
      },
      {
        field: "transaction_posting_date",
        headerName: "Transaction Posting Date",
        minWidth: 180,
        flex: 1.2,
      },
      amountColumn("amount_receivable", "Amount Receivable", 170),
      {
        field: "due_date_2",
        headerName: "Due Date 2",
        minWidth: 130,
        flex: 1,
      },
      {
        field: "payment_status",
        headerName: "Payment Status",
        minWidth: 150,
        flex: 1,
      },
      {
        field: "bank_account_number",
        headerName: "Bank Account",
        minWidth: 170,
        flex: 1,
      },
      {
        field: "ifsc_code",
        headerName: "IFSC",
        minWidth: 130,
        flex: 1,
      },
      {
        field: "bank_branch",
        headerName: "Bank Branch",
        minWidth: 160,
        flex: 1,
      },
      {
        field: "remarks",
        headerName: "Remarks",
        minWidth: 200,
        flex: 1.4,
      },
      {
        field: "timeline_bucket",
        headerName: "Timeline",
        minWidth: 130,
        flex: 1,
      },
    ];
  }, [activeSheet]);

  // SEARCH
  const filteredRows = useMemo(() => {
    const search = searchText.trim().toLowerCase();

    if (!search) return rowData;

    return rowData.filter((row) =>
      Object.values(row).some((value) =>
        String(value ?? "").toLowerCase().includes(search)
      )
    );
  }, [rowData, searchText]);

  // EXCEL DOWNLOAD
  const handleDownload = async () => {
    try {
      const response = await api.get(
        "/treasury/export/excel",
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "Genvicure_Treasury_Master.xlsx";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Excel download failed:", error);
      window.alert("Excel download failed.");
    }
  };

  const activeSheetInfo = sheets.find(
    (sheet) => sheet.name === activeSheet
  );

  const ActiveIcon = activeSheetInfo?.icon || Database;

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-[#F6F4EF] p-5 lg:p-6">

      {/* PAGE HEADER */}
      <header className="mb-5 flex shrink-0 flex-wrap items-center justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <span className="h-[2px] w-6 bg-[#C4A66A]" />
            <p className="text-[10px] font-semibold uppercase tracking-[2px] text-[#A88950]">
              Treasury management
            </p>
          </div>

          <h1 className="text-[30px] font-semibold tracking-[-1px] text-[#14263D]">
            Financial Records
          </h1>

          <p className="mt-1 text-[12px] text-[#8290A0]">
            Manage, review and maintain your treasury data
          </p>
        </div>

        <div className="flex items-center gap-3 rounded-xl border border-[#E8E5DE] bg-white px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#F1EBDD] text-[#A88950]">
            <Database size={18} />
          </div>
          <div>
            <p className="text-[10px] text-[#8290A0]">
              Current records
            </p>
            <p className="text-[17px] font-semibold tabular-nums text-[#14263D]">
              {rowData.length.toLocaleString("en-IN")}
            </p>
          </div>
        </div>
      </header>

      {/* SHEET NAVIGATION */}
      <div className="mb-4 grid shrink-0 grid-cols-2 gap-3 xl:grid-cols-4">
        {sheets.map((sheet) => {
          const Icon = sheet.icon;
          const active = activeSheet === sheet.name;

          return (
            <button
              key={sheet.name}
              type="button"
              onClick={() => {
                setActiveSheet(sheet.name);
                setSearchText("");
              }}
              className={`flex min-w-0 items-center gap-3 rounded-xl border px-4 py-3 text-left transition duration-200 ${
                active
                  ? "border-[#C4A66A] bg-[#14263D] text-white shadow-[0_5px_15px_rgba(20,38,61,0.10)]"
                  : "border-[#E8E5DE] bg-white text-[#526174] hover:border-[#C4A66A]/70 hover:bg-[#FBFAF7]"
              }`}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
                  active
                    ? "bg-white/10 text-[#D8BD88]"
                    : "bg-[#F1EBDD] text-[#A88950]"
                }`}
              >
                <Icon size={19} />
              </div>

              <div className="min-w-0 flex-1">
                <p className={`truncate text-[13px] font-semibold ${
                  active ? "text-white" : "text-[#243A52]"
                }`}>
                  {sheet.name}
                </p>
                <p className={`mt-0.5 truncate text-[10px] ${
                  active ? "text-white/55" : "text-[#98A1AC]"
                }`}>
                  {sheet.description}
                </p>
              </div>

              {active && (
                <ChevronRight
                  size={16}
                  className="shrink-0 text-[#D8BD88]"
                />
              )}
            </button>
          );
        })}
      </div>

      {/* GRID PANEL */}
      <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-[#E8E5DE] bg-white shadow-[0_3px_12px_rgba(20,38,61,0.035)]">

        {/* PANEL HEADER */}
        <div className="flex shrink-0 flex-wrap items-center justify-between gap-4 border-b border-[#EEECE6] px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F1EBDD] text-[#A88950]">
              <ActiveIcon size={19} />
            </div>

            <div>
              <h2 className="text-[15px] font-semibold text-[#14263D]">
                {activeSheet}
              </h2>
              <p className="mt-0.5 text-[10px] text-[#8290A0]">
                {activeSheetInfo?.description}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">

            {/* SEARCH */}
            <div className="relative">
              <Search
                size={15}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#98A1AC]"
              />
              <input
                type="text"
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
                placeholder="Search records..."
                className="h-9 w-[190px] rounded-lg border border-[#E8E5DE] bg-[#FAF9F6] pl-9 pr-3 text-[11px] text-[#243A52] outline-none transition placeholder:text-[#A5ADB6] focus:border-[#C4A66A] focus:bg-white"
              />
            </div>

            {/* REFRESH */}
            <button
              type="button"
              onClick={loadData}
              disabled={loading}
              className="flex h-9 items-center gap-2 rounded-lg border border-[#E8E5DE] bg-white px-3 text-[11px] font-medium text-[#526174] transition hover:border-[#C4A66A] hover:text-[#A88950] disabled:opacity-50"
            >
              <RefreshCw
                size={14}
                className={loading ? "animate-spin" : ""}
              />
              Refresh
            </button>

            {/* ADD ROW */}
            <button
              type="button"
              onClick={handleAddRow}
              disabled={saving}
              className="flex h-9 items-center gap-2 rounded-lg bg-[#14263D] px-3.5 text-[11px] font-semibold text-white transition hover:bg-[#243A52] disabled:opacity-50"
            >
              <Plus size={15} />
              Add Row
            </button>

            {/* DELETE ROW */}
            <button
              type="button"
              onClick={handleDeleteRow}
              disabled={saving || selectedRowId === null}
              className="flex h-9 items-center gap-2 rounded-lg border border-[#E9D9D5] bg-[#FBF5F3] px-3 text-[11px] font-medium text-[#A85E55] transition hover:bg-[#F7EAE7] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Trash2 size={14} />
              Delete
            </button>

            {/* DOWNLOAD */}
            <button
              type="button"
              onClick={handleDownload}
              className="flex h-9 items-center gap-2 rounded-lg border border-[#D9E5DF] bg-[#F2F7F3] px-3 text-[11px] font-semibold text-[#237A62] transition hover:bg-[#E8F2EB]"
            >
              <Download size={14} />
              Export Excel
            </button>
          </div>
        </div>

        {/* GRID INFORMATION BAR */}
        <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-[#EEECE6] bg-[#FAF9F6] px-5 py-2.5">
          <div className="flex items-center gap-2">
            <Rows3 size={13} className="text-[#A88950]" />
            <span className="text-[10px] text-[#718092]">
              Showing{" "}
              <strong className="font-semibold text-[#243A52]">
                {filteredRows.length}
              </strong>{" "}
              of{" "}
              <strong className="font-semibold text-[#243A52]">
                {rowData.length}
              </strong>{" "}
              records
            </span>
          </div>

          <div className="flex items-center gap-2 text-[10px] text-[#98A1AC]">
            <Pencil size={12} />
            Select a cell to edit its value
          </div>
        </div>

        {/* AG GRID */}
        <div className="ag-theme-quartz treasury-grid min-h-0 flex-1 w-full">
          <AgGridReact
            theme="legacy"
            rowData={filteredRows}
            columnDefs={columnDefs}
            defaultColDef={baseColumn}
            getRowId={(params) => String(params.data.id)}
            onRowClicked={(event) => {
              if (event.data?.id) {
                setSelectedRowId(Number(event.data.id));
              }
            }}
            onCellValueChanged={handleCellChange}
            pagination={false}
            stopEditingWhenCellsLoseFocus
            headerHeight={43}
            rowHeight={42}
            animateRows={true}
            suppressCellFocus={false}
            overlayLoadingTemplate={
              '<span class="ag-overlay-loading-center">Loading financial records...</span>'
            }
            loading={loading}
            rowSelection="single"
          />
        </div>

        {/* PANEL FOOTER */}
        <div className="flex shrink-0 items-center justify-between border-t border-[#EEECE6] bg-[#FAF9F6] px-5 py-2.5">
          <p className="text-[10px] text-[#98A1AC]">
            Genvicure Treasury MIS
          </p>
          <p className="text-[10px] text-[#98A1AC]">
            {selectedRowId !== null
              ? `Selected record ID: ${selectedRowId}`
              : "No record selected"}
          </p>
        </div>
      </section>
    </div>
  );
}
