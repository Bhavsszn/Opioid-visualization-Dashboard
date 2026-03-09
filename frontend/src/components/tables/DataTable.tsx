import { EmptyState } from "../ui/EmptyState";

export type DataColumn<T> = {
  key: keyof T;
  title: string;
  render?: (row: T) => string | number | null;
};

export function DataTable<T extends object>({
  columns,
  rows,
  rowKey,
}: {
  columns: DataColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string;
}) {
  if (!rows.length) {
    return <EmptyState title="No records" description="No rows were returned for this section." />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={String(col.key)}>{col.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((col) => (
                <td key={String(col.key)}>{col.render ? col.render(row) : String((row as Record<string, unknown>)[String(col.key)] ?? "-")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
