export default function PriorityBadge({ level }) {
  const levelLower = (level || 'low').toLowerCase();

  return (
    <span className={`priority-badge ${levelLower}`}>
      {level || 'LOW'}
    </span>
  );
}
