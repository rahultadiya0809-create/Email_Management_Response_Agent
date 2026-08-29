export default function CategoryTag({ category }) {
  const cat = (category || 'informational').toLowerCase();

  return (
    <span className={`category-tag ${cat}`}>
      {category || 'Informational'}
    </span>
  );
}
