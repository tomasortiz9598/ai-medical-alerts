import { useState } from 'react';
import type { ChangeEvent } from 'react';

type Props = {
  onSubmit: (file: File) => void;
  disabled?: boolean;
};

export function FileUpload({ onSubmit, disabled }: Props) {
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onSubmit(file);
    }
  };

  return (
    <div className="file-upload">
      <label className={`file-upload-label ${disabled ? 'disabled' : ''}`}>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          disabled={disabled}
        />
        <span>{fileName ?? 'Choose PDF...'}</span>
      </label>
      <p className="hint">File upload triggers immediate processing.</p>
    </div>
  );
}
