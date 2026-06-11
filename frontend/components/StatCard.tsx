interface StatCardProps {
  label: string;
  value: string;
  hint?: string;
}

export default function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <div className="md-card md-card-interactive p-5">
      <p className="text-label-md uppercase tracking-wide text-on-surface-variant">
        {label}
      </p>
      <p className="mt-2 text-headline-sm text-on-surface">{value}</p>
      {hint && <p className="mt-1 text-body-sm text-on-surface-variant">{hint}</p>}
    </div>
  );
}
