import React from "react";

export default function CitationCard({ citation }) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 6,
        padding: 8,
        marginTop: 8,
      }}
    >
      <strong>{citation.document_title}</strong> — p.{citation.page}
      {citation.section ? `, §${citation.section}` : ""}
      {citation.academic_year ? ` (${citation.academic_year})` : ""}
      {citation.url && (
        <div>
          <a href={citation.url} target="_blank" rel="noreferrer">
            Source
          </a>
        </div>
      )}
    </div>
  );
}
